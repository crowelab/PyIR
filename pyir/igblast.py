import os
from . import parsers
import tempfile
import signal


def run(args, input_file):
    igblast_run = IgBlastRun(args)
    return igblast_run.run_single_process(input_file)


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

    def __init__(self, args):
        '''
        Constructor takes argument dictionary and sequence dictionary
        '''

        self.args = args

        self.legacy = args['legacy']
        self.debug = args['debug']
        self.tmp_dir = args['tmp_dir']
        self.blast_outfmt = '3' if args['legacy'] else '19'

        # Collect IgBLAST variables and prepare for
        # _path_to_data_base = os.path.join(args['database'], args['receptor'], args['species'])
        # suffix = 'TCR' if args['receptor'] == 'TCR' else 'gl'
        self.collected_args = [
            args['executable'],
            '-min_D_match', args['minD'],
            '-num_alignments_V', args['num_V_alignments'],
            '-num_alignments_D', args['num_D_alignments'],
            '-num_alignments_J', args['num_J_alignments'],
            '-organism', args['species'],
            '-ig_seqtype', args['receptor'],
            '-germline_db_V', args['germlineV'],
            '-germline_db_D', args['germlineD'],
            '-germline_db_J', args['germlineJ'],
            '-auxiliary_data', os.path.join(args['aux'], args['species'] + '_gl.aux'),
            '-outfmt', self.blast_outfmt,
            '-domain_system', 'imgt',
            '-word_size', args['word_size'],
            '-gapopen', '5',
            '-gapextend', '2',
            '-num_alignments', '1',
            '-num_descriptions', '1',
            # '-penalty', '-1',
            # '-reward', '1',
            '-num_threads', '1',
            '-show_translation',
            '-extend_align5end',
            '-query']

        self.input_type = args['input_type']

        # self.use_memory = args['use_mem']
        self.use_filter = args['enable_filter']

        # Internal use variables
        self.query = None
        self.seqs = None

    def get_seqs_dict(self, input_file):
        retval = {}

        if self.input_type == 'fasta':
            with open(input_file, 'r') as fin:
                seq = ''
                id = ''
                for line in fin:
                    if line.startswith('>'):
                        if seq:
                            retval[id] = {'seq': seq}
                            seq = ''
                        id = line[1:].strip('\n').strip()
                    else:
                        seq += line.strip()

                if id:
                    retval[id] = {'seq': seq}

            return retval
        elif self.input_type == 'fastq':
            with open(input_file[1], 'r') as fin:
                line = fin.readline()
                while line:
                    id = line[1:].strip()
                    seq = fin.readline().strip()
                    fin.readline()
                    quality_scores = fin.readline().strip()
                    retval[id] = {
                        'seq': seq,
                        'quality_scores': quality_scores
                    }
                    line = fin.readline()

            return retval

    def signal_handler(self, signum, frame):
        raise RuntimeError("Parent process failure")

    def run_single_process(self, input_file):
        if self.input_type == 'fasta':
            query = input_file
        else:
            query = input_file[0]

        output_file = tempfile.NamedTemporaryFile(prefix='pyir_', suffix=".json", delete=False, dir=self.tmp_dir).name
        if self.legacy:
            seqs = self.get_seqs_dict(input_file)
            parser = parsers.LegacyParser(seqs, output_file, self.args)
        else:
            parser = parsers.AirrParser(output_file, self.args)

        collected_args = self.collected_args[:]
        collected_args.append(query)

        # make sure this process is terminated on keyboard interrupt
        signal.signal(signal.SIGINT, self.signal_handler)

        parser.parse(collected_args)

        if self.args['outfmt'] == 'dict':
            return parser.out_d, parser.total_parsed, input_file, parser.total_passed
        else:
            return output_file, parser.total_parsed, input_file, parser.total_passed
