from abc import ABCMeta, abstractmethod
import collections
import json
import re
from . import filters
import subprocess

REVERSE_COMPLEMENT = {
    'A': 'T',
    'C': 'G',
    'G': 'C',
    'T': 'A'
}

IGBLAST_TSV_HEADER = ['sequence_id','sequence','locus','stop_codon','vj_in_frame','productive','rev_comp','complete_vdj','v_call','d_call','j_call','sequence_alignment','germline_alignment','sequence_alignment_aa','germline_alignment_aa','v_alignment_start','v_alignment_end','d_alignment_start','d_alignment_end','j_alignment_start','j_alignment_end','v_sequence_alignment','v_sequence_alignment_aa','v_germline_alignment','v_germline_alignment_aa','d_sequence_alignment','d_sequence_alignment_aa','d_germline_alignment','d_germline_alignment_aa','j_sequence_alignment','j_sequence_alignment_aa','j_germline_alignment','j_germline_alignment_aa','fwr1','fwr1_aa','cdr1','cdr1_aa','fwr2','fwr2_aa','cdr2','cdr2_aa','fwr3','fwr3_aa','fwr4','fwr4_aa','cdr3','cdr3_aa','junction','junction_length','junction_aa','junction_aa_length','v_score','d_score','j_score','v_cigar','d_cigar','j_cigar','v_support','d_support','j_support','v_identity','d_identity','j_identity','v_sequence_start','v_sequence_end','v_germline_start','v_germline_end','d_sequence_start','d_sequence_end','d_germline_start','d_germline_end','j_sequence_start','j_sequence_end','j_germline_start','j_germline_end','fwr1_start','fwr1_end','cdr1_start','cdr1_end','fwr2_start','fwr2_end','cdr2_start','cdr2_end','fwr3_start','fwr3_end','fwr4_start','fwr4_end','cdr3_start','cdr3_end','np1','np1_length','np2','np2_length']

