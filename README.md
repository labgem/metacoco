

# Readme.md


MetaCoco: METAbolism COmpletion for microbial COmmunities
-------------

**MetaCoCo** is a Bash/Python pipeline that generates a completion matrix of
[MetaCyc](https://metacyc.org/) metabolic pathways for one or multiple bacterial
genomes or metagenomes, starting from FASTA files.

The pipeline performs:
- gene prediction using [Prodigal](https://github.com/hyattpd/Prodigal),
- functional annotation with [KofamScan](https://github.com/takaram/kofam_scan),
- metabolic pathway inference using
  [Pathway Tools](https://bioinformatics.ai.sri.com/ptools/).

This version is currently designed to run MetaCoCo on a Linux cluster using the SLURM job scheduler and Environment Modules for managing the following software dependencies:

[![](https://img.shields.io/badge/kofam_scan-1.3.0-brightgreen.svg)](https://github.com/takaram/kofam_scan) 
[![](https://img.shields.io/badge/prodigal-2.6.3-brightgreen.svg)](https://github.com/hyattpd/Prodigal) 
[![](https://img.shields.io/badge/biopython-1.78-brightgreen.svg)](https://github.com/biopython/biopython) 
[![](https://img.shields.io/badge/Pathway%20Tools-27.0-brightgreen.svg)](https://bioinformatics.ai.sri.com/ptools/) 
[![](https://img.shields.io/badge/%20PythonCyC-1.1-brightgreen.svg)](https://github.com/ecocyc/PythonCyc)

**Usage**

- Run the main script: 

```bash
sbatch --array=0-N run_ptools_pipeline.sh -i GENOMES/ -o results -f metacoco_input.csv -t HIGH/MIDDLE/LOW
or 
sbatch --array=0-N run_ptools_pipeline.sh -i GENOMES/ -o results -f metacoco_input.csv -t HIGH/MIDDLE/LOW -p ANNOTATIONS/
```

- Once it's done, please run:
```bash
sbatch -c2 run_create_completion_matrix.sh -i results/ -l results/Shortname.txt
```

**Input files**

The script takes a folder containing fasta files, an metacoco_input.csv file and a -t argument to specify the threshold of stringency, as input.

A optional argument -p allow to give your own annotations.

*Input data*
   
	Folder_input
	
	metacoco_input.csv
	
	GENOMES/
	
	├── GENOME1_genomic.fna
	
	├── GENOME2_genomic.fna
	
	├── GENOME3_genomic.fna
	
	│   ...
    

Input files must have the exact same name as in the metacoco_input.csv and finished with _genomic.fna 

**WARNING**

As Pathway Tools is very specific about names, please use only name in uppercase and without any other specific character

ex : gca_XXXX_genomic.fna 

=> GCAXXXX_genomic.fna

*metacoco_input.csv file*

This is a required file to run PathoLogic and allowed to give more informations to Pathway Tools. The more precise you are, the more accurate will be the prediction.

This is a tabulated file, with minimum informations as followed : 

    | ncbi_organism_name | ncbi_strain_identifiers | ncbi_taxid |

    | GENOME1 | GCAXXXXX |  1735114 |
   
	| GENOME2 | GCAXXXXX |  1926873 |


**Output files**

MetaCoCo is going to produce two types of completion matrix:

- Individual matrix for each genome

- 1 matrix gathering all the results of each genome

In the results/ folder you will find the raw results of Pathologic/Pathway Tools.

For more informations about the differents formats, please refer here: https://bioinformatics.ai.sri.com/ptools/flatfile-format.html

In your main folder you will find all the matrix in a csv tabulated format.


References
------------

.. [Hyatt2010] Hyatt, D., Chen, G.-L., Locascio, P. F., Land, M. L., Larimer, F. W. & Hauser, L. J. Prodigal: prokaryotic gene recognition and translation initiation site identification. *BMC Bioinformatics* 11, 119 (2010). https://doi.org/10.1186/1471-2105-11-119

.. [Aramaki2020] Aramaki, T., Blanc-Mathieu, R., Endo, H., Ohkubo, K., Kanehisa, M., Goto, S. & Ogata, H. KofamKOALA: KEGG Ortholog assignment based on profile HMM and adaptive score threshold. *Bioinformatics* 36(7), 2251–2252 (2020). https://doi.org/10.1093/bioinformatics/btz859

... [MetaCyc20] R.Caspi, R.Billington, I.M. Keseler, A.Kothari, M.Krummenacker, P.E.Midford, W.K. Ong, S.Paley, P.Subhraveti, P.D. Karp The MetaCyc database of metabolic pathways and enzymes - a 2019 update
Nucleic Acids Res48(D1):D445-D453 (2020). https://doi.org/10.1093/nar/gkz862

.. [PTools24] Karp, P. D., Paley, S. M., Midford, P. E., Krummenacker, M., Billington, R., Kothari, A., Ong, W. K., Subhraveti, P., Keseler, I. M. & Caspi R. Pathway Tools version 28.0: Integrated Software for Pathway/Genome Informatics and Systems Biology. arXiv (2024). https://doi.org/10.48550/arXiv.1510.03964

License
-------

This software is licensed under the GNU LGPL-3.0-or-later
