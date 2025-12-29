# coding=utf-8

from datetime import datetime
import struct
import six

from const import MARKET
from utils.log import log

def query_market(code) -> MARKET:
    """
    0 - 深圳， 1 - 上海
    """
    if code.startswith(("50", "51", "60", "68", "90", "110", "113", "132", "204")):
        return MARKET.SH
    elif code.startswith(("00", "12", "13", "18", "15", "16", "18", "20", "30", "39", "115", "1318")):
        return MARKET.SZ
    elif code.startswith(("5", "6", "7", "9")):
        return MARKET.SH
    elif code.startswith(("4", "8")):
        return MARKET.BJ
    else:
        log.error("unknown market code: {}".format(code))
        return None


#### XXX: 分析了一下，貌似是类似utf-8的编码方式保存有符号数字
def get_price(data, pos):
    pos_byte = 6
    bdata = indexbytes(data, pos)
    intdata = bdata & 0x3f
    if bdata & 0x40:
        sign = True
    else:
        sign = False

    if bdata & 0x80:
        while True:
            pos += 1
            bdata = indexbytes(data, pos)
            intdata += (bdata & 0x7f) << pos_byte
            pos_byte += 7

            if bdata & 0x80:
                pass
            else:
                break

    pos += 1

    if sign:
        intdata = -intdata

    return intdata, pos

def to_datetime(num, with_time=False) -> datetime:
    year = 0
    month = 0
    day = 0
    hour = 15
    minute = 0
    if with_time:
        zip_data = num & 0xFFFF
        year = (zip_data >> 11) + 2004
        month = int((zip_data & 0x7FF) / 100)
        day = (zip_data & 0x7FF) % 100

        tminutes = num >> 16
        hour = int(tminutes / 60)
        minute = tminutes % 60
    else:
        year = int(num / 10000)
        month = int((num % 10000) / 100)
        day = num % 100
    if year > datetime.now().year:
        raise ValueError("year is too large")

    return datetime(year, month, day, hour, minute)

def get_time(buffer, pos):
    (tminutes, ) = struct.unpack("<H", buffer[pos: pos + 2])
    hour = int(tminutes / 60)
    minute = tminutes % 60
    pos += 2

    return hour, minute, pos

def indexbytes(data, pos):

    if six.PY2:
        if type(data) is bytearray:
            return data[pos]
        else:
            return six.indexbytes(data, pos)
    else:
        return data[pos]


def format_time(time_stamp):
    if time_stamp == 0:
        return '00:00:00.000'
    else:
        time_stamp = str(time_stamp)
    """
    format time from reversed_bytes0
    by using method from https://github.com/rainx/pytdx/issues/187
    """
    time = time_stamp[:-6] + ':'
    if int(time_stamp[-6:-4]) < 60:
        time += '%s:' % time_stamp[-6:-4]
        time += '%06.3f' % (
            int(time_stamp[-4:]) * 60 / 10000.0
        )
    else:
        time += '%02d:' % (
            int(time_stamp[-6:]) * 60 / 1000000
        )
        time += '%06.3f' % (
            (int(time_stamp[-6:]) * 60 % 1000000) * 60 / 1000000.0
        )
    return time