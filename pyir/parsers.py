from abc import ABCMeta, abstractmethod
import collections
import json
import re
import pyir.output
import Bio.SeqIO
from Bio.Seq import Seq

class BaseParser():

    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(self, line, output):
        pass

class QueryParser(BaseParser):

    def __init__(self, args, seq_dict, out_file):

        self.args = args
        self.regex = re.compile('^Query= (\S*)')
        self.seq_dict = seq_dict
        self.out = open(out_file, 'w')
        self.current_seq = None
        self.formatter = pyir.output.get_formatter(self.args)
        self.total_parsed = 0

    def parse(self, line, output):

        matches = re.match(self.regex, line)

        if matches:

            output = self.dump_output(output) if output else output

            output['Sequence ID'] = matches.group(1)

            try:

                output['Raw Sequence'] = str(self.seq_dict[output['Sequence ID']].seq).upper()
                self.total_parsed += 1

            except KeyError as e:

                pass

        return output

    def dump_output(self, output):

        self.out.write(self.formatter.format(output) + '\n')

        return collections.OrderedDict()

class SeqLengthParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^Length=(\S*)')

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        matches = re.match(self.regex, line)

        if matches:
            output['Sequence Length'] = matches.group(1)

        return output

class SignificantAlignmentParser(BaseParser):

    def __init__(self):

        self.trigger_regex = re.compile('^Sequences producing significant alignments')
        self.hit_regex = re.compile('^(\S*)\s*(\S*)\s*(\S*)')
        self.halt_regex = re.compile('^Domain classification requested')
        self.hits = []
        self.triggered = False

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        disable_trigger = re.match(self.halt_regex, line)
        if disable_trigger:
            self.triggered = False
            output['Hits'] = self.hits
            self.hits = []
            return output

        if self.triggered:
            matches = re.match(self.hit_regex, line)
            self.hits.append({'gene': matches.group(1), 'bit_score': float(matches.group(2)), 'e_value':float(matches.group(3))})
            return output

        matches = re.match(self.trigger_regex, line)

        if matches:
            self.triggered = True

        return output


class DomainParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^Domain classification requested: (\w*)')

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        matches = re.match(self.regex, line)

        if matches:
            output['Domain Classification'] = matches.group(1)

        return output


class VDJSummaryParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^V-\(D\)-J rearrangement summary for query sequence \((.*)\)\.')
        self.triggered = False

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        if self.triggered:

            for key, val in dict(zip(self.fields, line.strip().split('\t'))).items():

                stripped_key = key.strip()
                value = val.split(',')[0]
                output[stripped_key] = value

                if stripped_key == 'Top V gene match':
                    self.set_family('V family', value, output)
                    for hit in output['Hits']:
                        if hit['gene'] == value:
                            output['Top V gene e_value'] = hit['e_value']

                if stripped_key == 'Top D gene match':
                    self.set_family('D family', value, output)

                if stripped_key == 'Top J gene match':
                    self.set_family('J family', value, output)
                    for hit in output['Hits']:
                        if hit['gene'] == value:
                            output['Top J gene e_value'] = hit['e_value']

            self.triggered = False

            return output

        matches = re.match(self.regex, line)

        if matches:
            self.fields = matches.group(1).split(',')
            self.triggered = True

        return output

    def set_family(self, prop, value, output):
        try:
            star_index = value.index('*')
            output[prop] = value[0:star_index]
        except:
            output[prop] = value

class VDJJunctionParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^V-\(D\)-J junction details baseParserd on top germline gene matches \((.*)\)\.')
        self.triggered = False

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        if self.triggered:

            for key, val in dict(zip(self.fields, line.strip().split('\t'))).items():
                output[key.strip()] = val

            self.triggered = False

            return output

        matches = re.match(self.regex, line)

        if matches:
            self.fields = matches.group(1).split(',')
            self.triggered = True

        return output

class SubRegionParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^Sub-region sequence details \((.*)\)')
        self.triggered = False

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        if self.triggered:

            region = dict(zip(self.fields, line.strip().split('\t')))
            region_type = region['type']
            del region['type']

            for key, val in region.items():
                output[region_type + '-' + key.strip()] = val

            self.triggered = False

            return output

        matches = re.match(self.regex, line)

        if matches:
            self.fields = matches.group(1).split(',')
            self.fields.insert(0, 'type')
            self.triggered = True

        return output

