import functools
import multiprocessing
import pkg_resources
import os
from . import arg_parse, igblast
import shutil
import signal
import subprocess
import tempfile
import time
import tqdm

IGBLAST_TSV_HEADER = ['sequence_id','sequence','locus','stop_codon','vj_in_frame','productive','rev_comp','complete_vdj','v_call','d_call','j_call','sequence_alignment','germline_alignment','sequence_alignment_aa','germline_alignment_aa','v_alignment_start','v_alignment_end','d_alignment_start','d_alignment_end','j_alignment_start','j_alignment_end','v_sequence_alignment','v_sequence_alignment_aa','v_germline_alignment','v_germline_alignment_aa','d_sequence_alignment','d_sequence_alignment_aa','d_germline_alignment','d_germline_alignment_aa','j_sequence_alignment','j_sequence_alignment_aa','j_germline_alignment','j_germline_alignment_aa','fwr1','fwr1_aa','cdr1','cdr1_aa','fwr2','fwr2_aa','cdr2','cdr2_aa','fwr3','fwr3_aa','fwr4','fwr4_aa','cdr3','cdr3_aa','junction','junction_length','junction_aa','junction_aa_length','v_score','d_score','j_score','v_cigar','d_cigar','j_cigar','v_support','d_support','j_support','v_identity','d_identity','j_identity','v_sequence_start','v_sequence_end','v_germline_start','v_germline_end','d_sequence_start','d_sequence_end','d_germline_start','d_germline_end','j_sequence_start','j_sequence_end','j_germline_start','j_germline_end','fwr1_start','fwr1_end','cdr1_start','cdr1_end','fwr2_start','fwr2_end','cdr2_start','cdr2_end','fwr3_start','fwr3_end','fwr4_start','fwr4_end','cdr3_start','cdr3_end','np1','np1_length','np2','np2_length']
MAX_CHUNK_SIZE = 1000

class PyIR():
    """The primary class for PyIR"""
    def __init__(self, query=None, args=None, is_api=True):
        self.is_api = is_api
        if not self.is_api:
            self.args = arg_parse.PyIrArgumentParser().parse_arguments()
        else:
            if not query:
                raise ValueError('No query provided to PyIR')

            args_formatted = [query]
            if args:
                if isinstance(args, dict):
                    for key in args.keys():
                        args_formatted.append(key if key.startswith('-') else '--' + key)
                        args_formatted.append(args[key])
                elif isinstance(args, list) or isinstance(args, tuple):
                    for item in args:
                        args_formatted.append(item)

            self.args = arg_parse.PyIrArgumentParser().parse_arguments(args_formatted)

        self.setup = True if self.args['query'] == 'setup' else False

        # self.args = args
        self.legacy = self.args['legacy']
        self.debug = self.args['debug']
        self.silent = self.args['silent']
        self.num_procs = self.args['multi']
        if not os.path.exists(self.args['tmp_dir']):
            os.makedirs(self.args['tmp_dir'])

        self.input_file = self.args['query']
        self.input_type = self.args['input_type']

        if not self.setup:
            self.chunk_size = self.args['chunk_size'] if self.args['chunk_size'] else self.get_chunk_size()
            self.tmp_dir = tempfile.mkdtemp(dir=self.args['tmp_dir'])
            self.args['tmp_dir'] = self.tmp_dir
            self.output_file = self.args['out'] if self.args['out'] else self.input_file.split('.')[0]
            if self.args['outfmt'] in ['json', 'lsjson']:
                self.output_file += '.json'
            elif self.args['outfmt'] == 'tsv':
                self.output_file += '.tsv'
        else:
            self.output_folder = self.args['out'].rstrip('/\\') if self.args['out'] else \
                pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/germlines")


#        IgBLAST Arguments
#
#
        self.executable = self.args['executable']
        self.minD = self.args['minD']
        self.numV = self.args['num_V_alignments']
        self.numD = self.args['num_D_alignments']
        self.numJ = self.args['num_J_alignments']
        self.num_procs = self.args['multi']
        self.species = self.args['species']
        self.receptor = self.args['receptor']
        self.word_size = self.args['word_size']

