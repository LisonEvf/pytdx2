"""
pytdx2 交互式接口文档 — 每个接口独立演示
用法: python doc.py
"""

from collections import OrderedDict
from datetime import date

import pandas as pd

from opentdx.tdxClient import TdxClient
from opentdx.const import *

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_rows', 10)


# ======================== 注册机制 ========================

ITEMS = OrderedDict()


def demo(key, title):
    def decorator(func):
        ITEMS[key] = (title, func)
        return func
    return decorator


def show(code_str, result=None, comment=None):
    """展示示例代码及结果。"""
    if comment:
        print(f"  # {comment}")
    print(f"  >>> {code_str}\n{'='*60}")
    if result is not None:
        print(result)
    print()


def run(key, tdx=None):
    title, func = ITEMS[key]
    print(f"\n{'='*60}")
    print(f"  {key}. {title}")
    print(f"{'='*60}\n")
    try:
        func(tdx)
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
    print(f"\n{'─'*60}\n")


# ======================== TdxClient — A股 ========================

@demo('01', 'stock_count          获取股票数量')
def _(c):
    show("c.stock_count(MARKET.SZ)", c.stock_count(MARKET.SZ), comment="获取深市股票数量")
    show("c.stock_count(MARKET.SH)", c.stock_count(MARKET.SH), comment="获取沪市股票数量")


@demo('02', 'stock_list           获取股票列表')
def _(c):
    show("c.stock_list(MARKET.SZ, count=5)",
         pd.DataFrame(c.stock_list(MARKET.SZ, count=5)),
         comment="获取深市前5只股票")


@demo('03', 'index_momentum       获取指数动量')
def _(c):
    show("c.index_momentum(MARKET.SH, '999999')",
         pd.DataFrame(c.index_momentum(MARKET.SH, '999999')),
         comment="上证指数动量")


@demo('04', 'index_info           获取指数概况')
def _(c):
    show("c.index_info([(MARKET.SH,'999999'), ...])",
         pd.DataFrame(c.index_info([
             (MARKET.SH, '999999'), (MARKET.SZ, '399001'),
             (MARKET.SZ, '399006'), (MARKET.BJ, '899050'),
         ])),
         comment="批量获取主要指数概况")


@demo('05', 'stock_kline          获取日K线')
def _(c):
    show("c.stock_kline(MARKET.SH, '999999', PERIOD.DAILY, count=5)",
         pd.DataFrame(c.stock_kline(MARKET.SH, '999999', PERIOD.DAILY, count=5)),
         comment="上证指数最近5根日K")


@demo('06', 'stock_kline(times=10) 多分钟K线')
def _(c):
    show("c.stock_kline(MARKET.SH, '999999', PERIOD.MINS, times=10, count=5)",
         pd.DataFrame(c.stock_kline(MARKET.SH, '999999', PERIOD.MINS, times=10, count=5)),
         comment="上证指数10分钟K线")


@demo('07', 'stock_kline(adjust)   复权K线')
def _(c):
    show("c.stock_kline(MARKET.SZ, '000001', PERIOD.DAILY, adjust=ADJUST.HFQ, count=3)",
         pd.DataFrame(c.stock_kline(MARKET.SZ, '000001', PERIOD.DAILY, count=3, adjust=ADJUST.HFQ)),
         comment="平安银行后复权日K")


@demo('08', 'stock_kline(weekly)  周K线')
def _(c):
    show("c.stock_kline(MARKET.SH, '999999', PERIOD.WEEKLY, count=5)",
         pd.DataFrame(c.stock_kline(MARKET.SH, '999999', PERIOD.WEEKLY, count=5)),
         comment="上证指数周K")


@demo('09', 'stock_tick_chart      实时分时图')
def _(c):
    show("c.stock_tick_chart(MARKET.SH, '999999')",
         pd.DataFrame(c.stock_tick_chart(MARKET.SH, '999999')),
         comment="上证指数实时分时")


@demo('10', 'stock_tick_chart(date) 历史分时图')
def _(c):
    show("c.stock_tick_chart(MARKET.SZ, '000001', date(2026, 3, 16))",
         pd.DataFrame(c.stock_tick_chart(MARKET.SZ, '000001', date(2026, 3, 16))),
         comment="平安银行历史分时")