class BaseParser:
    """Parsing super class used by parsers below.

    The basic workflow of each parser class is as follows:
    1. Create a regex to match the parser on. There are generally 2 types of lines to match: header lines, and
    information lines.
    2. When parse method is called, read current line of IgBLAST output. If matching on a header line, activate the
    'triggered' boolean and wait for further input to process. Otherwise, incorporate matching fields into the regex
    and process the line immediately when matched.
    3. Process the information in each line and save to the out_d object passed in the parse method
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, line, out_d):
        """The parse method is what handles each line and processes it.

        Each parser should return the following values from the parse method for the
        parsing algorithm to work correctly:
        - 'out_d' if matched or triggered, with the appropriate values in out_d updated
        - 'False' or 'None' if the current line doesn't match or trigger, but there are no errors

        If there is an irreconcilable error parsing and you want to indicate that the parser should move on to the next
        query, then the parse method should raise an exception (e.g. raising a FilterException when the current line
        doesn't pass the filter)
        """
        pass


class QueryParser(BaseParser):
    """Parses out basic query and sequence information

    This parser is responsible for the 'Sequence ID', 'Raw Sequence', and 'Sequence Length' fields"""
    def __init__(self, seq_dict):
        # self.args = args
        self.required = True
        self.regex = re.compile('^Query= ((\S| )*)')
        self.seq_dict = seq_dict

    def parse(self, line, out_d):
        matches = re.match(self.regex, line)
        if matches:
            out_d['Sequence ID'] = matches.group(1)

            try:
                out_d['Raw Sequence'] = self.seq_dict[out_d['Sequence ID']]['seq'].upper()
                # These are legacy fields I'm hard-coding or interpolating to save parser cycles.
                # Worth re-evaluating these in a future update
                out_d['Sequence Length'] = len(out_d['Raw Sequence'])
                out_d['Domain Classification'] = 'imgt'
            except KeyError as e:
                pass

            return out_d
        else:
            return False


class SignificantAlignmentParser(BaseParser):
    """Parses out information about each hit and alignment for significant matches

    This parser is responsible for the 'Hits' field along with its' subfields"""
    def __init__(self):
        self.required = True
        self.failure_regex = re.compile('^.+No hits found.+$')
        self.trigger_regex = re.compile('^Sequences producing significant alignments')
        self.hit_regex = re.compile('(.*?)[ ]+([0-9.\-e]+)[ ]+([0-9.\-e]+)')
        self.halt_regex = re.compile('^Domain classification requested')
        self.hits = []
        self.triggered = False

    # When triggered, parser will switch to matching on 'hit_regex' instead of 'trigger_regex' so that it parses
    # the 'Hits' fields correctly and stores the data
    def parse(self, line, out_d):
        disable_trigger = re.match(self.halt_regex, line)
        if disable_trigger:
            self.triggered = False
            out_d['Hits'] = self.hits
            self.hits = []
            return out_d

        if self.triggered:
            matches = re.match(self.hit_regex, line)
            self.hits.append({'gene': matches.group(1),
                              'bit_score': float(matches.group(2)),
                              'e_value': float(matches.group(3))})
            return out_d

        matches = re.match(self.trigger_regex, line)
        if matches:
            self.triggered = True
            return out_d

        if re.match(self.failure_regex, line):
            out_d['Hits'] = []
            out_d['Message'] = line.strip()
            return out_d

        return False


class VDJSummaryParser(BaseParser):
    """Parses out VDJ summary information

    This parser is responsible for the 'Top V gene match', 'Top D gene match', 'Top J gene match',
    'V family', 'J family', 'D family', 'Top V gene e_value', 'Top D gene e_value', and 'Top J gene e_value'
    fields as well as overall informational fields 'Chain type', 'stop codon', 'V-J frame', and 'Strand'"""
    def __init__(self):
        self.regex = re.compile('^V-\(D\)-J rearrangement summary for query sequence \((.*)\)\.')
        self.required = True
        self.triggered = False
        self.fields = None

    def parse(self, line, out_d):
        if self.triggered:
            item_d = dict(zip(self.fields, line.strip().split('\t')))

            for key, val in item_d.items():
                stripped_key = key.strip()
                value = val.split(',')[0]
                out_d[stripped_key] = value

                if stripped_key == 'Top V gene match':
                    self.set_family('V family', value, out_d)
                    for hit in out_d['Hits']:
                        if hit['gene'] == value:
                            out_d['Top V gene e_value'] = hit['e_value']
                            break
                elif stripped_key == 'Top D gene match':
                    self.set_family('D family', value, out_d)
                    for hit in out_d['Hits']:
                        if hit['gene'] == value:
                            out_d['Top D gene e_value'] = hit['e_value']
                            break
                elif stripped_key == 'Top J gene match':
                    self.set_family('J family', value, out_d)
                    for hit in out_d['Hits']:
                        if hit['gene'] == value:
                            out_d['Top J gene e_value'] = hit['e_value']
                            break

            if 'Top D gene match' not in out_d:
                out_d['Top D gene match'] = 'N/A'
                out_d['Top D gene e_value'] = 'N/A'
            self.triggered = False
            return out_d

        matches = re.match(self.regex, line)
        if matches:
            self.fields = matches.group(1).split(',')
            self.triggered = True

            return out_d

        return False

    @staticmethod
    def set_family(prop, value, output):
        try:
            star_index = value.index('*')
            output[prop] = value[0:star_index]
        except:
            output[prop] = value


class SubRegionParser(BaseParser):
    """Parses out Subregion information

    This parser is responsible for the 'Top V gene match', 'Top D gene match', 'Top J gene match',
    'V family', 'J family', 'D family', 'Top V gene e_value', 'Top D gene e_value', and 'Top J gene e_value'
    fields"""
    def __init__(self):
        self.regex = re.compile('^Sub-region sequence details \((.*)\)')
        self.required = False
        self.triggered = False
        self.fields = None

    def parse(self, line, out_d):
        if self.triggered:
            region = dict(zip(self.fields, line.strip().split('\t')))
            region_type = region['type']
            del region['type']
            for key, val in region.items():
                out_d[region_type + '-' + key.strip()] = val
            self.triggered = False
            return out_d

        matches = re.match(self.regex, line)
        if matches:
            self.fields = matches.group(1).split(',')
            self.fields.insert(0, 'type')
            self.triggered = True
            return out_d

        return False


class AlignmentSummaryParser(BaseParser):
    """Parses out Alignment summary information

        This parser is responsible for the alignment summary table fields from IgBlast, which can include:
        'FR1', 'FR2', 'FR3', 'FR4', 'CDR1', 'CDR2', 'CDR3', and 'Total' fields."""
    def __init__(self):
        self.regex = re.compile('^Alignment summary between query and top germline V gene hit \((.*)\)')
        self.required = True
        self.alignment_type_regex = re.compile('(\w*)-IMGT')
        self.triggered = False
        self.frameworks_found = []

    def parse(self, line, output):
        if self.triggered:
            alignment = dict(zip(self.fields, line.strip().split('\t')))
            alignment_type = alignment['type']
            alignment_type = alignment_type.replace(' (germline)', '').replace('-IMGT', '')

            if 'Total' not in alignment_type:
                self.frameworks_found.append(re.match(self.alignment_type_regex, alignment['type']).group(1))

            del alignment['type']

            if 'Total' in alignment_type:
                self.triggered = False
                output['Frameworks found'] = self.frameworks_found
                self.frameworks_found = []

            output[alignment_type] = {}
            for key, val in alignment.items():
                if val != 'N/A':
                    output[alignment_type][key.strip()] = float(val)
                else:
                    output[alignment_type][key.strip()] = val

            return output

        matches = re.match(self.regex, line)
        if matches:
            self.fields = matches.group(1).split(',')
            self.fields.insert(0, 'type')
            self.triggered = True

            return output

        return False


class AlignmentLine():
    """Helper class for parsing each line of the alignments result"""
    def __init__(self, line):
        self.id = None
        self.unique_key = None
        self.start = None
        self.end = None
        self.is_query = False
        self.left = ''
        self.type = ''
        self.gene_type = ''
        self.percent_identity = ''
        self.fraction = ''
        self.width = None
        self.span = None
        self.is_header = False
        self.is_translation = False
        self.appended_count = 0
        self.hit_regex = re.compile('([VDJ])\s+(\S*)\s+(\S*)\s+(\S*)\s+([0-9]+)\s+(\S*)\s+([0-9]+)')
        self.query_regex = re.compile('(\S*Query\S*)\s+([0-9]+)\s+(\S*)\s+([0-9]+)')
        self.header_regex = re.compile('[<\->]')
        self.read_line(line)

    def read_line(self, line):
        # Query Line
        matches = re.search(self.query_regex, line)
        if matches:
            self.id = matches.group(1)
            self.start = int(matches.group(2))
            self.left = self.id + '  ' + str(self.start)
            self.al_string = matches.group(3)
            self.end = int(matches.group(4))
            self.is_query = True
            self.span = matches.span(3)
            self.width = self.span[1] - self.span[0]
            self.unique_key = self.id + '-' + str(self.end)
            return

        # Hit Line
        matches = re.search(self.hit_regex, line)
        if matches:
            self.gene_type = matches.group(1)
            self.percent_identity = matches.group(2)
            self.fraction = matches.group(3)
            self.id = matches.group(4)
            self.start = int(matches.group(5))
            self.al_string = matches.group(6)
            self.end = int(matches.group(7))
            self.span = matches.span(6)
            self.width = self.span[1] - self.span[0]
            self.unique_key = self.id + '-' + str(self.end)
            return

        # Header Line
        matches = re.search(self.header_regex, line)
        if matches:
            self.id = 'header'
            self.unique_key = self.id
            self.is_header = True
            self.al_string = line
            self.start = ''
            self.end = ''
            return

        # if we made it here we must be a translation
        self.id = 'translation'
        self.unique_key = self.id
        self.is_translation = True
        self.al_string = line
        self.start = ''
        self.end = ''


class AlignmentParser(BaseParser):
    """Parses out Alignment summary information

        This parser is responsible for the 'Alignments' field as well as the 'NT', 'sequence_aa', and 'AA_Length' fields in
        'CDR1', 'CDR2', 'CDR3', 'FR1', 'FR2', 'FR3', and 'FR4'"""
    def __init__(self, input_type, seqs_dict):
        self.trigger_regex = re.compile('^Alignments')
        self.halt_regex = re.compile('^Lambda')
        self.alignments_regex = re.compile('(<[-\w]*>)')
        self.required = True
        self.alignments = []
        self.alignment_span = None
        self.final_alignments = collections.OrderedDict()
        self.current_line_index = 0
        self.triggered = False
        self.white_count = 0
        self.chunk = 0
        self.translation_trigger = False
        self.alignment_lines = []
        self.query_count = 0
        self.previous_alignment_line = None
        self.first_frame_index = 0
        self.query_alignment = None
        self.query_line_alignment = None
        self.input_type = input_type
        self.seqs_dict = seqs_dict

    def reset_vars(self):
        self.alignments = []
        self.alignment_span = None
        self.final_alignments = collections.OrderedDict()
        self.current_line_index = 0
        self.triggered = False
        self.white_count = 0
        self.chunk = 0
        self.translation_trigger = False
        self.alignment_lines = []
        self.query_count = 0
        self.previous_alignment_line = None
        self.first_frame_index = 0
        self.query_line_alignment = None

    def parse(self, line, out_d, previous_line_whitespace):
        if re.match(self.trigger_regex, line):
            self.triggered = True
            self.current_line_index = 0
            return out_d

        if not self.triggered:
            return False

        if re.match(self.halt_regex, line):
            return self.finish(out_d)

        alignment_line = AlignmentLine(line)
        if alignment_line.span:
            if self.alignment_span and (self.alignment_span[1] - self.alignment_span[0]) < alignment_line.width:
                self.alignment_span = alignment_line.span
            elif not self.alignment_span:
                self.alignment_span = alignment_line.span

        if self.previous_alignment_line and alignment_line.is_translation:
            if not self.previous_alignment_line.is_header and not previous_line_whitespace:
                # ignore this translation completely
                return out_d

        if alignment_line.is_query:
            self.query_alignment = alignment_line
            self.query_count += 1

        self.alignment_lines.append(alignment_line)
        alignment_line.chunk = self.query_count + alignment_line.is_header + alignment_line.is_translation
        self.previous_alignment_line = alignment_line
        return out_d

    @staticmethod
    def _reverse_complement(seq):
        retval = ''

        for i in range(1, len(seq) + 1):
            retval += REVERSE_COMPLEMENT[seq[-i]]

        return retval

    def finish(self, out_d):
        self.triggered = False

        final_alignment_keys = []
        final_alignments = []
        max_width = 0

        for al in self.alignment_lines:
            unique_key = None
            if al.id and al.end:
                unique_key = al.id + '-' + str(al.start - 1)
            elif al.is_header:
                unique_key = 'header'
                al.al_string = al.al_string[self.alignment_span[0]:self.alignment_span[1]]
            elif al.is_translation:
                unique_key = 'translation'
                al.al_string = al.al_string[self.alignment_span[0]:self.alignment_span[1]]

            if unique_key:
                if unique_key in final_alignment_keys:
                    i = final_alignment_keys.index(unique_key)
                    if unique_key != 'header' and unique_key != 'translation':
                        final_alignment_keys[i] = al.id + '-' + str(al.end)
                    final_alignments[i].al_string += al.al_string.rstrip('\n')
                    final_alignments[i].end = al.end

                    new_length = len(final_alignments[i].al_string)
                    max_width = new_length if new_length > max_width else max_width
                else:
                    offset = ' ' * (self.alignment_span[1] - self.alignment_span[0]) * (al.chunk - 1)
                    al.al_string = offset + al.al_string.rstrip('\n')
                    new_length = len(al.al_string)
                    max_width = new_length if new_length > max_width else max_width

                    if unique_key == 'header':
                        insert_index = 0
                    elif unique_key == 'translation':
                        insert_index = 1
                    else:
                        insert_index = len(final_alignment_keys)

                    final_alignment_keys.insert(insert_index, al.unique_key)
                    final_alignments.insert(insert_index, al)

        out_d['Alignments'] = {
            'strings': [],
            'keys': []
        }

        for alignment in final_alignments:
            alignment.al_string = alignment.al_string + (' ' * (max_width - len(alignment.al_string)))
            if not alignment.is_header and not alignment.is_translation:
                alignment.al_string = re.sub(' ', '-', alignment.al_string)

            out_d['Alignments']['keys'].append(alignment.id)
            out_d['Alignments']['strings'].append(alignment.al_string)

            if 'translation' in alignment.id:
                s = alignment.al_string
                first_frame_index = len(s) - len(s.lstrip()) - 1
                while first_frame_index - 3 >= 0:
                    first_frame_index -= 3

                self.first_frame_index = first_frame_index
                out_d['AA'] = alignment.al_string.replace(' ', '')

            if 'Query' in alignment.id:
                self.query_line_alignment = alignment

            filtered_hits = list(filter((lambda x: x['gene'] == alignment.id ), out_d['Hits']))
            if filtered_hits:
                filtered_hits[0]['gene_type'] = alignment.gene_type
                filtered_hits[0]['alignment_start'] = alignment.start
                filtered_hits[0]['alignment_end'] = alignment.end
                filtered_hits[0]['percent_identity'] = float(alignment.percent_identity.strip('%'))
                filtered_hits[0]['percent_fraction'] = alignment.fraction

        out_d['NT-Trimmed'] = self.query_line_alignment.al_string[self.first_frame_index:]

        match_index = 0
        for match in self.alignments_regex.finditer(out_d['Alignments']['strings'][0]):
            try:
                key = out_d['Frameworks found'][match_index]
            except:
                out_d['CDR3'] = {}
                key = 'CDR3'

            match_index += 1
            span = match.span()

            # FR4 check
            if 'CDR3' in key:
                # if seqs_dict[out_d['sequence_id']].letter_annotations:
                if self.input_type == 'fastq':
                    if out_d['Strand'] == '-':
                        cdr3_nt = self._reverse_complement(out_d['Alignments']['strings'][2][span[0]:span[1]])
                    else:
                        cdr3_nt = out_d['Alignments']['strings'][2][span[0]:span[1]]

                    dict_seq = self.seqs_dict[out_d['Sequence ID']]

                    cdr3_nt = str(cdr3_nt).replace('-', '')
                    cdr3_start_index = dict_seq['seq'].find(cdr3_nt)
                    cdr3_end_index = cdr3_start_index + len(cdr3_nt)

                    cdr_rec = dict_seq['quality_scores'][cdr3_start_index - 5:cdr3_end_index + 5]

                    lowest_phred = 100
                    for quality in cdr_rec.encode('ascii'):
                        lowest_phred = int(quality)-33 if lowest_phred > int(quality)-33 else lowest_phred

                    out_d['CDR3']['Quality'] = cdr_rec
                    out_d['CDR3']['Lowest Phred'] = lowest_phred

                fr4_aa = out_d['Alignments']['strings'][1][span[1]:].replace(' ', '')
                fr4_nt = out_d['Alignments']['strings'][2][span[1]:]
                if len(fr4_aa) or len(fr4_nt):
                    out_d['FR4'] = {}
                    if len(fr4_aa):
                        out_d['FR4']['AA'] = fr4_aa
                    if len(fr4_nt):
                        out_d['FR4']['NT'] = fr4_nt

            out_d[key]['AA'] = out_d['Alignments']['strings'][1][span[0]:span[1]].replace(' ', '')
            out_d[key]['AA_Length'] = len(out_d[key]['AA'])
            out_d[key]['NT'] = out_d['Alignments']['strings'][2][span[0]:span[1]]

        if self.input_type == 'fastq':
            l = self.seqs_dict[out_d['Sequence ID']]['quality_scores'].encode('ascii')
            average_quality = round(sum([int(x)-33 for x in l]) / float(len(l)), 2)
            out_d['Average Quality'] = average_quality

        try:
            del out_d['Frameworks found']
        except:
            pass

        self.reset_vars()
        return out_d


class LegacyParser():
    """This class manages the overall parsing, including what parsers and filters are being included"""

    def __init__(self, seq_dict, out_file, args):
        self.args = args

        if self.args['outfmt'] in ['lsjson', 'json']:
            self.out_file = open(out_file, 'w')
        elif self.args['outfmt'] == 'dict':
            self.out_d = collections.OrderedDict()
        elif self.args['outfmt'] == 'tsv':
            raise NotImplementedError("TSV outputting unsupported with legacy output; use non-legacy mode")

        self.current_d = collections.OrderedDict()
        self.filters = filters.PyIRFilters(args)

        self.total_parsed = 0
        self.total_passed = 0
        self.end_regex = re.compile('^Effective search space used:.*$')

        # The parsers must be initialized in order of appearance in BLAST output for PyIR to work
        self.parsers = [
            QueryParser(seq_dict),
            SignificantAlignmentParser(),
            VDJSummaryParser(),
            AlignmentSummaryParser(),
            AlignmentParser(args['input_type'], seq_dict)
        ]

    def parse(self, cmd):
        previous_line_whitespace = False
        parser_index = 0
        triggered = False

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   universal_newlines=True)

        for line in process.stdout:
            if line.isspace():
                previous_line_whitespace = True
                continue
            else:
                previous_line_whitespace = False

