# -*- coding: utf-8 -*-
#!/usr/bin/env/ python3


import os
import sys
import pythoncyc
import argparse
import subprocess
from pythoncyc import PTools as PTools
from pythoncyc.PTools import PToolsError as PToolsError
from pythoncyc.PTools import PythonCycError as PythonCycError

#Usage : python3 dev_pythoncyc.py -p META


def close_pgdb_wosaving(pgdb):
    try:
        r = PTools.sendQueryToPTools('(close-kb :kb (kb-of-organism "'+pgdb._orgid+'") :save-updates-p nil)')
    except PToolsError as msg:
        raise PythonCycError('Pathway Tools was unable to close KB of organism (orgid) {orgid}. More specifically:  {msg}'.format(orgid=pgdb._orgid, msg=msg))
    return(r)


def get_genes_of_reaction(rxn, pgdb):
    genes = set()
    for gene in pgdb.genes_of_reaction(rxn):
        genes.add(gene)
    for enz in pgdb.enzymes_of_reaction(rxn):
        for gene in pgdb.genes_of_protein(enz):
            genes.add(gene)
    return(genes)


def write_pathway(pgdb):
    with open("metacyc_pathways.tsv", "w") as pathways:
        with open("metacyc_reactions_by_pathway.tsv", "w") as reactions:
            header1="Pathway_Id\tCommon_name\n"
            pathways.write(header1)
            header2="Pathway_Id\tReaction_Id\tSpontaneous\tOrphan\tOrphan_in_Metacyc\n"
            reactions.write(header2)
            for path in pgdb.all_pathways(selector='all', base=True):
                to_write=path.split("|")[1]+"\t"+pgdb[path].common_name+"\n"
                pathways.write(to_write)
                for rxn in pgdb[path].reaction_list:
                    orphan_in_metacyc = "FALSE"
                    orphan = "NA"
                    spontaneous = "FALSE"
                    if pgdb[rxn].spontaneous_p != None and pgdb[rxn].spontaneous_p == True:
                        spontaneous = "TRUE"
                    if len(get_genes_of_reaction(rxn, pgdb)) == 0 and spontaneous == "FALSE":
                        orphan_in_metacyc = "TRUE"
                    if pgdb[rxn].orphan_p != None:
                        if pgdb[rxn].orphan_p[0] == "|NO|":
                            orphan = "FALSE"
                        else:
                            orphan = "TRUE"
                    to_write_r = path.split("|")[1]+"\t"+rxn.split("|")[1]+"\t"+spontaneous+"\t"+orphan+"\t"+orphan_in_metacyc+"\n"
                    reactions.write(to_write_r)

def get_pathways_none_spontaneous_reactions(pgdb):
    pathways = dict()
    for path in pgdb.all_pathways(selector='all', base=True):
        pathways[path] = dict()
        pathways[path]['Name'] = pgdb[path].common_name
        pathways[path]['Reactions'] = set()
        for rxn in pgdb[path].reaction_list:
            if pgdb[rxn].spontaneous_p != None:
                 if pgdb[rxn].spontaneous_p != True:
                     pathways[path]['Reactions'].add(rxn)
            else:
                pathways[path]['Reactions'].add(rxn)
    return(pathways)
  
def get_pathways_none_spontaneous_orphan_reactions(pgdb):
    pathways = dict()
    for path in pgdb.all_pathways(selector='all', base=True):
        pathways[path] = dict()
        pathways[path]['Name'] = pgdb[path].common_name
        pathways[path]['Reactions'] = set()
        for rxn in pgdb[path].reaction_list:
            is_spontaneous = False
            is_orphan = None
            is_orphan_in_metacyc = False
            
            if pgdb[rxn].spontaneous_p != None and pgdb[rxn].spontaneous_p == True:
                is_spontaneous = True
                
            if is_spontaneous == False:
                if len(get_genes_of_reaction(rxn, pgdb)) == 0:
                    is_orphan_in_metacyc = True
                
                if pgdb[rxn].orphan_p != None and pgdb[rxn].orphan_p[0] == "|NO|":
                    is_orphan = False
                else:
                    is_orphan = True
                    
            if not(is_orphan_in_metacyc and (is_orphan == None or is_orphan)) and not is_spontaneous:
                pathways[path]['Reactions'].add(rxn)
                
    return(pathways)                  

def get_reactions_with_genes(pgdb):
    reactions = set()
    for rxn in pgdb.all_rxns(type_of_reactions = ':all'):
        if len(get_genes_of_reaction(rxn, pgdb)) != 0:
            reactions.add(rxn)
    return(reactions)