@demo('11', 'stock_quotes_detail  详细报价')
def _(c):
    codes = [(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SH, '600000')]
    show(f"codes = {codes}\nc.stock_quotes_detail(codes)",
         pd.DataFrame(c.stock_quotes_detail(codes)),
         comment="批量获取详细报价")


@demo('12', 'stock_quotes_detail(code) 详细报价(单只)')
def _(c):
    show("c.stock_quotes_detail(MARKET.SZ, '000001')",
         pd.DataFrame(c.stock_quotes_detail(MARKET.SZ, '000001')),
         comment="单只股票详细报价")


@demo('13', 'stock_top_board       排行榜')
def _(c):
    show("boards = c.stock_top_board(CATEGORY.A)", comment="A股排行榜")
    boards = c.stock_top_board(CATEGORY.A)
    for name, board in boards.items():
        print(f"  {name}: {len(board)}条")
    print(f"\n  涨幅榜前5:")
    print(pd.DataFrame(boards.get('increase', [])[:5]))
    print()


@demo('14', 'stock_quotes_list     行情列表(排序+过滤)')
def _(c):
    show("c.stock_quotes_list(CATEGORY.A, count=10, sortType=SORT_TYPE.TOTAL_AMOUNT, filter=[...])",
         pd.DataFrame(c.stock_quotes_list(
             CATEGORY.A, count=10,
             sortType=SORT_TYPE.TOTAL_AMOUNT,
             filter=[FILTER_TYPE.BJ, FILTER_TYPE.ST, FILTER_TYPE.KC],
         )),
         comment="A股按总金额排序，排除北证/ST/科创，取前10")


@demo('15', 'stock_quotes          简略报价')
def _(c):
    codes = [(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SH, '600000')]
    show(f"codes = {codes}\nc.stock_quotes(codes)",
         pd.DataFrame(c.stock_quotes(codes)),
         comment="批量简略报价")


@demo('16', 'stock_unusual         异动数据')
def _(c):
    show("c.stock_unusual(MARKET.SZ, count=10)",
         pd.DataFrame(c.stock_unusual(MARKET.SZ, count=10)),
         comment="深市最近10条异动")


@demo('17', 'stock_auction         竞价数据')
def _(c):
    show("c.stock_auction(MARKET.SZ, '300308')",
         pd.DataFrame(c.stock_auction(MARKET.SZ, '300308')),
         comment="竞价数据")


@demo('18', 'stock_history_orders  历史委托')
def _(c):
    show("c.stock_history_orders(MARKET.SZ, '000001', date(2026, 1, 7))",
         pd.DataFrame(c.stock_history_orders(MARKET.SZ, '000001', date(2026, 1, 7))),
         comment="平安银行历史委托")


@demo('19', 'stock_transaction     实时成交')
def _(c):
    show("c.stock_transaction(MARKET.SZ, '000001')",
         pd.DataFrame(c.stock_transaction(MARKET.SZ, '000001')),
         comment="平安银行实时逐笔成交")


@demo('20', 'stock_transaction(his)历史成交')
def _(c):
    show("c.stock_transaction(MARKET.SH, '000001', date(2026, 3, 3))",
         pd.DataFrame(c.stock_transaction(MARKET.SH, '000001', date(2026, 3, 3))),
         comment="平安银行历史成交")


@demo('21', 'stock_chart_sampling 分时缩略')
def _(c):
    chart = c.stock_chart_sampling(MARKET.SZ, '000001')
    show("c.stock_chart_sampling(MARKET.SZ, '000001')",
         f"  共 {len(chart)} 个采样点, 范围: {min(chart):.2f} ~ {max(chart):.2f}",
         comment="平安银行分时缩略数据")


@demo('22', 'stock_f10             F10公司信息')
def _(c):
    show("c.stock_f10(MARKET.SZ, '000001')", comment="平安银行F10")
    info = c.stock_f10(MARKET.SZ, '000001')
    for item in info:
        content = item['content']
        preview = str(content)[:200] if content else 'None'
        print(f"  [{item['name']}] {preview}...")