#            For the current line check the current parser and see if it matches. If it doesn't, and the current
#            parser is not required, then continue on to the next parser and do the same thing until one reaches a
#            parser that is both not matching and is required.
            offset = 0
            while True:
                if type(self.parsers[parser_index+offset]).__name__ == "AlignmentParser":
                    out = self.parsers[parser_index + offset].parse(line, self.current_d, previous_line_whitespace)
                else:
                    out = self.parsers[parser_index + offset].parse(line, self.current_d)

                if out:
                    self.current_d = out
                    if not triggered:
                        parser_index = parser_index+offset
                        triggered = True
                    break
                else:
                    if triggered:
                        triggered = False
                        parser_index = ((parser_index+1) % len(self.parsers))
                    else:
                        if parser_index+offset == len(self.parsers)-1:
                            break
                        else:
                            offset += 1

            # If we match with the ending line, save our results and reset for next sequence
            if re.match(self.end_regex, line):
                should_write = True
                if 'additional_field' in self.args and self.args['additional_field']:
                    self.current_d[self.args['additional_field'][0]] = self.args['additional_field'][1]

                if self.args['enable_filter']:
                    should_write = self.filters.run_filters(self.current_d)

                if should_write:
                    if self.args['outfmt'] == 'lsjson':
                        if self.args['pretty']:
                            self.out_file.write(json.dumps(self.current_d, indent=4, separators=(',', ':')) + '\n')
                        else:
                            self.out_file.write(json.dumps(self.current_d) + '\n')
                    elif self.args['outfmt'] == 'json':
                        if self.args['pretty']:
                            self.out_file.write(json.dumps(self.current_d, indent=4, separators=(',', ':')) + ',\n')
                        else:
                            self.out_file.write(json.dumps(self.current_d) + ',\n')
                    elif self.args['outfmt'] == 'dict':
                        self.out_d[self.current_d['sequence_id']] = self.current_d

                    self.total_passed += 1

                self.current_d = {}
                self.total_parsed += 1
                parser_index = 0

        self.out_file.close()


