#!/bin/bash
#SBATCH --job-name=pgdb_pipeline
#SBATCH --output pgdb_pipeline%A_%a.out
#SBATCH --mem-per-cpu=10240
#SBATCH --cpus-per-task=2
#SBATCH --time=24:00:00
#SBATCH -p normal

######################################
## prodigal scan on inti
## allow multiple prodigal analysis in parrallel with the array option of sbatch on slurm
##
## commande line example
##sbatch --array=1-3%3 run_kofam.sh -f liste.txt -p path_of_input_data_folder -o path_of_output_data_folder
######################################


#ARGUMENTS
# 1. list of protein prediction using prodigal named *_annot_prot.faa
# 2. Path of input data folder
# 3. Path of output data folder
#######################################

##########Initialize variables to default values############


UsageInfo () {
    echo "usage : sbatch --array=1-3%3 run_kofam.sh -f info_file -p annotations_folder -k kofamdatabase -i fasta files folder -o path_of_output_data_folder  "
    echo "-f : path and name of the file with informations about strains as presented in the example_file"
    echo "-p : path of folder with proteins annotations"
    echo "-i : input folder with fasta files"
    echo "-o : path of output folder"
    echo "-h : print this help"
}

##################### options #############

options=':h:f:p:o:i:'

while getopts $options option; do
  case "$option" in
	  h) echo "$usage"; exit;;
	  f) INFOFILE=${OPTARG};;
	  i) INFOLDER=${OPTARG};;
	  p) ANNOTATIONS=${OPTARG};;
	  o) OUTFOLDER=${OPTARG};;
	  :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
     \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done

### Modules ##############
module load extenv/labgem
module load kofamscan/1.3.0
module load pathway-tools/27.0.p1
module load prodigal/2.6.3
KOFAM_PATHWAY="/env/cns/proj/agc/bank/KOFAM/29_11_2023"
MR_file="/env/cns/proj/agc/proj/metacoco/bin/metacyc_kegg_reactions_crossref_web.tsv"
KO_file="/env/cns/proj/agc/proj/metacoco/bin/kegg_orthology_reactions_crossref.tsv"

create_ptools_local ${OUTFOLDER}
export PTOOLS_LOCAL_PATH=${OUTFOLDER}/
export PTOOLS_LOCAL_PATH_INPUTS=${OUTFOLDER}/inputs

##########  Script  ################
INPUTS=($INFOLDER/*.fna)

mkdir -p ${OUTFOLDER}
ls -l ${INFOLDER} | tail -n+2 | awk '{print $9}' | awk -F ".fna" '{print $1}' > ${OUTFOLDER}/Listegenomes.txt

i=${INPUTS[$SLURM_ARRAY_TASK_ID]}
echo $i
IDname=$(basename "${i%*_*}")

echo ${IDname}
echo "reorganize folder in /inputs/"
mkdir -p ${OUTFOLDER}/KOFAM
mkdir -p ${OUTFOLDER}/inputs/${IDname}
cp ${i} ${OUTFOLDER}/inputs/${IDname}/${IDname}.fna



echo "check annotations"

#1 run prodigal if annotation not provided
if [ ! "$ANNOTATIONS" ] ; then
echo "pas d'annotations"
mkdir -p ${OUTFOLDER}/ANNOTATIONS
ANNOTATIONS=${OUTFOLDER}/ANNOTATIONS
prodigal -i ${INPUTS[$SLURM_ARRAY_TASK_ID]} -o ${OUTFOLDER}/ANNOTATIONS/${IDname}_prodigal_genes -a ${OUTFOLDER}/ANNOTATIONS/${IDname}_annot_prot.faa
fi

#run kofam
exec_annotation --cpu 2 -p ${KOFAM_PATHWAY}/profiles -k ${KOFAM_PATHWAY}/ko_list --tmp-dir=${OUTFOLDER}/KOFAM/tmp_${IDname} -f detail-tsv -o ${OUTFOLDER}/KOFAM/${IDname}_kofamout.txt ${ANNOTATIONS}/${IDname}_annot_prot.faa
rm -r ${OUTFOLDER}/KOFAM/tmp_${IDname}
awk -F "\t" '$6<0.001 {print $0}' ${OUTFOLDER}/KOFAM/${IDname}_kofamout.txt > ${OUTFOLDER}/KOFAM/${IDname}_kofamout_e001.txt


StrainName=$(grep -w ${IDname} ${INFOFILE} | awk -F "\t" '{print $2}')
NCBI_strain_ID=$(grep -w ${IDname} ${INFOFILE} | awk -F "\t" '{print $1}')
NCBI_TaxaID=$(grep -w ${IDname} ${INFOFILE} | awk -F "\t" '{print $3}')

#create .dat files

echo -e 'ID\t'$IDname'
STORAGE\tFILE
NAME\t'$StrainName'
ABBREV-NAME\t'$StrainName'
STRAIN\t'$NCBI_strain_ID'
CREATE?\tT
DOMAIN\tTAX-'$NCBI_TaxaID'
RANK\tspecies
AUTHOR\tLABGeM' > ${OUTFOLDER}/inputs/${IDname}/organism-params.dat

echo -e 'ID\t'$IDname'C
NAME\t'$IDname'C
TYPE\t:CHRSM
CIRCULAR?\tY
ANNOT-FILE\t'$IDname'.pf
SEQ-FILE\t'$IDname'.fna
//' > ${OUTFOLDER}/inputs/${IDname}/genetic-elements.dat


echo ${IDname} >> ${OUTFOLDER}/Shortname.txt

echo "create pf file"

echo "python3 create_pf_file.py -m ${MR_file} -k ${KO_file} -o ${OUTFOLDER}/inputs/${IDname}/${IDname}.pf -f ${OUTFOLDER}/KOFAM/${IDname}_kofamout_e001.txt"
python3 /env/cns/proj/agc/proj/metacoco/bin/create_pf_file.py -m ${MR_file} -k ${KO_file} -o ${OUTFOLDER}/inputs/${IDname}/${IDname}.pf -f ${OUTFOLDER}/KOFAM/${IDname}_kofamout_e001.txt
echo "ok pf file"

echo "enter ptools"
echo "pathologic_batch ${PTOOLS_LOCAL_PATH_INPUTS}/${IDname}"
pathologic_batch ${PTOOLS_LOCAL_PATH_INPUTS}/${IDname}

echo "ok ptools"
