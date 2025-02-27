# -*- coding: utf-8 -*-
#!/usr/bin/env/ python3

import argparse


#usage : python3 create_pf_file.py -m MR_file -k KO_file -o output name and path -f input file name and path

def create_pf_entry(ID, ko_dict, mr_dict, kofam_dict, product_dict):
    to_add_EC = set()
    to_add_metacyc = set()
    to_add_function = set()
    for i in kofam_dict[ID]:
        to_add_EC.add("EC    "+i[1])
        if i[0] in mr_dict.keys():
            to_add_metacyc.add("METACYC\t"+ ko_dict[mr_dict[i[0]]])
    if len(product_dict[ID]) == 1 :
        to_add_function.add("FUNCTION\t"+product_dict[ID][0])
    else:
        for p in product_dict[ID]:
            to_add_function.add("FUNCTION\t"+p)
    to_write=('ID\t{ID}\n' + 
              'NAME\t{ID}\n' +
              'STARTBASE\t1\n' +
              'ENDBASE\t99\n' +
              'PRODUCT-TYPE\tP\n' +
              '{METACYC}\n' +
              '{FUNCTION}\n'+
              '{EC}\n' +
              '//\n').format(ID=ID, EC="\n".join(to_add_EC), METACYC="\n".join(to_add_metacyc), FUNCTION="\n".join(to_add_function) )
    return(to_write)

def create_KO_MR_dict(KO_file, MR_file):
    ko_dict= dict()
    mr_dict = dict()
    with open(KO_file) as ko_file, open(MR_file) as mr_file:
        for line in ko_file:
            l = line.split()
            ko_dict[l[0]] = l[1].strip()
        for line in mr_file:
            l = line.split()
            mr_dict[l[0]] = l[1].strip()
    return(ko_dict, mr_dict)


def parse_kofam_file(kofamout, ko_dict, output, mr_dict):
    kofam_dict = dict()
    product_dict = dict()
    with open(kofamout) as kofam_file:
        with open(output, "w") as output_file:
            for line in kofam_file:
                if line.startswith("*"):
                    l = line.split("\t")
                    if l[2] in mr_dict.keys() and mr_dict[l[2]] in ko_dict.keys():
                        if l[1] not in kofam_dict.keys():
                            kofam_dict[l[1]] = list()
                        if l[1] not in product_dict.keys():
                            product_dict[l[1]] = list()
                        if "[" in line:
                            EC = l[-1].split(":")[-1].split("]")[0]
                            kofam_dict[l[1]].append((l[2], EC))
                            product = l[-1].split("[EC")[0].split('"')[1]
                            product_dict[l[1]].append(product)
                        else:
                            kofam_dict[l[1]].append((l[2]))
                            product = l[-1].split('"')[1]
                            product_dict[l[1]].append(product)
            for ID in kofam_dict:
                entry = create_pf_entry(ID, ko_dict, mr_dict, kofam_dict, product_dict)
                output_file.write(entry)            
    
                        
def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-m", help="Path and name of MR_file)",
        required=True, type=str)
    parser.add_argument(
        "-k", help="Path and name of KO_file",
        required=True, type=str)
    parser.add_argument(
    "-o", help="Path and name for output",
    required=True, type=str)
    parser.add_argument(
    "-f", help="Path and name of kofamout file",
    required=True, type=str)
    args = parser.parse_args()

    (ko_dict, mr_dict) = create_KO_MR_dict(args.m, args.k)
    parse_kofam_file(args.f, ko_dict, args.o, mr_dict)

if __name__ == "__main__":
    main()

