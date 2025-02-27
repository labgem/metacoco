#!/bin/bash
#SBATCH --job-name=run_completion_matrix
#SBATCH --output completion_matrix%A_%a.out
#SBATCH --mem-per-cpu=10240
#SBATCH --time=03:00:00
#SBATCH -p normal


usage="sh run_pathwaytools.sh -i $(pwd)/Data -o $(pwd)/Analysis -p $(pwd)/ANNOTATIONS

Make a user provide a input Data folder and output data folder to perform full pathwaytools analysis
where:
    -h  show this help text
    -i  path to the Input Fasta Data folder (ex : $(pwd)/Data
    -o  path to output folder (ex ex : $(pwd)/Analysis)
    -p  path to the Annotation Data folder (ex : $(pwd)/ANNOTATIONS"

UsageInfo () {
    echo "usage : bash run_pathwaytools.sh -p fasta_folder -o output_data_folder -p annotation_folder"
    echo "-i : path of ptools-local with PGDB to analyse"
    echo "-l : list of PGDB"
    echo "-m : Argument for missing value : O or NA - 0 by default"
    echo "-h : print this help"
}

##################### options #############

options=':h:i:l:m:'

while getopts $options option; do
  case "$option" in
          h) echo "$usage"; exit;;
          i) PTOOLSPATH=${OPTARG};;
          l) PGDB=${OPTARG};;
          m) VALUE=${OPTARG};;
          :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
     \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done


# mandatory arguments
if [ ! "$PTOOLSPATH" ] || [ ! "$PGDB" ]  ; then
  echo "arguments -i and -l must be provided!"
  echo "$usage" >&2; exit 1
fi

### LINKS ######

################

### Modules ##############
module load extenv/labgem
module load pythoncyc
module load biopython/1.78

##########################


start_ptools_server() {
    echo "Start server ..."
    pathway-tools -lisp -python-local-only-non-strict > ptools.out 2>ptools.err  &
    server_pid=$!

    # Wait for the server to start (max 300 seconds)
    for attempt in {1..10}; do
        my_pid=$(lsof -t -i tcp:5008)

        if [[ -n $my_pid ]]; then
            # Make sure the running server is the one we just started.
            if [[ $my_pid -ne $server_pid ]]; then
                echo "ERROR: Multiple ptools Servers running."
                echo "→ lsof -t -i tcp:5008 | xargs kill"
                exit 1
            fi

            break
        fi

        sleep 30
    done

    if [[ -z $my_pid ]]; then
        echo "ERROR: Timeout while waiting for ptools Server"
        stop_ptools_server
        exit 1
    fi
}

stop_ptools_server() {
    echo "Stop Server ..."
    kill -9 $server_pid
}


#1 declare ptools path


export PTOOLS_LOCAL_PATH=${PTOOLSPATH}/
export PTOOLS_LOCAL_PATH_INPUTS=${PTOOLSPATH}/inputs

echo ${PTOOLS_LOCAL_PATH_INPUTS}

start_ptools_server

echo "Server running ..."
echo "Starting PGDB extraction ..."

#run pyhtoncyc extractions

if [ ! "$VALUE" ] ; then
echo "no value"
VALUE="0"
fi

echo "python3 create_completion_matrix.py -l ${PGDB} -m ${VALUE}"
python3 create_completion_matrix.py -l ${PGDB} -m ${VALUE}


stop_ptools_server
