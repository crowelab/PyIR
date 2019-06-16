import os
import pyir.parsers
import subprocess
import tempfile
import Bio.SeqIO
import signal
import time

def run(args, input_file_map):

    igblast_run = IgBlastRun(args)

    fasta_input_file = input_file_map['fasta']

    if args['input_format'] == 'fastq':
        fastq_input_file = input_file_map['fastq']
    else:
        fastq_input_file = None

    return igblast_run.run_single_process(fasta_input_file, fastq_input_file)

class IgBlastRun():

    '''
    IgBlast single run is the class to call for a single IgBlast subprocess.
    This class is the most handy for multiprocessing but can be called alone
    for a single fasta file.

    Examples:

    --Constructor:

    Ig_sr = IgBlast_SingleRun(argument_dictionary, query_file)

    --Set the fasta file to be parsed. Not constant like the argument dictionary

    --Run the process. Takes in single queue object. This is where the process will
    dump the output file

    Ig_sr.run_single_process(QueueObject)
    '''

    def __init__(self, arg_dict):
        '''
        Constructor takes argument dictionary and sequence dictionary
        '''

        self.args = arg_dict
        # Set sequence dictionary to member
        # Debug mode - Bool
        self.debug = arg_dict['debug']

        # Fetch Argument Dictionary Values
        # IgBlast Specific
        self.executable = arg_dict['executable']
        self.minD = arg_dict['minD']
        self.numV = arg_dict['num_V_alignments']
        self.numD = arg_dict['num_D_alignments']
        self.numJ = arg_dict['num_J_alignments']
        self.num_procs = arg_dict['multi']
        self.species = arg_dict['species']
        self.receptor = arg_dict['receptor']
        self.igblast_out = tempfile.NamedTemporaryFile(suffix='.blast_out', delete=False).name
        self.wordSize = arg_dict['word_size']

        # First fetch the path to our data directory
        _path_to_data_base = os.path.join(os.environ['IGDATA'], self.receptor, self.species)

        suffix = 'TCR' if self.receptor == 'TCR' else 'gl'
        self.germline_v = os.path.join(_path_to_data_base, self.species + "_" + suffix + "_V")
        self.germline_d = os.path.join(_path_to_data_base, self.species + "_" + suffix + "_D")
        self.germline_j = os.path.join(_path_to_data_base, self.species + "_" + suffix + "_J")
        self.auxilary_path = os.path.join(os.environ['IGDATA'], "aux", self.species + "_gl.aux")

        # Igblast specific but user can't change without hardcoding
        self.outfmt = "3"
        self.domain_system = "imgt"

        self.out_format = arg_dict['out_format']

    def get_seqs_dict(self, input_file):

        return Bio.SeqIO.to_dict(Bio.SeqIO.parse(input_file, self.args['input_format']))

    def _collect(self):
        '''Collect all blast arguments and put them in one list accessible by subproces.Popen'''

        return [
            self.executable,
            '-min_D_match', self.minD,
            '-num_alignments_V', self.numV,
            '-num_alignments_D', self.numD,
            '-num_alignments_J', self.numJ,
            '-organism', self.species,
            '-ig_seqtype', self.receptor,
            '-germline_db_V', self.germline_v,
            '-germline_db_D', self.germline_d,
            '-germline_db_J', self.germline_j,
            '-auxiliary_data', self.auxilary_path,
            '-outfmt', self.outfmt,
            '-domain_system', self.domain_system,
            '-out', self.igblast_out,
            '-query', self.query,
            '-word_size', str(self.wordSize),
            '-gapopen', '5',
            '-gapextend', '2',
            '-evalue', '1000000.0',
            '-num_alignments', '1',
            '-num_descriptions', '1',
            '-penalty', '-1',
            '-reward', '1',
            '-num_threads', '1',
            '-show_translation'
        ]

    def signal_handler(self, signum, frame):
        raise RuntimeError("Parent process failure")

    def run_single_process(self, input_file, fastq_input_file):

        self.query = input_file

        if self.args['input_format'] == 'fastq':
            self.seqs = self.get_seqs_dict(fastq_input_file)
        else:
            self.seqs = self.get_seqs_dict(input_file)

        collectedArgs = self._collect()

        # make sure this process is terminated on keyboard interrupt
        signal.signal(signal.SIGINT, self.signal_handler)

        p = subprocess.Popen(collectedArgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stderr = p.communicate()

        if stderr[1]:
            print("Error in calling Igblastn:\n\n {0}".format(stderr[1]))

        # until process is done until it moves on to the next line
        p.wait()

        output_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False, dir=self.args['tmp_dir']).name

        parser = pyir.parsers.IgBlastParser(self.args, self.seqs, self.igblast_out, output_file)
        total_parsed = parser.parse()

        os.remove(self.igblast_out)

        time.sleep(.1)

        return output_file, total_parsed, input_file
