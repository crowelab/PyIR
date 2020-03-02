import re

AA_PATTERN = re.compile('(WG|FG)')

AIRR_TO_LEGACY = {
    'v_support': 'Top V gene e_value',
    'j_support': 'Top J gene e_value',
    'vj_in_frame': 'V-J frame',
    'productive': 'Productive',
    'stop_codon': 'stop codon',
    'sequence_alignment': 'NT-Trimmed'
}

class PyIRFilters:
    def __init__(self, args):
        self.debug = args['debug']
        self.legacy = args['legacy']
        self.is_fastq = True if args['input_type'] == 'fastq' else False

        if args['enable_filter']:
            self.filters = []
            self.min_v_evalue = args['filter_v_evalue']
            self.min_j_evalue = args['filter_j_evalue']
            self.filters.append(self._e_seq_dict_filter)
            if args['filter_productive']:
                self.filters.append(self._productive_filter)
            if args['filter_stop_codon']:
                self.filters.append(self._stop_codon_filter)
            if args['filter_vjframe']:
                self.filters.append(self._vj_frame_filter)
            if args['filter_aa_strings']:
                self.filters.append(self._aa_filter)
            if args['filter_nt_strings']:
                self.filters.append(self._nt_filter)

            min,max = args['filter_cdr3_length'].split(',')
            self.min_cdr3_length = int(min)
            self.max_cdr3_length = int(max)
        else:
            self.filters = []

    def get_seqdict_field(self, field):
        if self.legacy:
            return AIRR_TO_LEGACY[field]
        else:
            return field


    def run_filters(self, seq_dict):
        for fil in self.filters:
            if not fil(seq_dict):
                return False

        return True

    def _e_seq_dict_filter(self, seq_dict):
        if self.get_seqdict_field('v_support') in seq_dict and self.get_seqdict_field('j_support') in seq_dict and \
                seq_dict[self.get_seqdict_field('v_support')] and seq_dict[self.get_seqdict_field('j_support')]:
            if float(seq_dict[self.get_seqdict_field('v_support')]) <= self.min_v_evalue and float(seq_dict[self.get_seqdict_field('j_support')]) <= self.min_j_evalue:
                return True
            else:
                if self.debug:
                    print("E value check failed -- V gene:", seq_dict[self.get_seqdict_field('v_support')], "J gene:", seq_dict[self.get_seqdict_field('j_support')])
                return False
        else:
            if self.debug:
                print("E value check failed -- No top V or J match")
                return False

    def _productive_filter(self, seq_dict):
        if seq_dict[self.get_seqdict_field('productive')] in ['Yes', 'T']:
            return True
        else:
            if self.debug:
                print("Productive failed -- Productive:", seq_dict[self.get_seqdict_field('productive')])
                return False

    def _stop_codon_filter(self, seq_dict):
        if seq_dict[self.get_seqdict_field('stop_codon')] in ['No', 'F']:
            return True
        else:
            if self.debug:
                print("stop codon failed -- stop codon:", seq_dict[self.get_seqdict_field('stop_codon')])
                return False

    def _vj_frame_filter(self, seq_dict):
        if seq_dict[self.get_seqdict_field('vj_in_frame')] in ['In-frame', 'T']:
            return True
        else:
            if self.debug:
                print("V-J frame failed -- V-J frame:", seq_dict[self.get_seqdict_field('vj_in_frame')])
                return False

    def _aa_filter(self, seq_dict):
        if self.legacy:
            if 'AA' in seq_dict and '*' not in seq_dict['AA'] and 'CDR3' in seq_dict and 'AA' in seq_dict['CDR3'] and \
                    re.search(AA_PATTERN, seq_dict['AA'].split(seq_dict['CDR3']['AA'])[1]):
                return True
            else:
                if self.debug:
                    print("AA failed -- AA:", seq_dict['AA'])
                return False
        else:
            if '*' not in seq_dict['sequence_alignment_aa'] and seq_dict['cdr3_aa'] and \
                    re.search(AA_PATTERN, seq_dict['sequence_alignment_aa'].split(seq_dict['cdr3_aa'])[1]):
                return True
            else:
                if self.debug:
                    print("AA failed -- AA:", seq_dict['sequence_alignment_aa'])
                return False

    def _nt_filter(self, seq_dict):
        if 'N' not in seq_dict[self.get_seqdict_field('sequence_alignment')][2:-3]:
            return True
        else:
            if self.debug:
                print("NT-Trimmed failed -- NT-Trimmed:", seq_dict[self.get_seqdict_field('sequence_alignment')])
            return False

    def _cdr3_filter(self, seq_dict):
        if self.legacy:
            if 'CDR3' in seq_dict and 'AA' in seq_dict['CDR3'] and len(seq_dict['CDR3']['AA']) in range(self.min_cdr3_length,self.max_cdr3_length):
                return True
            else:
                if self.debug:
                    if 'CDR3' in seq_dict:
                        if 'AA' in seq_dict['CDR3']:
                            print("cdr3 length failed -- CDR3 AA:", seq_dict['CDR3']['AA'])
                        else:
                            print("cdr3 length failed -- AA missing from CDR3:", seq_dict['CDR3'])
                    else:
                        print("cdr3 length failed -- CDR3 missing from query")
                return False
        else:
            if 'cdr3' in seq_dict and 'cdr3_aa' in seq_dict and len(seq_dict['cdr3_aa']) in range(self.min_cdr3_length,self.max_cdr3_length):
                return True
            else:
                return False


    def _quality_filter(self, seq_dict):
        if not self.is_fastq:
            return True
        else:
            if self.legacy:
                if 'CDR3' in seq_dict:
                    if 'Lowest Phred' in seq_dict['CDR3']:
                        if seq_dict['CDR3']['Lowest Phred'] >= 30:
                            return True
                    else:
                        if self.debug:
                            print("CDR3 Quality failed -- CDR3 Lowest Phred:", seq_dict['CDR3']['Lowest Phred'])
                        return False
                else:
                    if self.debug:
                        print("CDR3 Quality failed -- No CDR3!")
                    return False
            else:
                return True

    def _fr3_filter(self, seq_dict):
        if self.legacy:
            if 'FR3' in seq_dict:
                if 'AA' in seq_dict['FR3']:
                    if 'C' in seq_dict['FR3']['AA'][-3:]:
                        return True
                    else:
                        if self.debug:
                            print("FR3 'C' filter failed -- FR3 AA:", seq_dict['FR3']['AA'])
                        return False
                else:
                    if self.debug:
                        print("FR3 'C' filter failed -- No AA in FR3:", seq_dict['FR3'])
                    return False
            else:
                if self.debug:
                    print("FR3 'C' filter failed -- FR3 missing from query")
                return False
        else:
            if 'fr3_aa' in seq_dict and 'C' in seq_dict['fr3_aa'][-3:]:
                return True
            else:
                return False
