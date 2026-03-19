from parser.base_parser import register_parser
from parser.quotation.kline import K_Line


@register_parser(0x52d)
class K_Line_Offset(K_Line):
    pass