class AlignmentSummaryParser(BaseParser):

    def __init__(self):

        self.regex = re.compile('^Alignment summary between query and top germline V gene hit \((.*)\)')
        self.alignment_type_regex = re.compile('(\w*)-IMGT')
        self.triggered = False
        self.frameworks_found = []

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

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

            return output

        matches = re.match(self.regex, line)

        if matches:
            self.fields = matches.group(1).split(',')
            self.fields.insert(0, 'type')
            self.triggered = True

        return output

class AlignmentLine():

    def __init__(self, line):

        self.id = None
        self.start = None
        self.end = None
        self.is_query = False
        self.left = ''
        self.type = ''
        self.span = None
        self.is_header = False
        self.is_translation = False
        self.appended_count = 0
        self.hit_regex = re.compile('([VDJ])\s+(\S*)\s+(\S*)\s+(\S*)\s+([0-9]+)\s+(\S*)\s+([0-9]+)')
        self.query_regex = re.compile('(\S*Query\S*)\s+([0-9]+)\s+(\S*)\s+([0-9]+)')
        self.header_regex = re.compile('[<\->]')

        self.read_line(line)

    def read_line(self, line):

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

    def __init__(self):

        self.trigger_regex = re.compile('^Alignments')
        self.halt_regex = re.compile('^Lambda')
        self.alignments_regex = re.compile('(<[-\w]*>)')

        self.reset_vars()

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

    def parse(self, line, output, previous_line_whitespace, seqs_dict):

        if re.match(self.trigger_regex, line):
            self.triggered = True
            self.current_line_index = 0
            return output

        if not self.triggered:
            return output

        if re.match(self.halt_regex, line):
            return self.finish(line, output, seqs_dict)

        alignment_line = AlignmentLine(line)

        if self.alignment_span and alignment_line.span and (self.alignment_span[1] - self.alignment_span[0]) < alignment_line.width:
            self.alignment_span = alignment_line.span

        if not self.alignment_span and alignment_line.span:
            self.alignment_span = alignment_line.span

        if self.previous_alignment_line and alignment_line.is_translation:
            if not self.previous_alignment_line.is_header and not previous_line_whitespace:
                # ignore this translation completely
                return output

        self.alignment_lines.append(alignment_line)

        if alignment_line.is_query:
            self.query_alignment = alignment_line
            self.query_count += 1

        alignment_line.chunk = self.query_count + alignment_line.is_header + alignment_line.is_translation

        self.previous_alignment_line = alignment_line

        return output

    def finish(self, line, output, seqs_dict):

        self.triggered = False

        final_alignment_keys = []
        final_alignments = []
        span = None
        max_width = 0

        for al in self.alignment_lines:

            unique_key = None

            if al.id and al.end:
                unique_key = al.id + '-' + str(al.start  - 1)

            if al.is_header:
                unique_key = 'header'
                al.al_string = al.al_string[self.alignment_span[0]:self.alignment_span[1]]

            if al.is_translation:
                unique_key = 'translation'
                al.al_string = al.al_string[self.alignment_span[0]:self.alignment_span[1]]

            if unique_key and unique_key in final_alignment_keys:

                i = final_alignment_keys.index(unique_key)

                final_alignments[i].al_string += al.al_string.rstrip('\n')
                final_alignments[i].end = al.end

                new_length = len(final_alignments[i].al_string)
                max_width = new_length if new_length > max_width else max_width

                if unique_key != 'header' and unique_key != 'translation':
                    final_alignment_keys[i] = al.id + '-' + str(al.end)

                unique_key = None

            if unique_key and unique_key not in final_alignment_keys:

                offset = ' ' * (self.alignment_span[1] - self.alignment_span[0]) * (al.chunk - 1)
                al.al_string = offset + al.al_string.rstrip('\n')

                new_length = len(al.al_string)
                max_width = new_length if new_length > max_width else max_width

                insert_index = len(final_alignment_keys)

                if unique_key == 'header':
                    insert_index = 0

                if unique_key == 'translation':
                    insert_index = 1

                final_alignment_keys.insert(insert_index, al.unique_key)
                final_alignments.insert(insert_index, al)

        output['Alignments'] = {
            'strings': [],
            'keys': []
        }

        for alignment in final_alignments:

            alignment.al_string = alignment.al_string + (' ' * (max_width - len(alignment.al_string)))
            if not alignment.is_header and not alignment.is_translation:
                alignment.al_string = re.sub(' ', '-', alignment.al_string)

            output['Alignments']['keys'].append(alignment.id)
            output['Alignments']['strings'].append(alignment.al_string)

            if 'translation' in alignment.id:

                s = alignment.al_string
                first_frame_index = len(s) - len(s.lstrip()) - 1
                while first_frame_index - 3 >= 0:
                    first_frame_index -= 3

                self.first_frame_index = first_frame_index

                output['AA']= alignment.al_string.replace(' ', '')

            if 'Query' in alignment.id:
                self.query_line_alignment = alignment

            filtered_hits = list(filter((lambda x: x['gene'] == alignment.id ), output['Hits']))
            if filtered_hits:
                filtered_hits[0]['gene_type'] = alignment.gene_type
                filtered_hits[0]['alignment_start'] = alignment.start
                filtered_hits[0]['alignment_end'] = alignment.end
                filtered_hits[0]['percent_identity'] = float(alignment.percent_identity.strip('%'))
                filtered_hits[0]['percent_fraction'] = alignment.fraction

        output['NT-Trimmed'] = self.query_line_alignment.al_string[self.first_frame_index:]

        match_index = 0
        for match in self.alignments_regex.finditer(output['Alignments']['strings'][0]):

            try:
                key = output['Frameworks found'][match_index]
            except:
                output['CDR3'] = {}
                key = 'CDR3'

            match_index += 1
            span = match.span()

            # FR4 check
            if 'CDR3' in key:

                if seqs_dict[output['Sequence ID']].letter_annotations:

                    if output['Strand'] == '-':
                        cdr3_nt = Seq(output['Alignments']['strings'][2][span[0]:span[1]]).reverse_complement()
                    else:
                        cdr3_nt = output['Alignments']['strings'][2][span[0]:span[1]]


                    dict_seq = seqs_dict[output['Sequence ID']]

                    cdr3_nt = str(cdr3_nt).replace('-', '')
                    cdr3_start_index = dict_seq.seq.find(cdr3_nt)
                    cdr3_end_index = cdr3_start_index + len(cdr3_nt)

                    cdr_rec = dict_seq[cdr3_start_index - 5:cdr3_end_index + 5]

                    lowest_phred = 100
                    for quality in cdr_rec.letter_annotations['phred_quality']:
                        lowest_phred = quality if lowest_phred > quality else lowest_phred

                    output['CDR3']['Quality'] = cdr_rec.format('fastq').split('\n')[3]
                    output['CDR3']['Lowest Phred'] = lowest_phred

                fr4_aa = output['Alignments']['strings'][1][span[1]:].replace(' ', '')
                fr4_nt = output['Alignments']['strings'][2][span[1]:]
                if len(fr4_aa) or len(fr4_nt):
                    output['FR4'] = {}
                if len(fr4_aa):
                   output['FR4']['AA'] = fr4_aa
                if len(fr4_nt):
                   output['FR4']['NT'] = fr4_nt

            output[key]['AA'] = output['Alignments']['strings'][1][span[0]:span[1]].replace(' ', '')
            output[key]['NT'] = output['Alignments']['strings'][2][span[0]:span[1]]

        if seqs_dict[output['Sequence ID']].letter_annotations:

            l = seqs_dict[output['Sequence ID']].letter_annotations['phred_quality']
            output['Average Quality'] = round(sum(l) / float(len(l)), 2)


        try:
            del output['Frameworks found']
        except:
            pass

        self.reset_vars()

        return output

class IgBlastParser():

    parser_classes = [
        SeqLengthParser,
        SignificantAlignmentParser,
        DomainParser,
        VDJSummaryParser,
        VDJJunctionParser,
        SubRegionParser,
        AlignmentParser,
        AlignmentSummaryParser
    ]

    def __init__(self, args, seq_dict, igblast_output, out_file):

        self.args = args
        self.seq_dict = seq_dict
        self.igblast_output = igblast_output
        self.out_file = out_file
        self.output = collections.OrderedDict()
        self.query_parser = QueryParser(self.args, self.seq_dict, self.out_file)

    def parse(self):

        current_line_index = 0

        parsers = []

        for parser_class in self.parser_classes:
            parsers.append(parser_class())

        self.started = False

        previous_line_whitespace = False
        for line in open(self.igblast_output):

            if line.isspace():
                previous_line_whitespace = True
                continue

            self.output = self.query_parser.parse(line, self.output)


            for parser in parsers:

                self.output = parser.parse(line, self.output, previous_line_whitespace, self.seq_dict)

            previous_line_whitespace = False

        self.query_parser.dump_output(self.output)

        return self.query_parser.total_parsed
