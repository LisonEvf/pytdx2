from opentdx.parser.baseParser import register_parser
from opentdx.parser.quotation.kline import K_Line


@register_parser(0x52d)
class K_Line_Offset(K_Line):
    pass