#       Filtering Arguments
#
#
        self.use_filter = self.args['enable_filter']

        if self.args['outfmt'] == 'tsv':
            self.outkeys = IGBLAST_TSV_HEADER
            if 'additional_field' in self.args and self.args['additional_field']:
                self.outkeys.extend([self.args['additional_field'][0]])
            self.outkeys.extend(['v_family', 'd_family', 'j_family', 'cdr3_aa_length'])

        self.gzip_output = self.args['gzip']
        self.progress = None

    def run_setup(self):
        if not os.path.exists(
                pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/bin")):
            raise FileNotFoundError("Missing package bin directory -- was PyIR installed correctly?")

        baseArgs = ['bash',
                    pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"),
                                                    "pyir/data/bin/SetupGermlineLibrary.sh"),
                    pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/bin"),
                    self.output_folder]

        subprocess.run(baseArgs)

    def run(self):
        """Manages overall program execution. Function generally follows these steps:
        1. Takes input
        2. Splits input into chunks in temporary data directory.
        3. Multithread chunks and run each through igBlast executable, parser, filtering, etc.
        4. Takes chunked results, combines into one and zips up output"""
        if self.setup:
            return self.run_setup()


        if not self.silent:
            start = time.time()
            print('Splitting input {0} file {1}'.format(self.input_type, self.input_file))

        num_seqs, input_files = self.split_input_file()

        if not self.silent:
            print('{0:,} sequences successfully split into {1} pieces'.format(num_seqs, len(input_files)))
            print('Starting process pool using {0} processors'.format(self.num_procs))

        output = self.run_pool(input_files, num_seqs)

        if not self.silent:
            end = time.time()
            total_time = round(end - start, 2)
            seqs_per_sec = int(num_seqs / total_time)
            print('{0:,} sequences processed in {1:,} seconds, {2:,} sequences / s'.format(num_seqs, total_time, seqs_per_sec))

        if not output:
            print('Error: No output')
            return None
        elif self.args['outfmt'] in ['lsjson', 'json', 'tsv']:
            self.concat_files(output, self.output_file)

            if not self.debug:
                shutil.rmtree(self.tmp_dir)

            if self.gzip_output:
                if not self.silent:
                    print("Zipping up final output")
                subprocess.check_call(['gzip', '-f', self.output_file])

                if not self.silent:
                    print("Analysis complete, result file: {0}.gz".format(self.output_file))
                return os.path.join(os.getcwd(), self.output_file + '.gz')
            else:
                if not self.silent:
                    print("Analysis complete, result file: {0}".format(self.output_file))
                return os.path.join(os.getcwd(), self.output_file)
        elif self.args['outfmt'] in ['dict']:
            if not self.silent:
                print("Analysis complete, returning dictionary")
            return {key: val for d in output for key, val in d.items()}

    def get_chunk_size(self):
        """Takes input file and uses file size to determine optimal chunk size."""
        input_file_size = os.stat(self.input_file).st_size
        if self.input_type == 'fasta':
            return min(int((0.0000012360827411141800 * input_file_size) + 44.6), MAX_CHUNK_SIZE)
        elif self.input_type == 'fastq':
            return min(int((0.0000006180413705570910 * input_file_size) + 44.6), MAX_CHUNK_SIZE)

    def split_input_file(self):
        num_seqs = 0
        pieces = []

        if self.input_type == 'fasta':
            index = 0
            lines = 0
            fout = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False, dir=self.tmp_dir)
            pieces.append(fout)

            with open(self.input_file, 'r') as fin:
                seq = ''
                line = fin.readline()
                while line:
                    if line.startswith('>'):
                        if seq:
                            fout.write(seq + '\n')
                            seq = ''
                            num_seqs += 1

                        fout.write(line)
                    else:
                        seq += line.strip()

                    if lines/2 // self.chunk_size > index:
                        line = fin.readline()
                        while line and not line.startswith('>'):
                            lines += 1
                            seq += line.strip()
                            line = fin.readline()

                        fout.write(seq + '\n')
                        num_seqs += 1
                        fout.close()

                        fout = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False, dir=self.tmp_dir)
                        pieces.append(fout)
                        index += 1
                        seq = ''
                    else:
                        lines += 1
                        line = fin.readline()

            fout.write(seq)
            num_seqs += 1
            fout.close()
            return [num_seqs, pieces]
        elif self.input_type == 'fastq':
            index = 0
            lines = 0

            fout_fasta = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False, dir=self.tmp_dir)
            fout = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False, dir=self.tmp_dir)
            pieces.append((fout_fasta, fout))

            with open(self.input_file, 'r') as fin:
                line = fin.readline()
                lines += 1
                while line:
                    if line.startswith('@'):
                        header = line[1:].strip().replace(' ','')

                        fout_fasta.write('>' + header + '\n')
                        fout.write('@' + header + '\n')

                        seqline = fin.readline()
                        fout_fasta.write(seqline)
                        fout.write(seqline)
                        fout.write(fin.readline())
                        fout.write(fin.readline())

                        lines += 1

                        if lines/2 // self.chunk_size > index:
                            fout_fasta.close()
                            fout_fasta = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False,
                                                                     dir=self.tmp_dir)
                            fout.close()
                            fout = tempfile.NamedTemporaryFile(mode='w', prefix='pyir_', delete=False,
                                                                        dir=self.tmp_dir)
                            pieces.append((fout_fasta, fout))

                            index += 1

                        line = fin.readline()
                        lines += 1
                        num_seqs += 1

            fout_fasta.close()
            fout.close()
            return [num_seqs, pieces]

    def run_pool(self, input_files, total_seqs):
        """Creates a multiprocessing pool and runs all o"""
        output_files = []
        with multiprocessing.Pool(processes=self.num_procs) as p:
            func = functools.partial(igblast.run, self.args)

            results = []

            if self.input_type == 'fasta':
                pool_results = p.imap_unordered(func, [x.name for x in input_files])
            elif self.input_type == 'fastq':
                pool_results = p.imap_unordered(func, [(x[0].name, x[1].name) for x in input_files])

            if not self.silent:
                with tqdm.tqdm(total=total_seqs, unit='seq') as pbar:
                    for x in pool_results:
                        if x[0]:
                            pbar.update(x[1])
                            results.append(x)
                    pbar.close()
            else:
                for x in pool_results:
                    results.append(x)

            total_passed = 0
            for result in results:
                output_files.append(result[0])
                total_passed += result[3]

            if self.use_filter:
                if not self.silent:
                    print(total_passed, "Passed filtering")

        return output_files

    def concat_files(self, list_of_files, outfile):
        """Concatenate a list of files"""
        with open(outfile, 'w') as fout:
            if self.args['outfmt'] == 'lsjson':
                concat_cmd = ['cat'] + list_of_files
                subprocess.run(concat_cmd, stdout=fout)
            elif self.args['outfmt'] == 'json':
                fout.write('[\n')
                for f in list_of_files:
                    with open(f, 'r') as filein:
                        for line in filein:
                            fout.write(line)
                fout.seek(fout.tell()-2, 0)
                fout.write('\n]\n')
            elif self.args['outfmt'] == 'tsv':
                fout.write('\t'.join(self.outkeys) + '\n')
                for f in list_of_files:
                    with open(f, 'r') as filein:
                        for line in filein:
                            fout.write(line)