

# Readme.md


![](https://img.shields.io/badge/Pathway%20Tools-27.0-brightgreen.svg) ![](https://img.shields.io/badge/%20PythonCyC-1.1-brightgreen.svg)

MetaCoco : METAbolism COmpletion for microbial COmmunities
-------------

MetaCoco is a bash/python pipeline that creates a completion matrix of metabolic pathways for one or many  bacterian genomes/metagenomes starting from fasta or gbk/gbff files.


**Table of Contents**

[TOCM]

[TOC]

#Availability

This version is currently designed to run MetaCoCo on the inti server : https://inti.cnrgh.fr/
A specific access is required.

#Use

##Run on inti


- Run the main script : 

```bash
sbatch --array=0-N run_ptools_pipeline.sh -i GENOMES/ -o results -f metacoco_input.csv -t HIGH/MIDDLE/LOW
or 
sbatch --array=0-N run_ptools_pipeline.sh -i GENOMES/ -o results -f metacoco_input.csv -t HIGH/MIDDLE/LOW -p ANNOTATIONS/
```

- Once it's done, please run :
```bash
sbatch -c2 run_create_completion_matrix.sh -i results/ -l results/Shortname.txt
```

##Input files
The script takes a folder containing fasta files, an metacoco_input.csv file and a -t argument to specify the threshold of stringency, as input.
A optional argument -p allow to give your own annotations.

#####Input data
    Folder_input
	metacoco_input.csv
	GENOMES/
	├── GENOME1_genomic.fna
	├── GENOME2_genomic.fna
	├── GENOME3_genomic.fna
	│   ...
    

Input files must have the exact same name as in the metacoco_input.csv and finished with _genomic.fna 

**ATTENTION :** As Pathway Tools is very specific about names, please use only name in uppercase and without any other specific character

ex : gca_XXXX_genomic.fna 
=> GCAXXXX_genomic.fna

#####metacoco_input.csv file

This is a required file to run PathoLogic and allowed to give more informations to Pathway Tools. The more precise you are, the more accurate will be the prediction.

This is a tabulated file, with minimum informations as followed : 

    | ncbi_organism_name | ncbi_strain_identifiers | ncbi_taxid |

    | GENOME1 | GCAXXXXX |  1735114 |
    | GENOME2 | GCAXXXXX |  1926873 |


##Output files

MetaCoCo is going to produce two types of completion matrix :

- Individual matrix for each genome
- 1 matrix gathering all the results of each genome

In the results/ folder you will find the raw results of Pathologic/Pathway Tools.
For more informations about the differents formats, please refer here : https://bioinformatics.ai.sri.com/ptools/flatfile-format.html

In your main folder you will find all the matrix in a csv tabulated format.


Bibliography
------------

.. [Green2004] Green, M.L., Karp, P.D. A Bayesian method for identifying missing enzymes in predicted metabolic pathway databases. BMC Bioinformatics 5, 76 (2004). https://doi.org/10.1186/1471-2105-5-76

.. [Karp2011] Karp, P. D., Latendresse, M., & Caspi, R. The pathway tools pathway prediction algorithm. Standards in genomic sciences 5(3), 424–429 (2011). https://doi.org/10.4056/sigs.1794338

.. [Karp2018] Karp, P. D., Weaver, D. & Latendresse, M. How accurate is automated gap filling of metabolic models?. BMC Systems Biology 12(1), 73 (2018). https://doi.org/10.1186/s12918-018-0593-7

.. [Karp2019arXiv] Karp, P. D., Paley, S. M., Midford, P. E., Krummenacker, M., Billington, R., Kothari, A., Ong, W. K., Subhraveti, P., Keseler, I. M. & Caspi R. Pathway Tools version 23.0: Integrated Software for Pathway/Genome Informatics and Systems Biology. arXiv (2019). https://arxiv.org/abs/1510.03964v3

.. [PathwayToolsarXiv] Karp, P. D., Paley, S. M., Midford, P. E., Krummenacker, M., Billington, R., Kothari, A., Ong, W. K., Subhraveti, P., Keseler, I. M. & Caspi R. Pathway Tools: Integrated Software for Pathway/Genome Informatics and Systems Biology. arXiv. https://arxiv.org/abs/1510.03964

License
-------

This package is licensed under the GNU LGPL-3.0-or-later
