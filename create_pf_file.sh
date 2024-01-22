#!/bin/bash
#SBATCH --job-name=pf_file
#SBATCH --output pf_file%A_%a.out
#SBATCH --mem-per-cpu=10240
#SBATCH --time=03:00:00
#SBATCH -p normal


######################################
## create pf file for ptools analysis on inti
## allow multiple file creation in parrallel with the array option of sbatch on slurm
##
## commande line example
##sbatch --array=0-10%10 create_pf_file.sh -m $MR_file -k $KO_file -p $INFOLDER -o $OUTFOLDER
######################################


#ARGUMENTS
# 1. list of protein prediction using prodigal named *_prodigal_prot.faa
# 2. Path of input data folder
# 3. Path of output data folder
#######################################

##########Initialize variables to default values############


UsageInfo () {
    echo "usage : sbatch --array=0-10%10 create_pf_file.sh -m $MR_file -k $KO_file -p $INFOLDER -o $OUTFOLDER"
    echo "-o : path of output folder"
    echo "-k : KO_file"
    echo "-m : MR_file"
    echo "-h : print this help"
}

##################### options #############

options=':h:o:k:m:'

while getopts $options option; do
  case "$option" in
	  h) echo "$usage"; exit;;
	  o) OUTFOLDER=${OPTARG};;
	  k) KO_file=${OPTARG};;
	  m) MR_file=${OPTARG};;
	  :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
     \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done




##########  Script  ################

INPUTS=($OUTFOLDER/KOFAM/*_kofamout_e001.txt)
echo ${INPUTS}

echo ${OUTFOLDER}
echo ${KO_file}
echo ${MR_file}
i=${INPUTS[$SLURM_ARRAY_TASK_ID]}
IDname=$(basename $i _kofamout_e001.txt)

echo ${IDname}

#run python script
echo "python3 create_pf_file.py -m ${MR_file} -k ${KO_file} -o ${OUTFOLDER}/inputs/${IDname}/${IDname}.pf -f ${INPUTS[$SLURM_ARRAY_TASK_ID]}"
python3 create_pf_file.py -m ${MR_file} -k ${KO_file} -o ${OUTFOLDER}/inputs/${IDname}/${IDname}.pf -f ${INPUTS[$SLURM_ARRAY_TASK_ID]}