@demo('23', 'stock_block           板块信息')
def _(c):
    show("c.stock_block(BLOCK_FILE_TYPE.DEFAULT)", comment="默认板块文件")
    data = c.stock_block(BLOCK_FILE_TYPE.DEFAULT)
    print(f"  共 {len(data)} 个板块")
    print(pd.DataFrame(data[:5]))
    print()


@demo('24', 'stock_vol_profile     成交分布')
def _(c):
    show("c.stock_vol_profile(MARKET.SZ, '000001')",
         pd.DataFrame(c.stock_vol_profile(MARKET.SZ, '000001')),
         comment="平安银行成交分布")


# ======================== TdxClient — 扩展市场 ========================

@demo('25', 'goods_count          商品数量')
def _(c):
    show("c.goods_count()", c.goods_count(), comment="扩展市场商品总数")


@demo('26', 'goods_category_list  商品分类列表')
def _(c):
    show("c.goods_category_list()",
         pd.DataFrame(c.goods_category_list()),
         comment="扩展市场分类")


@demo('27', 'goods_list           商品列表')
def _(c):
    show("c.goods_list(count=5)",
         pd.DataFrame(c.goods_list(count=5)),
         comment="前5个商品")


@demo('28', 'goods_quotes          单只商品报价')
def _(c):
    show("c.goods_quotes(EX_MARKET.CFFEX_FUTURES, 'IF2602')",
         c.goods_quotes(EX_MARKET.CFFEX_FUTURES, 'IF2602'),
         comment="中金所 IF2602 报价")


@demo('29', 'goods_quotes(batch)   批量商品报价')
def _(c):
    show("c.goods_quotes([(EX_MARKET.CFFEX_FUTURES,'IC2602'), ...])",
         pd.DataFrame(c.goods_quotes([
             (EX_MARKET.CFFEX_FUTURES, 'IC2602'),
             (EX_MARKET.HK_MAIN_BOARD, '09988'),
             (EX_MARKET.US_STOCK, 'TSLA'),
         ])),
         comment="批量报价")


@demo('30', 'goods_quotes_list     商品行情列表(排序)')
def _(c):
    show("c.goods_quotes_list(EX_MARKET.US_STOCK, count=10, sortType=SORT_TYPE.TOTAL_AMOUNT)",
         pd.DataFrame(c.goods_quotes_list(
             EX_MARKET.US_STOCK, count=10,
             sortType=SORT_TYPE.TOTAL_AMOUNT,
         )),
         comment="美股按总金额排序前10")


@demo('31', 'goods_kline          商品K线')
def _(c):
    show("c.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY, count=5)",
         pd.DataFrame(c.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY, count=5)),
         comment="美股TSLA日K")


@demo('32', 'goods_history_trans   商品历史成交')
def _(c):
    show("c.goods_history_transaction(EX_MARKET.US_STOCK, 'FHN-C', date(2025, 10, 28))",
         pd.DataFrame(c.goods_history_transaction(EX_MARKET.US_STOCK, 'FHN-C', date(2025, 10, 28))),
         comment="美股FHN-C历史成交")


@demo('33', 'goods_tick_chart      商品实时分时')
def _(c):
    show("c.goods_tick_chart(EX_MARKET.HK_MAIN_BOARD, '09988')",
         pd.DataFrame(c.goods_tick_chart(EX_MARKET.HK_MAIN_BOARD, '09988')),
         comment="港股09988实时分时")


@demo('34', 'goods_tick_chart(his) 商品历史分时')
def _(c):
    show("c.goods_tick_chart(EX_MARKET.US_STOCK, 'HIMS', date(2026, 3, 12))",
         pd.DataFrame(c.goods_tick_chart(EX_MARKET.US_STOCK, 'HIMS', date(2026, 3, 12))),
         comment="美股HIMS历史分时")