def get_pathways(pgdb):
    pathways = set()
    for path in pgdb.all_pathways(selector='all', base=True):
        pathways.add(path)
    return(pathways)
    

def write_pgdb_pathway_completion(pgdb, pgdb_name, use_orphan, completion_dict, position):
    print(completion_dict)
    if use_orphan:
        meta_pathways = get_pathways_none_spontaneous_reactions(pgdb)
        file_name = pgdb_name+"_pathway_completion.tsv"
    else:
        meta_pathways = get_pathways_none_spontaneous_orphan_reactions(pgdb)
        file_name = pgdb_name+"_pathway_completion_wo_orphan.tsv"
        
    pgdb_reactions = get_reactions_with_genes(pgdb)
    pgdb_pathways = get_pathways(pgdb)
  
    with open(file_name, "w") as pgdb_write:
        header="PGDB\tPathway\tPathway_name\tIs_predicted\tCompletion\n"
        pgdb_write.write(header)
        for path in meta_pathways:
            path_predicted = path in pgdb_pathways
            if len(meta_pathways[path]['Reactions']) == 0:
                completion = 0.0
            else:
                completion = len(meta_pathways[path]['Reactions'].intersection(pgdb_reactions))/len(meta_pathways[path]['Reactions'])
            to_write=pgdb_name+"\t"+path.split("|")[1]+"\t"+meta_pathways[path]['Name']+"\t"+str(path_predicted)+"\t"+str(completion)+"\n"
            pgdb_write.write(to_write)
            completion_dict[pgdb[path].common_name][position] = (str(completion))
        return(completion_dict)
 
 
 
def write_completion_matrix(completion_dict, file_name, header):
    with open(file_name, "w") as matrix_file:
        matrix_file.write(header)
        for pathway in completion_dict:
            values_to_write = "\t".join(completion_dict[pathway])
            to_write = pathway+"\t"+values_to_write+"\n"
            matrix_file.write(to_write)
        
  
def init_completion_dict(pgdb_list, completion_dict, completion_dict_wo_orphan):
    for p in pgdb_list:
        name = p.strip()
        pgdb_name = '|'+name+'|'
        pgdb = pythoncyc.select_organism(pgdb_name)
        pgdb_pathways = get_pathways(pgdb)
        for path in pgdb_pathways:
            path_name = pgdb[path].common_name
            if path_name not in completion_dict.keys():
                completion_dict[path_name] = ["0.0"] * len(pgdb_list) 
                completion_dict_wo_orphan[path_name] = ["0.0"] * len(pgdb_list)
    return(completion_dict, completion_dict_wo_orphan)
  
                    
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-p", help="Enter the name of the PGDB (example : META)", required=False, type=str)
    parser.add_argument("-l", help="Enter file with list of PGDB ", required=False, type=str)
    parser.add_argument("-m", help="Argument for missing value : O or NA - 0 by default", required=False, type=str)
    args = parser.parse_args()
    ## write completion in separate files
    header = "#NAMES"
    completion_dict = dict()
    completion_dict_wo_orphan = dict()
    with open(args.l) as pgdb_file:
        pgdb_list = [line.strip() for line in pgdb_file]
    (completion_dict, completion_dict_wo_orphan) = init_completion_dict(pgdb_list, completion_dict, completion_dict_wo_orphan)
    if args.l:
        for (name, position) in zip(pgdb_list, range(len(pgdb_list))):
            name = name.strip()
            print(name)
            header = header +"\t"+name
            print(header)
            pgdb_name = '|'+name+'|'
            print(pgdb_name)
            pgdb = pythoncyc.select_organism(pgdb_name)
            print(pgdb)
            #write_reactions_kegg_cross_ref(pgdb)
            write_pathway(pgdb)
            completion_dict = write_pgdb_pathway_completion(pgdb, name,  True, completion_dict, position)
            completion_dict_wo_orphan = write_pgdb_pathway_completion(pgdb, name , False, completion_dict_wo_orphan, position)
            #print(pgdb._orgid)
            #close_pgdb_wosaving(pgdb)   
    elif args.p:
        pgdb_name = '|'+args.p+'|'
        pgdb = pythoncyc.select_organism(pgdb_name)
        write_pathway(pgdb)
        write_pgdb_pathway_completion(pgdb, meta, args.p, True)
        write_pgdb_pathway_completion(pgdb, meta, args.p, False)
    else:
        sys.exit("Please select an option!")
    header = header+"\n"
    write_completion_matrix(completion_dict, "completion_matrix.txt", header)
    write_completion_matrix(completion_dict_wo_orphan, "completion_matrix_wo_orphan.tsv", header)

if __name__ == "__main__":
    main()
