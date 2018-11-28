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
```git clone https://github.com/crowelab/PyIR ```

**Global Installation**
```bash
cd PyIR/
sudo pip install .

```

**Local Installation**
```bash
cd PyIR/
pip install --user .

```
If installing locally confirm pythons local bin is in your path. If not you can add the the following to your ~/.bashrc
```bash
export PY_USER_BIN=$(python -c 'import site; print(site.USER_BASE + "/bin")')
export PATH=$PY_USER_BIN:$PATH
```

**Building the Database**

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

Usage
========
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

Using PyIR as an api
========

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

Synthetic Data Sets
========

Synthetic clonotype data sets for manuscript High frequency of shared clonotypes in human B cell receptor repertoires:
- [HIP1](https://vumc.box.com/s/4j0qik17muxkat610k68n12w4zzgzhrk)
- [HIP2 (Part 1)](https://vumc.box.com/s/choce3dr9tt3ddleyykta0nzmv6kg66y)
- [HIP2 (Part 2)](https://vumc.box.com/s/fpq2morlllk7g5b5hu1858h2xw53a0bn)
- [HIP3](https://vumc.box.com/s/rl3nz1d31ey5vte7rda8heknqtvr7u7g)
- [CORD1](https://vumc.box.com/s/cs42juru0hcm2hvbszak313f4a9jlmro)
- [CORD2](https://vumc.box.com/s/ny0c2q325gshkt65xd2v7vz0dz5s6ir5)
- [CORD3](https://vumc.box.com/s/6lafm9wk2vmzsg3kwuujti3k6woqtf1l)
