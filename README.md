# PyIR
An IgBLAST wrapper and parser

PyIR is a minimally-dependent high-speed wrapper for the IgBLAST immunoglobulin and T-cell analyzer. This is achieved 
through chunking the input data set and running IgBLAST single-core in parallel to better utilize modern multi-core and 
hyperthreaded  processors. 

PyIR has become an essential part of the Vanderbilt Vaccine Center workflow, and the requirements in the past few years 
 has lead to the development of new features including:
- Parsing algorithm refactorization
- AIRR naming compliance
- Updated IgBlast binary
- Multiple output formats (including python dictionary)
- Built-in sequence filtering
- Simplified command-line interface

## Requires
1. Linux
2. Python 3.6
3. Pip version >=10.0.1 and the following packages: [tqdm](https://github.com/tqdm/tqdm)
4. Any requirements for [IgBLAST](https://ncbi.github.io/igblast/) (including glibc >= 2.14)
5. wget, gawk


## Files for testing and Manuscripts

Test files used for the BMC Bioinformatics manuscript can be found at:
https://clonomatch.accre.vanderbilt.edu/pyirfiles/

Files pertaining to the manuscript *High frequency of shared clonotypes in human B cell receptor repertoires* and be found at: https://github.com/crowelab/PyIR/wiki/Files-for-Manuscripts


## Installation
PyIR is installed with the [pip](https://pip.pypa.io/en/stable/installing/) software packager, but is not 
currently a part of the PyPI repository index. It can be manually downloaded and installed as followed:

### 1. Download the repository
This repository can be downloaded by selecting "Download ZIP" from the "Clone and Download" menu at the top right of this github page or by using git from command line:

```
git clone https://github.com/crowelab/PyIR
```

### 2. Install with pip

#### Global Installation

```bash
cd PyIR/
sudo pip3 install .
```

#### Local Installation

```bash
cd PyIR/
pip3 install --user .
```

#### Potential Issues:
##### 1. Can't find pyir executable
Locate your local bin folder with PyIR and add it to your PATH variable. ~/.local/bin and /usr/local/bin are good places
to start. If using scl or other virtual environments (such as conda) be sure to account for those when searching your 
directories.

##### 2. Error with IgBLAST executable
Double-check that you've met all prerequisites to install IgBLAST, including GLIBC > 2.14 (which has caused issues 
with CentOS 6) and libuv (can be installed with "sudo apt install libuv1.dev")

##### 3. Installed correctly but packages are missing
Ensure that the version of pip used to install pyir is associated with the correct version of python you are 
attempting to run. This can also be an issue with virtual environments.



## Database Setup

PyIR requires a set of BLAST germline databases to assign the VDJ germlines.

A snapshot of the IMGT/GENE-DB human immunome repertoire is included with PyIR, but users are recommended to build 
their own database to keep up with the newest germline definitions. A link to the full instructions from NCBI can be 
found [here](https://ncbi.github.io/igblast/cook/How-to-set-up.html), or you can use PyIR's setup script to build the 
databases automatically:


```bash
#Builds databases in pyir library directory
pyir setup

#Builds databases in specified path
pyir setup -o path/
```

## Examples

### CLI
```bash
#Default PyIR
pyir example.fasta

#PyIR with filtering
pyir example.fasta --enable_filter

#PyIR with custom BLAST database
pyir example.fasta -d [path_to_DB]
```

### API

#### Example 1: Running PyIR on a fasta and getting filtered sequences back as Python dictionary

```python
## Initialize PyIR and set example file for processing
from pyir import PyIR
FILE = 'example.fasta'

pyirfiltered = PyIR(query=FILE, args=['--outfmt', 'dict', '--enable_filter'])
result = pyirfiltered.run()

#Prints size of Python returned dictionary
print(len(result))
 ```

#### Example 2: Count the number of somatic variants per V3J clonotype in the returned results and print the top 10 results
```python
## Initialize PyIR and set example file for processing
from pyir import PyIR
FILE = 'example.fasta'

sv = {}
for key, entry in result.items():
    v3j = entry['v_family'] + '_' + entry['j_family'] + '_' + entry['cdr3_aa']
    if v3j not in sv:
        sv[v3j] = 0
    sv[v3j] += 1

for i,item in enumerate(sorted(sv.items(), key=lambda x: x[1], reverse=True)):
    if i > 9:
        break
    v3j = item[0].split('_')
    print('v:', v3j[0], 'j:', v3j[1], 'cdr3:', v3j[2], 'count:', item[1])
```

#### Example 3: Process example file and return filepath
```python
## Initialize PyIR and set example file for processing
from pyir import PyIR
FILE = 'example.fasta'

pyirfile = PyIR(query=FILE)
result = pyirfile.run()

#Prints the output file
print(result)
```

#### Example 4: Process example file in and return filepath to results in MIARR format
```python
## Initialize PyIR and set example file for processing
from pyir import PyIR
FILE = 'example.fasta'

pyirfile = PyIR(query=FILE, args=['--outfmt', 'tsv'])
result = pyirfile.run()

#Prints the output file
print(result)
```

#### Example 5: Plot CDR3 length distribution histogram
```python
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import figure
## Initialize PyIR and set example file for processing
from pyir import PyIR
FILE = 'example.fasta'

#create PyIR API instance and return Python dictionary
pyirexample = PyIR(query=FILE, args=['--outfmt', 'dict', '--enable_filter'])
result = pyirexample.run()

cdr3lens = {}
total_reads = 0

#iterate over values returned by PyIR
for key, entry in result.items():
	clen = entry['cdr3_aa_length']
	#if the CDR3 length is not in the dictionary, add it
	if int(clen) not in cdr3lens.keys():
		cdr3lens[int(clen)] = 0
	#increment appropriate dictionary value and total
	cdr3lens[int(clen)] += 1
	total_reads += 1

x = []
y = []

for xval in sorted(cdr3lens.keys()):
	x.append(xval)
	y.append(cdr3lens[xval]/total_reads)

fig, ax = plt.subplots(1 , 1, dpi=600, facecolor='None', edgecolor='None')
plt.bar(x, y, color="#a0814b")
fig.savefig("synth01_cdr3length_distribution.svg", bbox_inches='tight', pad_inches=0)
```

## Contact

Email pyir@vvcenter.org with any questions or open an issue on Github and we'll get back to you.
