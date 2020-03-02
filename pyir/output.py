import json
from abc import ABCMeta, abstractmethod


class BaseFormatter:
    __metaclass__ = ABCMeta

    def __init__(self, args):
        self.args = args

    @abstractmethod
    def format(self, parser_output, args):
        pass


class JsonFormatter(BaseFormatter):
    def format(self, parser_output):
        return json.dumps(parser_output, indent=4, separators=(',',':')) if self.args['pretty'] else json.dumps(parser_output)


format_type_mapping = {
    'json': JsonFormatter,
}


def get_formatter(args):
    """Returns formatter class given the command line arguments"""
    return format_type_mapping[args['out_format']](args)

