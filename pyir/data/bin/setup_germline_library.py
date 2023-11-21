#!/bin/python3

import os
import sys
from os import path
import argparse
import urllib.request
import subprocess
from subprocess import run
import shutil

SPECIES = [{
    'name': 'human',
    'imgt_name': 'Homo_sapiens',
    'ig': {
        'V': ['IGHV','IGKV', 'IGLV'],
        'J': ['IGHJ', 'IGKJ', 'IGLJ'],
        'D': ['IGHD'],
    },
    'tcr': {
        'V': ['TRAV', 'TRBV'],
        'J': ['TRAJ', 'TRBJ'],
        'D': ['TRBD']
    }
}, {
    'name': 'mouse',
    'imgt_name': 'Mus_musculus',
    'ig': {
        'V': ['IGHV', 'IGKV', 'IGLV'],
        'J': ['IGHJ', 'IGKJ', 'IGLJ'],
        'D': ['IGHD'],
    },
    'tcr': {
        'V': ['TRAV', 'TRBV', 'TRDV', 'TRGV'],
        'J': ['TRAJ', 'TRBJ', 'TRDJ', 'TRGJ'],
        'D': ['TRBD', 'TRDD']
    }
}, {
    'name': 'rabbit',
    'imgt_name': 'Oryctolagus_cuniculus',
    'ig': {
        'V': ['IGHV', 'IGKV', 'IGLV'],
        'J': ['IGHJ', 'IGKJ', 'IGLJ'],
        'D': ['IGHD'],
    },
    'tcr': {
        'V': ['TRAV', 'TRBV', 'TRDV', 'TRGV'],
        'J': ['TRAJ', 'TRBJ', 'TRDJ', 'TRGJ'],
        'D': ['TRBD', 'TRDD']
    }
}, {
    'name': 'rat',
    'imgt_name': 'Rattus_norvegicus',
    'ig': {
        'V': ['IGHV', 'IGKV', 'IGLV'],
        'J': ['IGHJ', 'IGKJ', 'IGLJ'],
        'D': ['IGHD'],
    },
    'tcr': {
        'V': [],
        'J': [],
        'D': []
    }
}, {
    'name': 'rhesus_monkey',
    'imgt_name': 'Macaca_mulatta',
    'ig': {
        'V': ['IGHV', 'IGKV', 'IGLV'],
        'J': ['IGHJ', 'IGKJ', 'IGLJ'],
        'D': ['IGHD'],
    },
    'tcr': {
        'V': ['TRAV', 'TRBV', 'TRDV', 'TRGV'],
        'J': ['TRAJ', 'TRBJ', 'TRDJ', 'TRGJ'],
        'D': ['TRBD', 'TRDD']
    }
}]

parser = argparse.ArgumentParser()
parser.add_argument('basedir')
parser.add_argument('outdir')
args = parser.parse_args()

if 'linux' in sys.platform:
    platform = 'linux'
elif 'darwin' in sys.platform:
    platform = 'darwin'
else:
    raise ValueError('Unsupported system platform: ' + sys.platform + ". Run setup_germline_library.py on a Linux or "
                                                                       "OSX machine")
print('setup args:', args)

def get_local_data():
    try:
        os.makedirs(path.join(args.outdir, 'Ig', 'human'))
    except FileExistsError:
        pass
    ig_c_file = path.join(args.outdir, 'Ig', 'human', 'human_gl_C.fasta')
    ig_c_db = path.join(path.dirname(ig_c_file), path.basename(ig_c_file).split('.')[0])

    shutil.copy2(path.join(args.basedir,'crowelab_data','human_gl_C.fasta'), ig_c_file)
    result = run(
        [path.join(args.basedir, 'bin', 'makeblastdb_' + platform), '-dbtype', 'nucl', '-hash_index', '-parse_seqids',
         '-in', ig_c_file, '-out', ig_c_db, '-title', ig_c_db], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)
    print(result.stdout)

    try:
        os.makedirs(path.join(args.outdir, 'TCR', 'human'))
    except FileExistsError:
        pass
    tcr_c_file = path.join(args.outdir, 'TCR', 'human', 'human_TCR_C.fasta')
    tcr_c_db = path.join(path.dirname(tcr_c_file), path.basename(tcr_c_file).split('.')[0])

    shutil.copy2(path.join(args.basedir, 'crowelab_data', 'human_TCR_C.fasta'), tcr_c_file)
    result = run(
        [path.join(args.basedir, 'bin', 'makeblastdb_' + platform), '-dbtype', 'nucl', '-hash_index', '-parse_seqids',
         '-in', tcr_c_file, '-out', tcr_c_db, '-title', tcr_c_db], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True)
    print(result.stdout)

    try:
        # os.remove(path.join(args.outdir, 'prot'))
        shutil.rmtree(path.join(args.outdir, 'prot'))
    except FileNotFoundError:
        pass
    shutil.copytree(path.join(args.basedir,'crowelab_data','prot'), path.join(args.outdir, 'prot'))

def get_imgt_data():
    for species in SPECIES:
        for gene_locus in ['ig', 'tcr']:
            outdir_subfolder = 'Ig' if gene_locus == 'ig' else 'TCR'
            gene_file_ext = 'gl' if gene_locus == 'ig' else 'TCR'
            locus_url_ext = 'IG' if gene_locus == 'ig' else 'TR'

            try:
                os.makedirs(path.join(args.outdir, outdir_subfolder, species['name']))
            except FileExistsError:
                pass

            for gene in species[gene_locus]:
                gene_file = path.join(args.outdir, outdir_subfolder, species['name'], species['name'] + '_' + gene_file_ext + '_' + gene + '.fasta')
                gene_db = path.join(path.dirname(gene_file), path.basename(gene_file).split('.')[0])
                with open(gene_file, 'w') as fasta_out:
                    for locus in species[gene_locus][gene]:
                        locus_url = 'https://www.imgt.org/download/V-QUEST/IMGT_V-QUEST_reference_directory/' + \
                                    species['imgt_name'] + '/' + locus_url_ext + '/' + locus + '.fasta'
                        print('Downloading from:', locus_url)
                        write_out = False
                        for line in urllib.request.urlopen(locus_url):
                            line = line.decode('utf-8')
                            if line[0] == '>':
                                ls = line.strip().split('|')
                                if species['imgt_name'].replace('_',' ') in ls[2]:
                                    fasta_out.write('>' + ls[1] + '\n')
                                    write_out = True
                                else:
                                    write_out = False
                            elif write_out:
                                fasta_out.write(line.replace('.',''))

                result = run([path.join(args.basedir,'bin','makeblastdb_' + platform), '-dbtype', 'nucl', '-hash_index', '-parse_seqids',
                     '-in', gene_file, '-out', gene_db, '-title', gene_db], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)

                print(result.stdout)

get_local_data()
get_imgt_data()
