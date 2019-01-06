[![DOI](https://zenodo.org/badge/105039360.svg)](https://zenodo.org/badge/latestdoi/105039360)

### [Files pertaining to the manuscript *High frequency of shared clonotypes in human B cell receptor repertoires*](#files-associated-with-the-manuscript-high-frequency-of-shared-clonotypes-in-human-b-cell-receptor-repertoires)

#### [Install PyIR globally (for all users of your workstation)](#global-installation)

#### [Install PyIR locally (for the user that you are currently logged in under)](#global-installation)

#### [Building the databases that are used by PyIR](#building-the-database)

#### [Using PyIR from bash](#usage)

#### [Using PyIR as an api](#using-pyir-as-an-api)


# PyIR
Immunoglobulin and T-Cell receptor rearrangement software

A Python wrapper for IgBLAST that scales to allow for the parallel processing of millions of reads on shared memory computers. All output is stored in a convenient JSON format.


Requires
=========



1. Python 3.6
2. Pip version 10.0.1 or greater (python 3.6)
3. MacOSX or Linux
4. wget - Installed on many linux distributions by default. Available for mac through the homebrew package manager

Installation
=========

**Download the repository**

This repository can be downloaded by selecting "Download ZIP" from the "Clone and Download" menu at the top right of this github page or by using git from command line.

If you have git installed you may use the command in order to place a copy of the github repo into your current directory.
```
git clone https://github.com/crowelab/PyIR
```

#### **Global Installation**

Ensure that pip is associated with the correct verison of python. If pip --version says that it is asscoiated with python version 2 then pip3 should be explicityly used instead of pip.
```bash
cd PyIR/
sudo pip install .

```

#### **Local Installation**

Ensure that pip is associated with the correct verison of python. If pip --version says that it is asscoiated with python version 2 then pip3 should be explicityly used instead of pip.
```bash
cd PyIR/
pip install --user .

```
If installing locally confirm pythons local bin is in your path. If not you can add the the following to your ~/.bashrc
```bash
export PY_USER_BIN=$(python -c 'import site; print(site.USER_BASE + "/bin")')
export PATH=$PY_USER_BIN:$PATH
```

#### **Building the Database**

A shell script has been included in this repository which will build the databases and check to make sure that your installation is functioning properly. 
You may run the included "SetupGermlineLibrary.sh" script in order to build the gerline library and load test data. If the setup is successful then a file will be created which is a gunzipped json file containing the output of PyIR for the setup scripts testcase.

```
bash SetupGermlinLibrary.sh
```

<!--
```bash
mkdir pyir_data
cd pyir_data

# Download igblast internal and aux data
# All data can be manually downloaded here ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release or use the following convenience commands
wget -mnH --cut-dirs=4 ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/internal_data ./
wget -mnH --cut-dirs=5 --directory-prefix=aux ftp://ftp.ncbi.nih.gov/blast/executables/igblast/release/optional_file/ ./

# Create Ig and TCR folders.
mkdir -p Ig/human TCR/human
```

Go to http://www.imgt.org/vquest/refseqh.html and copy your human heavy **and** light genes into the following files

pyir_data/Ig/human/human_gl_V.fasta
pyir_data/Ig/human/human_gl_D.fasta
pyir_data/Ig/human/human_gl_J.fasta

Once you've copied the data from IMGT, run the following commands to format the IMGT fastas into fastas makeblastdb can evaluate

```bash
perl edit_imgt_file.pl pyir_data/Ig/human/human_gl_V.fasta > pyir_data/Ig/human/human_gl_V
perl edit_imgt_file.pl pyir_data/Ig/human/human_gl_J.fasta > pyir_data/Ig/human/human_gl_J
perl edit_imgt_file.pl pyir_data/Ig/human/human_gl_D.fasta > pyir_data/Ig/human/human_gl_D
```

PyIr comes packaged with PyIr/bin/makeblastdb_linux and PyIr/bin/makeblastdb_darwin. If on linux use makeblastdb_linux and if on mac use makeblastdb_darwin.
Run the following commands to build the BLAST database from the fastas generated from the previous perl command.

```bash
PyIR/bin/makeblastdb_linux -dbtype nucl -hash_index -parse_seqids -in pyir_data/Ig/human/human_gl_V
PyIR/bin/makeblastdb_linux -dbtype nucl -hash_index -parse_seqids -in pyir_data/Ig/human/human_gl_J
PyIR/bin/makeblastdb_linux -dbtype nucl -hash_index -parse_seqids -in pyir_data/Ig/human/human_gl_D
```
You can run PyIr the following way

```bash
pyir PyIr/testing/1K_Seqs.fasta -d pyir_data
```
-->
## Usage

```
usage: pyir [-h] -d DATABASE [-r {Ig,TCR}] [-s {human,mouse}]
            [-nV NUM_V_ALIGNMENTS] [-nD NUM_D_ALIGNMENTS]
            [-nJ NUM_J_ALIGNMENTS] [-mD MIND] [-cz CHUNK_SIZE] [-x EXECUTABLE]
            [-m MULTI] [-o inputfile.json.gz] [--debug]
            [--additional_field ADDITIONAL_FIELD] [-f json] [--pretty]
            [--silent]
            query.fasta

A Python wrapper for IgBLAST that scales to allow for the parallel processing
of millions of reads on shared memory computers. All output is stored in a
convenient JSON format. Authors - Andre Branchizio, Jordan Willis, Jessica
Finn

optional arguments:
  -h, --help            show this help message and exit

Necessary Arguments:
  Arguments that must be included

  query.fasta           The fasta or fastq file to be run through the protocol

File paths and types:
  Database paths, search types

  -d DATABASE, --database DATABASE
                        Path to your blast database directory
  -r {Ig,TCR}, --receptor {Ig,TCR}
                        The receptor you are analyzing, immunoglobulin or t
                        cell receptor
  -s {human,mouse}, --species {human,mouse}
                        The Species you are analyzing
  -cz CHUNK_SIZE, --chunk_size CHUNK_SIZE
                        How many sequences to work on at once. The higher the
                        number the more memory needed. If none specified chunk
                        size will be determined based on input file size

BLAST Specific Arguments:
  Arguments Specific to IgBlast

  -nV NUM_V_ALIGNMENTS, --num_V_alignments NUM_V_ALIGNMENTS
                        How many V genes do you want to match?
  -nD NUM_D_ALIGNMENTS, --num_D_alignments NUM_D_ALIGNMENTS
                        How many D genes do you want to match?, does not apply
                        for kappa and lambda
  -nJ NUM_J_ALIGNMENTS, --num_J_alignments NUM_J_ALIGNMENTS
                        How many J genes do you want to match?
  -mD MIND, --minD MIND
                        The amount of nucleotide matches needed for a D gene
                        match. >= 5 right now
  -x EXECUTABLE, --executable EXECUTABLE
                        The location of IGBlastn binary, the default location
                        is determined based on the OS and uses the igblast
                        binaries included in this application.

General Arguments:
  Output and Miscellaneous Arguments

  -m MULTI, --multi MULTI
                        Multiprocess by the amount of CPUs you have. Or you
                        can enter a number or type 0 to turn it off
  -o inputfile.json.gz, --out inputfile.json.gz
                        Output_file_name, defaults to inputfile.json.gz
  --debug               Debug mode, this will not delete the temporary blast
                        files and will print some other useful things, like
                        which regions did not parse
  --additional_field ADDITIONAL_FIELD
                        A comma key,value pair for an additional field you
                        want to add to the output json. Example '--
                        additional_field=donor,10` adds a donor field with
                        value 10.
  -f json, --out-format json
                        Output file format, only json currently supported
  --pretty              Pretty json output
  --silent              Silence stdout
```

# Using PyIR as an api


```python
import json
import pyir.factory
import tempfile

input_file = open('1K_Seqs.fasta', 'r')
out_file = tempfile.NamedTemporaryFile(delete=True)
num_procs = 4
argument_overrides = {
    'silent': True,
    'database': 'Path/To/Database',
    'query': input_file,
    'out': out_file.name,
    'multi': num_procs
}

py_ir = pyir.factory.PyIr(argument_overrides)
result = py_ir.run()
for line in result:
    seq = json.loads(line)
    # Do whatever you need with the resulting sequence
    print(seq['Sequence ID'], seq['Top V gene match'] if 'Top V gene match' in seq else 'No match' )

```






______
## Files associated with the manuscript *High frequency of shared clonotypes in human B cell receptor repertoires*

- [Source code (Recombinator and additional scripts)](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/SOURCECODE-2017-09-12766.tgz)

Adaptive Biotechnologies data sets (FASTA)

- [HIP2](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HIP2-BCR-ADAPTIVE.tgz)

Data sets obtained from sequencing

- [HIP1-3 heavy chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HEAVY-CHAINS/FIGURE2A-V3J-EXPERIMENTAL-CLONOTYPES-HIP1-3.tgz)

- [HIP1-3 heavy chain V3DJ clonotypes](crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HEAVY-CHAINS/FIGURE2B-V3DJ-EXPERIMENTAL-CLONOTYPES-HIP1-3.tgz)

- [Shared HIP1+2+3 heavy chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HEAVY-CHAINS/FIGURE2D-SHARED-HEAVY.tgz)

- [HIP1-3 kappa light chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/LIGHT-CHAINS/EXTENDED-DATA-FIGURE2G-V3J-EXPERIMENTAL-CLONOTYPES-HIP1-3-IGK.tgz)

- [HIP1-3 lambda light chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/LIGHT-CHAINS/EXTENDED-DATA-FIGURE2G-V3J-EXPERIMENTAL-CLONOTYPES-HIP1-3-IGL.tgz)

- [CORD1-3 heavy chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/CORD1-3_BCR/FIGURE3C-V3J-EXPERIMENTAL-CLONOTYPES-CORD1-3.tgz)

- [CORD1-3 heavy chain V3DJ clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/CORD1-3_BCR/EXTENDED-DATA-FIGURE3A-V3DJ-EXPERIMENTAL-CLONOTYPES-CORD1-3.tgz)

- [Shared HIP1+2+3 and CORD1-3 heavy chain V3J clonotypes](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/ALL+CORD1+CORD2+CORD3.dat.gz)


Synthetic data sets created using Recombinator

- [500 subsampled heavy chain V3DJ clonotypes for HIP1, HIP2 and HIP3](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HEAVY-CHAINS/FIGURE2A-V3J-EXPERIMENTAL-CLONOTYPES-HIP1-3.tgz)

- [Full set of synthetic clonotypes for HIP1 (broken down by CDR3 length)](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HIP1+FULL-REPERTOIRE-BROKEN-DOWN-BY-CDR3-LENGTH.tar)

- [Full set of synthetic clonotypes for HIP2 (broken down by CDR3 length)](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HIP2+FULL-REPERTOIRE-BROKEN-DOWN-BY-CDR3-LENGTH.tar)

- [Full set of synthetic clonotypes for HIP3 (broken down by CDR3 length)](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/HIP1-3_BCR/HIP3+FULL-REPERTOIRE-BROKEN-DOWN-BY-CDR3-LENGTH.tar)

- [100 sampled heavy chain V3DJ clonotypes for CORD1, CORD2 or CORD3](https://s3.amazonaws.com/crowelabpublicdataforpublications/HIP/CORD1-3_BCR/SYNTHETIC-CORDS.tgz)


 <!--
Synthetic clonotype data sets:
- [simHIP1](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/HIP1.tar)
- [simHIP2](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/HIP2.tar)
- [simHIP3](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/HIP3.tar)
- [simCORD1](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/CORD1.tar)
- [simCORD2](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/CORD2.tar)
- [simCORD3](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/CORD3.tar)

Recombinator & additional scripts:
- [Recombinator & other scripts](https://s3.amazonaws.com/crowelab-datasets-for-publication/SEEQ-PAPER-FILES/SOURCECODE-2017-09-12766.tgz)
-->
