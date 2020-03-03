#!/usr/bin/env python
import argparse
import multiprocessing
import sys
import os
import pkg_resources
import subprocess
import tempfile


class PyIrArgumentParser():
    """This class parses the command line arguments"""

    def __init__(self):
        """Return class

        Initializes all arguments for PyIR by category"""
        self.arg_parse = argparse.ArgumentParser(
            prog="pyir",
            description='''\
                A Python wrapper for IgBLAST that scales to allow for the parallel processing of millions of reads
                 on shared memory computers. All output is stored in a convenient JSON format.
                \nAuthors - Andre Branchizio, Jordan Willis, Jessica Finn, Sam Day
        ''')

        necessary_arguments = self.arg_parse.add_argument_group(
            title="Required Arguments"
        )

        necessary_arguments.add_argument(
            'query',
            metavar="query.fasta",
            help='The fasta or fastq file to be run through the protocol'
        )

        general_args = self.arg_parse.add_argument_group(
            title="General PyIR-Specific Arguments"
        )

        general_args.add_argument(
            '-t',
            '--input_type',
            dest='input_type',
            choices=['fasta', 'fastq'],
            help='Type of file to process. Default is inferred from the file extension ()'
        )

        general_args.add_argument(
            "-m",
            "--multi",
            dest='multi',
            default=multiprocessing.cpu_count(),
            type=int,
            help="Number of threads to process with. Default is as many cores are available (" + str(
                multiprocessing.cpu_count()) + ")"
        )

        general_args.add_argument(
            "-o",
            "--out",
            dest='out',
            metavar="inputfile.json.gz",
            help="Output_file_name, defaults to inputfile.json.gz"
        )

        general_args.add_argument(
            '--outfmt',
            dest='outfmt',
            choices={'lsjson', 'json', 'tsv', 'dict'},
            default='lsjson',
            help='Output format. Default is a line-separated JSON file, where each line contains an individual JSON '
                 'object. \'json\' format outputs a file in true JSON format, where the top-level object is an array '
                 'that contains each sequence with analysis as a JSON object. \'dict\' format only available in API '
                 'mode and uses significantly more memory'
        )

        general_args.add_argument(
            '-z',
            '--gzip',
            dest='gzip',
            type=self._check_bool,
            default=True,
            help="Gzip output file"
        )

        general_args.add_argument(
            "--debug",
            default=False,
            action="store_true",
            help="Debug mode. Keep's the temporary chunk files and prints additional output"
        )

        general_args.add_argument(
            "--pretty",
            action='store_true',
            default=False,
            help="Pretty json output"
        )

        general_args.add_argument(
            "--silent",
            action='store_true',
            default=False,
            help="Silence stdout output"
        )

        general_args.add_argument(
            '-cz',
            '--chunk_size',
            dest='chunk_size',
            type=int,
            help="How many sequences per chunk. This affects the number of chunks the input file is divided into as "
                 "well as how often progress gets updated. Ideal size varies from system to system and number of "
                 "sequences being processed. Default chunk size determined by file size at runtime. Advanced users "
                 "editing this flag with large input files should be wary of running into OS file pointer limits and "
                 "similar errors.",
        )

        general_args.add_argument(
            '--legacy',
            dest='legacy',
            default=False,
            help='Legacy parsing & formatting. PyIR has a history that precedes the widespread adoption of AIRR'
                 'formatting standards so the original parsing algorithm and fields are preserved under this flag.'
                 'WARNING: These fields are deprecated and will be unsupported at a later date, use at your own risk',
            action='store_true'
        )

        path_arguments = self.arg_parse.add_argument_group(
            title="Arguments related to file paths"
        )

        path_arguments.add_argument(
            '--igdata',
            type=str,
            dest='igdata',
            help="Path to your IGDATA directory. Default is " + self._get_igdata_dir(),
            default=self._get_igdata_dir(),
        )

        path_arguments.add_argument(
            "-x",
            '--executable',
            dest='executable',
            default=self.get_igblast(),
            type=str,
            help="The location of IgBlast binaries. Default is " + self.get_igblast()
        )

        path_arguments.add_argument(
            "--tmp_dir",
            dest='tmp_dir',
            default=tempfile.gettempdir(),
            help="Directory to keep temporary files. Default is " + tempfile.gettempdir()
        )

        data_arguments = self.arg_parse.add_argument_group(
            title="Input Data arguments"
        )

        data_arguments.add_argument(
            '-r',
            '--receptor',
            dest='receptor',
            default="Ig",
            choices=["Ig", "TCR"],
            help="The receptor you are analyzing, immunoglobulin or t cell receptor"
        )

        data_arguments.add_argument(
            '-s',
            '--species',
            dest='species',
            default='human',
            # choices=['human', 'mouse', 'rabbit', 'rat', 'rhesus_monkey'],
            choices=['human'],
            help='The Species you are analyzing'
        )

        data_arguments.add_argument(
            '--additional_field',
            type=self._additional_field_parse,
            help="A comma key,value pair for an additional field you want to add to the output json. Example \n "
                 "'--additional_field=donor,10' adds the field 'donor' with value 10."
        )

        blast_arguments = self.arg_parse.add_argument_group(
            title="IgBLAST Arguments",
            description="Arguments Specific to IgBlast"
        )

        blast_arguments.add_argument(
            '--aux',
            type=str,
            dest='aux',
            help="Path to your BLAST aux_data directory.",
            default=self._get_aux_dir(),
        )

        blast_arguments.add_argument(
            '--germlineV',
            type=str,
            dest='germlineV',
            help='Path to germline_db_V database for IgBLAST. Default value is derived from the IGDATA environment '
                 'variable.'
        )

        blast_arguments.add_argument(
            '--germlineD',
            type=str,
            dest='germlineD',
            help='Path to germline_db_D database for IgBLAST. Default value is derived from the IGDATA environment '
                 'variable.'
        )

        blast_arguments.add_argument(
            '--germlineJ',
            type=str,
            dest='germlineJ',
            help='Path to germline_db_J database for IgBLAST. Default value is derived from the IGDATA environment '
                 'variable.'
        )

        blast_arguments.add_argument(
            "-nV",
            "--numV",
            dest='num_V_alignments',
            default="3",
            type=str,
            help="Number of top V gene matches in output. Default is 3. "
                 "**DEPRECATED -- legacy field that will be removed"
        )

        blast_arguments.add_argument(
            "-nD",
            "--numD",
            dest='num_D_alignments',
            default="3",
            type=str,
            help="Number of top D gene matches in output. Default is 3. "
                 "**DEPRECATED -- legacy field that will be removed"
        )

        blast_arguments.add_argument(
            "-nJ",
            "--numJ",
            dest='num_J_alignments',
            default="3",
            type=str,
            help="Number of top J gene matches in output. Default is 3. "
                 "**DEPRECATED -- legacy field that will be removed"
        )

        blast_arguments.add_argument(
            '-mD',
            "--minD",
            dest='minD',
            type=self._check_d_match_validity,
            default="5",
            help="The minimum amount of nucleotide matches needed for a D gene match. Default is 5"
        )

        blast_arguments.add_argument(
            '-wS',
            "--word_size",
            dest='word_size',
            type=str,
            default="11",
            help="The Igblast word size to use. Default is 11"
        )

        filter_args = self.arg_parse.add_argument_group(
            title="Filtering Specific Arguments",
            description="Arguments to enable and control filtering on BLAST results"
        )

        filter_args.add_argument(
            '--enable_filter',
            action='store_true',
            help="Turns on data filtering",
            default=False
        )

        filter_args.add_argument(
            '--filter_v_evalue',
            type=float,
            help='maximum e-value for valid V germline matches',
            default=0.000001
        )

        filter_args.add_argument(
            '--filter_j_evalue',
            type=float,
            help='maximum e-value for valid J germline matches',
            default=0.000001
        )

        filter_args.add_argument(
            '--filter_productive',
            type=self._check_bool,
            help='Whether to filter on the productive flag from IgBLAST',
            default=True
        )

        filter_args.add_argument(
            '--filter_stop_codon',
            type=self._check_bool,
            help='Whether to filter on the stop_codon flag from IgBLAST',
            default=True
        )

        filter_args.add_argument(
            '--filter_vjframe',
            type=self._check_bool,
            help='Whether to filter on V-J being in-frame',
            default=True
        )

        filter_args.add_argument(
            '--filter_aa_strings',
            type=self._check_bool,
            help='Whether to filter out sequences that transpose to * and/or are missing the canonical WG|FG after'
                 'CDR3 in AA string',
            default=True
        )

        filter_args.add_argument(
            '--filter_nt_strings',
            type=self._check_bool,
            help='Whether to filter out sequences with \'N\' in sequence_alignment field',
            default=True
        )

        filter_args.add_argument(
            '--filter_cdr3_length',
            type=str,
            help='A minimum and maximum length for the CDR3 AA region, separated by a comma. Default: 3,50',
            default="3,50"
        )

        filter_args.add_argument(
            '--filter_cdr3_quality',
            type=float,
            help='Minimum Phred score allowed in CDR3 region (fastq files in legacy mode only)',
            default=30
        )

        filter_args.add_argument(
            '--filter_fr3_c_codon',
            type=self._check_bool,
            help='Whether to filter out sequences that are missing a \'C\' codon in the last 3 proteins of the AA string',
            default=True
        )

    def parse_arguments(self, overrides=None):
        """Returns dict

        Main function for parsing arguments"""
        arguments = self.arg_parse.parse_args(overrides)

        os.environ['IGDATA'] = arguments.igdata
        self._set_germline_databases(arguments)
        self._validate_executable(arguments.executable)
        if not arguments.input_type:
            if '.fastq' in arguments.query:
                arguments.input_type = 'fastq'
            elif '.fasta' in arguments.query or arguments.query.endswith('.fa'):
                arguments.input_type = 'fasta'
            else:
                if not arguments.silent:
                    print('Warning: Input type unable to be inferred, defaulting to fasta')
                arguments.input_type = 'fasta'

        return arguments.__dict__

    @staticmethod
    def _check_d_match_validity(amount):
        """Checks that the D gene nucleotide matches argument is valid"""
        if int(amount) >= 5:
            return str(amount)
        raise argparse.ArgumentTypeError(
            "The amount of D gene nucleotide matches must be >= 5, you have entered {0}".format(str(amount)))

    @staticmethod
    def _validate_path(path):
        """Checks that the given IGDATA path exists"""
        if os.path.exists(os.path.abspath(path)):
            os.environ['IGDATA'] = os.path.abspath(path)
            return os.path.abspath(path)
        raise argparse.ArgumentTypeError("{0} does not exist. Did you use setup.py correctly? Or do you have another location?".format(path))

    @staticmethod
    def _validate_executable(path):
        """Checks that the given igblast executable folder exists"""
        if path and os.path.exists(os.path.abspath(path)):
            return os.path.abspath(path)
        raise argparse.ArgumentTypeError("{0} does not exists, please point to where igblastn is".format(path))

    @staticmethod
    def _additional_field_parse(keyvaluestring):
        """Checks that the given keyvaluestring is formatted correctly"""
        # I don't know what an exception will be, but have to have some kind of error checking
        try:
            keyvalue_split = keyvaluestring.split(',')
            return (keyvalue_split[0], keyvalue_split[1])
        except:
            raise argparse.ArgumentTypeError("comma separated error with {0}".format(keyvaluestring))

    @staticmethod
    def _get_igdata_dir():
        if os.path.exists(pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/germlines")):
            return pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/germlines")
        elif 'IGDATA' in os.environ:
            return os.environ['IGDATA']
        else:
            raise argparse.ArgumentTypeError("Missing IGDATA environment variable")

    @staticmethod
    def test_igblast(path):
        try:
            subprocess.check_call([path, '-h'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return path
        except:
            print('Error with igblast:')
            subprocess.call([path, '-h'])
            sys.exit()

    def get_igblast(self):
        """Checks that the given IGBlast executable exists"""
        igblast_dir = pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"), "pyir/data/bin")
        if 'linux' in sys.platform:
            return self.test_igblast(os.path.join(igblast_dir,'igblastn_linux'))
        elif 'darwin' in sys.platform:
            return self.test_igblast(os.path.join(igblast_dir,'igblastn_darwin'))
        else:
            print('No IGBlast found for platform: {0} -- exiting...'.format(sys.platform))
            return None

    @staticmethod
    def _get_aux_dir():
        """Checks that the given PyIR aux_data directory exists"""
        if not os.path.exists(
                pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"),
                                                "pyir/data/germlines/aux_data")):
            raise ValueError("No aux directory found:", pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"),
                                                "pyir/data/germlines/aux_data"))
        else:
            return pkg_resources.resource_filename(pkg_resources.Requirement.parse("pyir"),
                                                   "pyir/data/germlines/aux_data")

    @staticmethod
    def _check_bool(val):
        if isinstance(val, bool):
            return val

        if val.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif val.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            return None

    @staticmethod
    def _set_germline_databases(args):
        pathbase = os.path.join(args.igdata, args.receptor, args.species)

        suffix = 'TCR' if args.receptor == 'TCR' else 'gl'
        if not args.germlineV:
            args.germlineV = os.path.join(pathbase, args.species + '_' + suffix + '_V')
        if not args.germlineD:
            args.germlineD = os.path.join(pathbase, args.species + '_' + suffix + '_D')
        if not args.germlineJ:
            args.germlineJ = os.path.join(pathbase, args.species + '_' + suffix + '_J')