class AirrParser():
    def __init__(self, out_file, args):
        self.args = args
        self.total_parsed = 0
        self.total_passed = 0

        if self.args['outfmt'] == 'tsv':
            self.outkeys = IGBLAST_TSV_HEADER[:]
            if 'additional_field' in self.args and self.args['additional_field']:
                self.outkeys.extend([self.args['additional_field'][0]])
            self.outkeys.extend(['v_family', 'd_family', 'j_family', 'cdr3_aa_length'])

        if self.args['outfmt'] == 'dict':
            self.out_d = {}
        else:
            self.out_file = open(out_file, 'w')

        self.filters = filters.PyIRFilters(args)

    def parse(self, cmd):
        first = True
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
        for line in process.stdout:
            linesplit = line.strip('\n').split('\t')
            if first:
                first = False
                continue
            else:
                d = {IGBLAST_TSV_HEADER[index]: linesplit[index] for index in range(0, len(IGBLAST_TSV_HEADER))}

                should_write = True
                if 'additional_field' in self.args and self.args['additional_field']:
                    d[self.args['additional_field'][0]] = self.args['additional_field'][1]

                if self.args['enable_filter']:
                    should_write = self.filters.run_filters(d)

                #This is where we generate PyIR-specific values
                d['v_family'] = d['v_call'].split(',')[0].split('*')[0]
                d['d_family'] = d['d_call'].split(',')[0].split('*')[0]
                d['j_family'] = d['j_call'].split(',')[0].split('*')[0]
                d['cdr3_aa_length'] = len(d['cdr3_aa'])

                # FR4 check
                if not d['fwr4'] and not d['fwr4_aa']:
                    if d['cdr3'] and d['cdr3_aa'] and d['productive'] == 'T':
                        matched_cdr3 = re.search(d['cdr3'], d['sequence_alignment'])
                        matched_cdr3_aa = re.search(d['cdr3_aa'], d['sequence_alignment_aa'])
                        if matched_cdr3 and matched_cdr3_aa:
                            d['fwr4'] = d['sequence_alignment'][matched_cdr3.end():]
                            d['fwr4_aa'] = d['sequence_alignment_aa'][matched_cdr3_aa.end():]
                            if d['fwr4'] and d['fwr4_aa']:
                                d['fwr4'] = d['fwr4'].replace('-', '')
                                if re.search(d['fwr4'], d['sequence']):
                                    d['fwr4_start'] = re.search(d['fwr4'], d['sequence']).start()+1
                                    d['fwr4_end'] = re.search(d['fwr4'], d['sequence']).end()

                if should_write:
                    if self.args['outfmt'] == 'lsjson':
                        if self.args['pretty']:
                            self.out_file.write(json.dumps(d, indent=4, separators=(',', ':')) + '\n')
                        else:
                            self.out_file.write(json.dumps(d) + '\n')
                    elif self.args['outfmt'] == 'json':
                        if self.args['pretty']:
                            self.out_file.write(json.dumps(d, indent=4, separators=(',', ':')) + ',\n')
                        else:
                            self.out_file.write(json.dumps(d) + ',\n')
                    elif self.args['outfmt'] == 'tsv':
                        for index in range(0, len(self.outkeys)):
                            if index == 0:
                                self.out_file.write(str(d[self.outkeys[index]]))
                            else:
                                self.out_file.write('\t' + str(d[self.outkeys[index]]))
                        self.out_file.write('\n')
                    elif self.args['outfmt'] == 'dict':
                        self.out_d[d['sequence_id']] = d

                    self.total_passed += 1

                self.total_parsed += 1

        if self.args['outfmt'] != 'dict':
            self.out_file.close()