@demo('35', 'goods_chart_sampling 商品分时缩略')
def _(c):
    chart = c.goods_chart_sampling(EX_MARKET.HK_MAIN_BOARD, '09988')
    show("c.goods_chart_sampling(EX_MARKET.HK_MAIN_BOARD, '09988')",
         f"  共 {len(chart)} 个采样点, 范围: {min(chart):.2f} ~ {max(chart):.2f}",
         comment="港股09988分时缩略")


# ======================== MAC协议 ========================

@demo('38', 'board_list(HY)        行业板块列表')
def _(c):
    show("c.board_list(BOARD_TYPE.HY)",
         pd.DataFrame(c.board_list(BOARD_TYPE.HY)))


@demo('39', 'board_list(DQ)        地区板块列表')
def _(c):
    show("c.board_list(BOARD_TYPE.DQ)",
         pd.DataFrame(c.board_list(BOARD_TYPE.DQ)))


@demo('40', 'board_list(HK)        港股板块列表')
def _(c):
    show("c.board_list(EX_BOARD_TYPE.HK_ALL)",
         pd.DataFrame(c.board_list(EX_BOARD_TYPE.HK_ALL)))


@demo('41', 'board_list(US)        美股板块列表')
def _(c):
    show("c.board_list(EX_BOARD_TYPE.US_ALL)",
         pd.DataFrame(c.board_list(EX_BOARD_TYPE.US_ALL)))


@demo('42', 'board_members         板块成员查询')
def _(c):
    show("c.board_members('880761')  # 锂矿板块",
         pd.DataFrame(c.board_members('880761')))


@demo('43', 'board_belong          股票所属板块')
def _(c):
    show("c.board_belong('000100', MARKET.SZ)",
         pd.DataFrame(c.board_belong('000100', MARKET.SZ)))


@demo('44', 'symbol_bars(stock)    股票K线')
def _(c):
    show("c.symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=3, fq=ADJUST.HFQ)",
         pd.DataFrame(c.symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=3, fq=ADJUST.HFQ)))


@demo('45', 'symbol_bars(index)    指数K线')
def _(c):
    show("c.symbol_bars(MARKET.SH, '880310', PERIOD.DAILY, count=3, fq=ADJUST.QFQ)",
         pd.DataFrame(c.symbol_bars(MARKET.SH, '880310', PERIOD.DAILY, count=3, fq=ADJUST.QFQ)))


@demo('46', 'symbol_bars(hk)       港股K线')
def _(c):
    show("c.symbol_bars(EX_MARKET.HK_MAIN_BOARD, '00100', PERIOD.DAILY, count=3)",
         pd.DataFrame(c.symbol_bars(EX_MARKET.HK_MAIN_BOARD, '00100', PERIOD.DAILY, count=3)))


@demo('47', 'symbol_bars(us)       美股K线')
def _(c):
    show("c.symbol_bars(EX_MARKET.US_STOCK, 'TSLA', PERIOD.WEEKLY, count=3)",
         pd.DataFrame(c.symbol_bars(EX_MARKET.US_STOCK, 'TSLA', PERIOD.WEEKLY, count=3)))


@demo('52', 'board_count           板块数量')
def _(c):
    show("c.board_count(BOARD_TYPE.HY)", c.board_count(BOARD_TYPE.HY), comment="行业板块数量")
    show("c.board_count(BOARD_TYPE.GN)", c.board_count(BOARD_TYPE.GN), comment="概念板块数量")
    show("c.board_count(EX_BOARD_TYPE.HK_ALL)", c.board_count(EX_BOARD_TYPE.HK_ALL), comment="港股板块数量")


@demo('53', 'board_members_quotes  板块成分报价')
def _(c):
    show("c.board_members_quotes('880761')  # 锂矿板块",
         pd.DataFrame(c.board_members_quotes('880761')))


@demo('54', 'mac_server_init       服务器初始化')
def _(c):
    show("c.mac_server_init()", c.mac_server_init(), comment="MAC协议服务器初始化")


@demo('55', 'mac_stock_query       股票查询')
def _(c):
    show("c.mac_stock_query(MARKET.SZ, '000001')",
         c.mac_stock_query(MARKET.SZ, '000001'),
         comment="平安银行行情查询")


