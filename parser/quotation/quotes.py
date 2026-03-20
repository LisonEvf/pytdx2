import struct

from const import MARKET
from parser.baseParser import register_parser
from parser.quotation.quotes_list import QuotesList


@register_parser(0x54c)
class Quotes(QuotesList):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception('stocks count must > 0')
        self.body = bytearray(struct.pack('<H6sH', 5, b'', count))
        for market, code in stocks:
            self.body.extend(struct.pack('<B6s', market.value, code.encode('gbk')))