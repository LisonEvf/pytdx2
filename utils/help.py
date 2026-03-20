# coding=utf-8

from datetime import date, datetime
import struct

from const import EX_CATEGORY, MARKET
from utils.log import log


def query_market(code) -> MARKET:
    """
    0 - 深圳， 1 - 上海
    """
    if code.startswith(("50", "51", "60", "68", "90", "110", "113", "132", "204")):
        return MARKET.SH
    elif code.startswith(
        ("00", "12", "13", "18", "15", "16", "18", "20", "30", "39", "115", "1318")
    ):
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
    bdata = data[pos]
    int_data = bdata & 0x3F
    if bdata & 0x40:
        sign = True
    else:
        sign = False

    if bdata & 0x80:
        while True:
            pos += 1
            bdata = data[pos]
            int_data += (bdata & 0x7F) << pos_byte
            pos_byte += 7

            if bdata & 0x80:
                pass
            else:
                break

    pos += 1

    if sign:
        int_data = -int_data

    return int_data, pos


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

        minutes = num >> 16
        hour = int(minutes / 60)
        minute = minutes % 60
    else:
        year = num // 10000
        month = num % 10000 // 100
        day = num % 100
    if year > datetime.now().year:
        raise ValueError("year is too large")

    return datetime(year, month, day, hour, minute)


def format_time(time_stamp):
    if time_stamp == 0 or time_stamp == 100:
        return "00:00:00.000"
    else:
        time_stamp = str(time_stamp)
    """
    format time from reversed_bytes0
    by using method from https://github.com/rainx/pytdx/issues/187
    """
    time = time_stamp[:-6] + ":"
    if int(time_stamp[-6:-4]) < 60:
        time += "%s:" % time_stamp[-6:-4]
        time += "%06.3f" % (int(time_stamp[-4:]) * 60 / 10000.0)
    else:
        time += "%02d:" % (int(time_stamp[-6:]) * 60 / 1000000)
        time += "%06.3f" % ((int(time_stamp[-6:]) * 60 % 1000000) * 60 / 1000000.0)
    return time


def unpack_futures(data, code_len: int = 23):
    if len(data) == 292 + code_len:
        raise Exception("")

    category, code = struct.unpack(f"<B{code_len}s", data[: 1 + code_len])
    (
        active,
        pre_close,
        open,
        high,
        low,
        current,
        open_position,
        add_position,
        vol,
        curr_vol,
        amount,
        in_vol,
        ex_vol,
        u14,
        hold_position,
    ) = struct.unpack(f"<I5f4If4I", data[1 + code_len : 61 + code_len])
    pending_list = struct.unpack("<5f5I5f5I", data[61 + code_len : 141 + code_len])
    pending = {
        "bids": [
            {"price": pending_list[i], "vol": pending_list[i + 5]} for i in range(5)
        ],
        "asks": [
            {"price": pending_list[i], "vol": pending_list[i + 5]}
            for i in range(10, 15)
        ],
    }
    (
        u1,
        settlement_price,
        u2,
        average_price,
        pre_settlement_price,
        u3,
        u4,
        u5,
        u6,
        pre_close_price,
    ) = struct.unpack("<HfIffIIIIf", data[141 + code_len : 179 + code_len])
    (
        s1,
        pre_vol,
        u7,
        s2,
        u8,
        day3_raise,
        s3,
        settlement_price2,
        date_raw,
        u9,
        raise_speed,
        u10,
        s4,
        u11,
        u12,
    ) = struct.unpack("<12sff12sff25sfIIff24sHB", data[179 + code_len : 291 + code_len])

    # 当没有 date_raw 数据时,会报错
    # goods.Futures_QuotesList(ExtMarketCategory.港股.value, 1895, 2)  02632没有date_raw数据
    if date_raw // 10000 == 0:
        date_obj = date(1900, 1, 1)
    else:
        date_obj = date(date_raw // 10000, date_raw % 10000 // 100, date_raw % 100)

    return {
        "category": EX_CATEGORY(category),
        "code": code.decode("gbk").replace("\x00", ""),
        "active": active,
        "pre_close": pre_close,
        "open": open,
        "high": high,
        "low": low,
        "current": current,
        "open_position": open_position,
        "add_position": add_position,
        "vol": vol,
        "curr_vol": curr_vol,
        "amount": amount,
        "in_vol": in_vol,
        "ex_vol": ex_vol,
        "u14": u14,
        "hold_position": hold_position,
        "pending": pending,
        "settlement_price": settlement_price,
        "average_price": average_price,
        "pre_settlement_price": pre_settlement_price,
        "pre_close_price": pre_close_price,
        "pre_vol": pre_vol,
        "day3_raise": day3_raise,
        "settlement_price2": settlement_price2,
        "date": date_obj,
        "raise_speed": raise_speed,
        "u1": u1,
        "u2": u2,
        "u3": [u3, u4, u5, u6],
    }


# 根据可视化的板块id获取到系统需要的真实板块code
def exchange_board_code(board_symbol):
    if board_symbol.startswith("US"):
        # US0401 => 30401
        board_code = 30000 + int(board_symbol.replace("US", ""))
    elif board_symbol.startswith("HK"):
        # HK0283 => 20283
        board_code = 20000 + int(board_symbol.replace("HK", ""))
    elif board_symbol.startswith("000"):
        # 000686 => 31686
        board_code = 31000 + int(board_symbol)
    elif board_symbol.startswith("399"):
        # 399372 => 30399
        board_code = int(board_symbol) - 399000 + 30000
    elif board_symbol.startswith("899"):
        # 899050 => 32050
        board_code = int(board_symbol) - 899000 + 32000
    elif board_symbol.startswith("88"):
        # 880686 => 20686
        board_code = int(board_symbol) - 880000 + 20000
    else:
        # 由于数字过大,可能查询到其他的板块
        board_code = int(board_symbol)

    return board_code
