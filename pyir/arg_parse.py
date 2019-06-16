#!/usr/bin/env python
import argparse
import Bio.SeqIO
import glob
import multiprocessing
import os
import pkg_resources
import subprocess

class PyIrArgumentParser():

    def __init__(self, is_api=False):

        self.arg_parse = argparse.ArgumentParser(
            prog="pyir",
            description='''\
                A Python wrapper for IgBLAST that scales to allow for the parallel processing of millions of reads on shared memory computers. All output is stored in a convenient JSON format.
                \nAuthors - Andre Branchizio, Jordan Willis, Jessica Finn
        ''')

        necessary_arguments = self.arg_parse.add_argument_group(
            title="Necessary Arguments",
            description="Arguments that must be included"
        )

        if not is_api:
            necessary_arguments.add_argument(
                'query',
                type=argparse.FileType('r'), metavar="query.fasta",
                help='The fasta or fastq file to be run through the protocol'
            )

        type_arguments = self.arg_parse.add_argument_group(
            title="File paths and types",
            description="Database paths, search types"
        )

        if not is_api:
            type_arguments.add_argument(
                '-d',
                '--database',
                type=str,
                help="Path to your blast database directory",
                required=True
            )

        type_arguments.add_argument(
            '-r',
            '--receptor',
            default="Ig",
            choices=["Ig", "TCR"],
            help="The receptor you are analyzing, immunoglobulin or t cell receptor"
        )

        type_arguments.add_argument(
            '-s',
            '--species',
            default='human',
            choices=['human', 'mouse'],
            help='The Species you are analyzing'
        )

        blast_arguments = self.arg_parse.add_argument_group(
            title="BLAST Specific Arguments",
            description="Arguments Specific to IgBlast"
        )

        blast_arguments.add_argument(
            "-nV",
            "--num_V_alignments",
            default="3",
            type=str,
            help="How many V genes do you want to match?"
        )

        blast_arguments.add_argument(
            "-nD",
            "--num_D_alignments",
            default="3",
            type=str,
            help="How many D genes do you want to match?, does not apply for kappa and lambda"
        )

        blast_arguments.add_argument(
            "-nJ",
            "--num_J_alignments",
            default="3",
            type=str,
            help="How many J genes do you want to match?"
        )

        blast_arguments.add_argument(
            '-mD',
            "--minD",
            type=self._check_d_match_validity,
            default="5",
            help="The amount of nucleotide matches needed for a D gene match. >= 5 right now"
        )

        blast_arguments.add_argument(
            "-word_size", 
            type=int,
            default=9,
            help="The word length that is going to be provded to igblast"

        )

        type_arguments.add_argument(
            '-cz',
            '--chunk_size',
            type=int,
            help="How many sequences to work on at once. The higher the number the more memory needed. If none specified chunk size will be determined based on input file size",
            default=None
        )

        blast_arguments.add_argument(
            "-x",
            '--executable',
            default= self.get_igblast(),
            type=str,
            help="The location of IGBlastn binary, the default location is determined based on the OS and uses the igblast binaries included in this application."
        )

        general_args = self.arg_parse.add_argument_group(
            title="General Arguments",
            description="Output and Miscellaneous Arguments"
        )

        general_args.add_argument(
            "-m",
            "--multi",
            default=multiprocessing.cpu_count(),
            type=int,
            help="Multiprocess by the amount of CPUs you have. Or you can enter a number or type 0 to turn it off"
        )

        general_args.add_argument(
            "-o",
            "--out",
            metavar="inputfile.json.gz",
            help="Output_file_name, defaults to inputfile.json.gz"
        )

        general_args.add_argument(
            "--debug",
            default=False,
            action="store_true",
            help="Debug mode, this will not delete the temporary blast files and will print some other useful things, like which regions did not parse"
        )

        general_args.add_argument(
            '--additional_field',
            type=self._additional_field_parse,
            help="A comma key,value pair for an additional field you want to add to the output json. Example \n '--additional_field=donor,10` adds a donor field with value 10."
        )

        general_args.add_argument(
            "-f",
            "--out-format",
            choices=['json'],
            default="json",
            metavar="json",
            help="Output file format, only json currently supported"
        )

        general_args.add_argument(
            "--pretty",
            action='store_true',
            help="Pretty json output"
        )

        general_args.add_argument(
            "--silent",
            action='store_true',
            help="Silence stdout"
        )

    def parse_arguments(self, overrides = None):

        arguments = self.arg_parse.parse_args()

        if overrides != None:
            for key in overrides:
                setattr(arguments, key, overrides[key])

        self._validate_path(arguments.database)
        self._validate_executable(arguments.executable)
        return arguments.__dict__

    def _check_d_match_validity(self, amount):

        if int(amount) >= 5:
            return str(amount)
        raise argparse.ArgumentTypeError("The amount of D gene nucleotide matches must be >= 5, you have entered {0}".format(str(amount)))

    def _validate_fasta(self, text):

        try:
            Bio.SeqIO.parse(text, 'fasta').next()
            return text
        except StopIteration:
            raise argparse.ArgumentTypeError("{0} is not fasta file".format(text))

    def _validate_path(self, path):

        if os.path.exists(os.path.abspath(path)):
            os.environ['IGDATA'] = os.path.abspath(path)
            return os.path.abspath(path)
        raise argparse.ArgumentTypeError("{0} does not exist. Did you use setup.py correctly? Or do you have another location?".format(path))

    def _validate_executable(self, path):

        if os.path.exists(os.path.abspath(path)):
            return os.path.abspath(path)
        raise argparse.ArgumentTypeError("{0} does not exists, please point to where igblastn is".format(path))

    def _additional_field_parse(self, keyvaluestring):
        '''I don't know what an exception will be, but have to have some kind of error checking '''
        try:
            keyvalue_split = keyvaluestring.split(',')
            return (keyvalue_split[0], keyvalue_split[1])
        except:
            raise argparse.ArgumentTypeError("comma seperated error with {0}".format(keyvaluestring))

    def get_data_dir(self):

        return pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data_dir")

    def get_igblast(self):

        igblast_dir = pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/igblast")
        igblasts = glob.glob(igblast_dir + '/igblastn_*')

        for binary in igblasts:
            try:
                import stat
                os.chmod(binary, stat.S_IEXEC)
            except:
                pass
            try:
                subprocess.check_call([binary, '-h'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return os.path.abspath(binary)
            except:
                continue
            return ""
