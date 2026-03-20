from parser.baseParser import register_parser
from parser.ex_quotation.table import Table

@register_parser(0x2423, 1)
class TableDetail(Table):
    def __init__(self, start: int = 0, mode: int = 0):
        super().__init__(start, mode)