@demo('56', 'mac_batch_stock_data  批量股票数据')
def _(c):
    show("c.mac_batch_stock_data(MARKET.SZ, '000001')",
         c.mac_batch_stock_data(MARKET.SZ, '000001'),
         comment="平安银行OHLCV")


@demo('57', 'mac_stock_detail      分笔明细')
def _(c):
    show("c.mac_stock_detail(MARKET.SZ, '000001')",
         pd.DataFrame(c.mac_stock_detail(MARKET.SZ, '000001')),
         comment="平安银行分笔Tick")


@demo('58', 'mac_stock_bar_count   K线柱数据')
def _(c):
    show("c.mac_stock_bar_count(MARKET.SZ, '000001', count=5)",
         pd.DataFrame(c.mac_stock_bar_count(MARKET.SZ, '000001', count=5)),
         comment="平安银行K线柱")


@demo('59', 'mac_stock_small_info  分钟级数据')
def _(c):
    show("c.mac_stock_small_info(MARKET.SZ, '000001')",
         pd.DataFrame(c.mac_stock_small_info(MARKET.SZ, '000001')),
         comment="平安银行5分钟数据")


@demo('60', 'mac_kline_offset      K线偏移表')
def _(c):
    show("c.mac_kline_offset(count=10)",
         pd.DataFrame(c.mac_kline_offset(count=10)),
         comment="K线偏移表(前10条)")


# ======================== 底层客户端直调 ========================

@demo('48', 'QuotationClient 直调 — HeartBeat/Info/公告')
def _(_tdx=None):
    from opentdx.client.quotationClient import QuotationClient
    from opentdx.parser import quotation

    client = QuotationClient()
    if not client.connect().login():
        return

    show("client.call(quotation.HeartBeat())", client.call(quotation.HeartBeat()), comment="服务器心跳")
    show("client.call(quotation.ServerInfo())", client.call(quotation.ServerInfo()), comment="服务器信息")
    show("client.call(quotation.ExchangeAnnouncement())", client.call(quotation.ExchangeAnnouncement()), comment="交易所公告")
    client.disconnect()


@demo('49', 'QuotationClient — download_file / table_file / csv_file')
def _(_tdx=None):
    from opentdx.client.quotationClient import QuotationClient

    client = QuotationClient()
    if not client.connect().login():
        return

    show("client.download_file('iwshop/0_000001.htm')", comment="下载文件 (研报HTML)")
    data = client.download_file('iwshop/0_000001.htm')
    print(f"  文件大小: {len(data)} bytes")
    if data:
        print(f"  预览: {data[:200].decode('utf-8', errors='replace')}")
    print()

    show("client.get_table_file('tdxhy.cfg')", comment="表格文件 (通达信/申万行业对照)")
    df = pd.DataFrame(client.get_table_file('tdxhy.cfg'),
                      columns=['market', 'code', '通达信行业', 'unk', 'nown', '申万行业'])
    print(f"  共 {len(df)} 条")
    print(df[:3])
    print()

    show("client.get_csv_file('spec/speckzzdata.txt')", comment="CSV文件 (转债表)")
    df = pd.DataFrame(client.get_csv_file('spec/speckzzdata.txt'),
                      columns=['market', 'code', '关联股', '转股价', '票面利率', '发行规模'])
    print(f"  共 {len(df)} 条")
    print(df[:3])
    print()
    client.disconnect()


@demo('50', 'QuotationClient — QuotesEncrypt / get_company_info')
def _(_tdx=None):
    from opentdx.client.quotationClient import QuotationClient
    from opentdx.parser import quotation

    client = QuotationClient()
    if not client.connect().login():
        return

    show("client.call(quotation.QuotesEncrypt([(MARKET.SH,'999999'), ...]))",
         pd.DataFrame(client.call(quotation.QuotesEncrypt([
             (MARKET.SH, '999999'), (MARKET.SZ, '399001'),
         ]))),
         comment="加密行情")

    show("client.get_company_info(MARKET.SZ, '000001')", comment="完整F10 (含除权/财报)")
    info = client.get_company_info(MARKET.SZ, '000001')
    for item in info:
        print(f"  [{item['name']}]")
    client.disconnect()


@demo('51', 'exQuotationClient 直调 — server_info / table / download')
def _(_tdx=None):
    from opentdx.client.exQuotationClient import exQuotationClient

    client = exQuotationClient()
    if not client.connect().login():
        return

    show("client.server_info()", client.server_info(), comment="服务器信息")
    show("client.get_table()[:200]", client.get_table()[:200], comment="商品表")

    show("client.download_file('tdxbase/code2name_hk.ini')", comment="下载文件 (港股代码表)")
    data = client.download_file('tdxbase/code2name_hk.ini')
    if data:
        print(f"  文件大小: {len(data)} bytes")
        print(f"  预览: {data[:200].decode('utf-8', errors='replace')}")
    print()
    client.disconnect()


# ======================== 主入口 ========================

TDX_KEYS = {k for k in ITEMS if k.isdigit() and int(k) <= 35}

MENU = """
╔════════════════════════════════════════════════════════════════════╗
║                   pytdx2 交互式接口文档                          ║
╠════════════════════════════════════════════════════════════════════╣
║  TdxClient — A股行情                                              ║
║  01 stock_count           02 stock_list           03 index_momentum║
║  04 index_info           05 stock_kline(日K)     06 stock_kline(分时)║
║  07 stock_kline(复权)    08 stock_kline(周K)     09 分时图(实时)  ║
║  10 分时图(历史)         11 详细报价             12 详细报价(单只) ║
║  13 排行榜               14 行情列表(排序+过滤)  15 简略报价       ║
║  16 异动数据             17 竞价数据             18 历史委托       ║
║  19 实时成交             20 历史成交             21 分时缩略       ║
║  22 F10公司信息          23 板块信息             24 成交分布       ║
╠════════════════════════════════════════════════════════════════════╣
║  TdxClient — 扩展市场 (期货/港股/美股)                              ║
║  25 goods_count           26 goods_category_list  27 goods_list     ║
║  28 goods_quotes(单只)    29 goods_quotes(批量)   30 goods_quotes_list║
║  31 goods_kline          32 goods_history_trans  33 商品分时(实时) ║
║  34 商品分时(历史)       35 商品分时缩略                              ║
╠════════════════════════════════════════════════════════════════════╣
║  TdxClient — MAC协议 (板块/统一行情)                                ║
║  38 行业板块列表         39 地区板块列表         40 港股板块列表   ║
║  41 美股板块列表         42 板块成员查询         43 股票所属板块   ║
║  44 股票K线              45 指数K线              46 港股K线         ║
║  47 美股K线              52 板块数量             53 板块成分报价   ║
╠════════════════════════════════════════════════════════════════════╣
║  TdxClient — MAC协议 (行情查询)                                     ║
║  54 服务器初始化         55 股票查询             56 批量股票数据   ║
║  57 分笔明细             58 K线柱数据            59 分钟级数据     ║
║  60 K线偏移表                                                       ║
╠════════════════════════════════════════════════════════════════════╣
║  底层客户端直调                                                    ║
║  48 QuotationClient 直调(心跳/公告)                                 ║
║  49 QuotationClient 直调(文件/CSV/表格)                             ║
║  50 QuotationClient 直调(加密行情/F10)                              ║
║  51 exQuotationClient 直调                                         ║
╠════════════════════════════════════════════════════════════════════╣
║  a 运行全部    0 退出    m 重新显示菜单                             ║
╚════════════════════════════════════════════════════════════════════╝
"""


def main():
    print(MENU)
    print("正在连接行情服务器...\n")
    tdx = TdxClient().__enter__()

    while True:
        choice = input("请输入编号 (0退出, a全部, m菜单): ").strip()
        if not choice:
            continue

        if choice == '0':
            tdx.__exit__(None, None, None)
            print("退出。")
            break

        if choice.lower() == 'a':
            for key in ITEMS:
                run(key, tdx)
            continue

        if choice.lower() == 'm':
            print(MENU)
            continue

        if choice not in ITEMS:
            print(f"  无效选项: {choice}")
            continue

        run(choice, tdx)


if __name__ == '__main__':
    main()
