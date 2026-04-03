from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

from tdx_mcp.client import exQuotationClient
from tdx_mcp.client import QuotationClient
from tdx_mcp.const import BLOCK_FILE_TYPE, CATEGORY, EX_CATEGORY, FILTER_TYPE, MARKET, PERIOD, SORT_TYPE
from tdx_mcp.parser.ex_quotation import file, goods
from tdx_mcp.parser.quotation import server, stock
if __name__ == "__main__":

    client = QuotationClient()
    if client.connect().login():
        
        # print("心跳包")
        # print(client.call(server.HeartBeat()))
        # print("获取服务器公告")
        # print(client.call(server.Announcement()))
        # print(client.call(server.TodoFDE()))
        # print("获取升级提示")
        # print(client.call(server.UpgradeTip()))
        # print("获取交易所公告--需要登录")
        # print(client.call(server.ExchangeAnnouncement()))
        # print(client.call(server.Info()))

        # print(f"获取 深市 股票数量 {client.get_count(MARKET.SZ)}", )
        
        # print("获取股票列表")
        # print(pd.DataFrame(client.get_list(MARKET.SZ)))

        # print("另一个获取股票列表")
        # print(pd.DataFrame(client.call(stock.List2(MARKET.SZ, 0))))

        # print("获取指数动量")
        # momentum = pd.DataFrame(client.get_index_momentum(MARKET.SH, '999999'))
        # momentum.plot.bar()
        # plt.show()

        # print("获取指数概况")
        # print(pd.DataFrame(client.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.SZ, '399006'), (MARKET.BJ, '899050'), (MARKET.SH, '000688'), (MARKET.SH, '000300')])))
        
        # print("获取k线")
        # print(pd.DataFrame(client.get_kline(MARKET.SH, '000001', PERIOD.DAILY)))
        
        # print("获取指数k线")
        # print(pd.DataFrame(client.get_kline(MARKET.SH, '999999', PERIOD.MINS, times=10)))
        
        # print("获取分时图")
        # df = pd.DataFrame(client.get_tick_chart(MARKET.SH, '999999'))
        # print(df)
        # # 图表1：主图 
        # plt.subplot(2, 1, 1)
        # ax1 = plt.gca()
        # plt.xlim(0, 240)
        # # 绘制price曲线
        # ax1.plot(df.index, df['price'])
        # # 绘制avg曲线（等于price的100倍）
        # ax1.plot(df.index, df['avg'])

        # # 图表2：成交量柱状图
        # plt.subplot(2, 1, 2)
        # plt.xlim(0, 240)
        # ax3 = plt.gca()
        # ax3.bar(df.index, df['vol'])

        # plt.show()

        # print("获取详细行情")
        # print(pd.DataFrame(client.get_stock_quotes_details([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        # , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')])))
        
        # print("获取行情全景")
        # for name, board in client.get_stock_top_board(CATEGORY.A).items():
        #     print("榜单：%s", name)
        #     print(pd.DataFrame(board))

        # print("获取行情列表")
        # print(pd.DataFrame(client.get_stock_quotes_list(CATEGORY.A)))
        
        # print("获取行情列表-按总金额排序，排除北证、ST、科创")
        # print(pd.DataFrame(client.get_stock_quotes_list(CATEGORY.A, sortType=SORT_TYPE.TOTAL_AMOUNT, filter=[FILTER_TYPE.BJ, FILTER_TYPE.ST, FILTER_TYPE.KC])))
        
        # print("获取简略行情")
        # print(pd.DataFrame(client.get_quotes([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        # , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')])))
        
        # print("获取异动")
        # print(pd.DataFrame(client.get_unusual(MARKET.SZ)))

        # print("查询历史分时行情")
        # print(pd.DataFrame(client.get_history_orders(MARKET.SH, '000001', date(2026, 1, 7))))
        
        # print("查询历史分时成交")
        # print(pd.DataFrame(client.get_transaction(MARKET.SH, '000001', date(2026, 3, 3))))
        
        # print("查询分时成交")
        # print(pd.DataFrame(client.get_transaction(MARKET.SZ, '000001')))

        # print("查询带笔数的历史分时成交")
        # print(pd.DataFrame(client.get_transaction(MARKET.SH, '000001', date(2026, 3, 3))))

        # print("获取历史分时线")
        # df = pd.DataFrame(client.get_tick_chart(MARKET.SZ, '000001', date(2026, 3, 3)))
        # print(df)
        # # 图表1：主图 
        # plt.subplot(2, 1, 1)
        # ax1 = plt.gca()
        # # 绘制price曲线
        # ax1.plot(df.index, df['price'])
        # # 绘制fast曲线（等于price的100倍）
        # ax1.plot(df.index, df['avg'] / 100)

        # # 图表2：成交量柱状图
        # plt.subplot(2, 1, 2)
        # ax3 = plt.gca()
        # ax3.bar(df.index, df['vol'])

        # plt.show()


        # def chart_sampling(market, code):
        #     print("获取分时图缩略数据")
        #     chart = client.get_chart_sampling(market, code)
        #     chart = pd.Series(chart)
        #     chart.plot()
        #     plt.show()
        # chart_sampling(MARKET.SZ, '000001')

        # print("查询公司信息")
        # print(client.get_company_info(MARKET.SZ, '000001'))

        # print("获取板块信息")
        # print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.DEFAULT)))
        # print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.ZS)))
        # print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.FG)))
        # print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.GN)))
        
        
        # def get_index_detail():
        #     print("获取指数信息")
        #     # df = pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', 'capitalization', 'circulating', 'ABcapitalization', 'circulatingValue', 'pe(TTM)', 'date', 'type', 'chg_1ago', 'chg_2ago', 'chg_3ago', 'pb', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'circulatingZ', 'u10', 'u11', 'u12', 'u13', 'amt_1ago', 'amt_2ago'])
        #     # df_base2 = pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', 'open_amt_1ago', 'open_amt_2ago'])
        #     df = pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', '总股本', '流通股', 'AB股总市值', '流通市值', '市盈(动)', 'date', 'type', '昨涨幅', '前日涨幅', '3日前涨幅', '市净率', '3', '4', '5', '6', '7', '8', '流通股本Z', '10', '11', '12', '13', '昨成交额', '前日成交额'])
        #     df_base2 = pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', '昨开盘金额', '前日开盘金额'])
        #     return pd.merge(df, df_base2, on=['market', 'code', 'date'], how='left')
        # print(get_index_detail())

        # # TODO 这里表头数量老变化，先不追究原因了
        # print(pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', '总股本', '流通股', 'AB股总市值', '流通市值', '市盈(动)', 'date', 'type', '昨涨幅', '前日涨幅', '3日前涨幅', '市净率', '3', '4', '5', '6', '7', '8', '流通股本Z', '10', '11', '12', '13', '昨成交额', '前日成交额']))
        # print(pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', '昨开盘金额', '前日开盘金额']))


        # print(pd.DataFrame(client.get_table_file('tdxhy.cfg'), columns=['market', 'code', '通达信新行业代码', 'unk', 'nown', '申万行业代码'])) # 通信达行业和申万行业对照表
        # print(pd.DataFrame(client.get_table_file('infoharbor_spec.cfg')))

        # print(client.download_file('infoharbor_block.dat'))
        # print(pd.DataFrame(client.get_table_file('infoharbor_ex.name'), columns=['market', 'code', 'name']))

        # print("获取转债表")
        # print(pd.DataFrame(client.get_csv_file('spec/speckzzdata.txt'), columns=['market', 'code', '关联股', '转股价', '票面利率', '发行规模', '1', '2', '转股日', '到期价', '到期日', '3', '4', '上市日期', '5', '信用评级', '信用评级1', '6', '7', '8', '9']))
        
        # print(client.download_file('spec/spectfdata.txt')) # bytearray(b'')
        # print("获取LOF表")
        # print(pd.DataFrame(client.get_csv_file('spec/speclofdata.txt'), columns=['market', 'code', '发行批准文号', 'unknown', '基金经理？', 'X']))
        # print("获取ETF表")
        # etf_table = client.get_csv_file('spec/specjjdata.txt')
        # etf_table = [(MARKET(int(row[1])), row[0]) for row in etf_table]
        # print(pd.DataFrame(client.get_stock_quotes_details(etf_table[:100])))
        
        # print("获取关联信息表") 
        # print(pd.DataFrame(client.get_table_file('infoharbor_ex.code'), columns=['code', 'name', '关联信息']))
        
        # # TODO 这里表头数量老变化，先不追究原因了
        # print("获取AI行情表") 
        # print(pd.DataFrame(client.get_table_file('spec/specgpext.txt'), columns=['market', 'code', 'core_Business', 'safe_score', 'light_spot', '']))

        # print(client.download_file('spec/specgpsxt.txt'))

        # print(pd.DataFrame(client.get_table_file('spec/speczshot.txt'))) # 指数热点
        # print(pd.DataFrame(client.get_table_file('spec/speczsevent.txt'))) # 指数事件
        # print(pd.DataFrame(client.get_table_file('spec/speczsevent_ds.txt'))) # 指数事件-大事
        # print(client.download_file('spec/spechkblock.txt').decode("gbk"))
        # print(client.download_file('specaddinfo.txt')) # bytearray(b'')

        # print(client.download_file('bi/bigdata_0.zip'))
        # print(client.download_file('bi/bigdata_1.zip'))
        # print(client.download_file('customcfg_cfv.zip'))

        # with open('zhb.zip', 'wb') as f:
        #     f.write(client.download_file('zhb.zip'))
        # with open('zd.zip', 'wb') as f:
        #     f.write(client.download_file('zd.zip'))
        # print(client.download_file('todayhf/sz000001.img')) # bytearray(b'')
        # print(client.download_file('tdxfin/gpcw.txt')) # bytearray(b'')
        # print(client.download_file('iwshop/0_000001.htm').decode("utf-8"))

        print("测试 QuotesXor (0x547协议)")
        print(pd.DataFrame(client.call(stock.QuotesXor([(MARKET.SZ, '000001')]))))
        print(pd.DataFrame(client.call(stock.QuotesXor([(MARKET.SZ, '000001'), (MARKET.SZ, '000002')]))))
        print(pd.DataFrame(client.call(stock.QuotesXor([(MARKET.SH, '600009'), (MARKET.SH, '600010')]))))
        print(pd.DataFrame(client.call(stock.QuotesXor([
            (MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.BJ, '899050'),
            (MARKET.SZ, '399006'), (MARKET.SH, '000688'), (MARKET.SH, '000300'), (MARKET.SH, '880005')
        ]))))


    # ex_client = exQuotationClient()
    # # for host in market_hosts:
    # #     if client.connect(host[1], host[2]):
    # #         print(client.call(market.f023()))
    # #         client.disconnect()
    # if ex_client.connect().login():
    #     print(ex_client.server_info())
        
    #     print("获取商品数量")
    #     print(ex_client.get_count())
    #     print("获取商品类别表")
    #     print(pd.DataFrame(ex_client.get_category_list()))
    #     print("获取商品列表")
    #     print(pd.DataFrame(ex_client.get_list()))

    #     print("获取期货报价列表")
    #     print(pd.DataFrame(ex_client.get_quotes_list(EX_CATEGORY.US_STOCK, 12632, 100)))
    #     print("获取商品报价")
    #     print(ex_client.get_quotes(EX_CATEGORY.CFFEX_FUTURES, 'IF2602'))
    #     print("批量获取商品报价")
    #     print(pd.DataFrame(ex_client.get_quotes([
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2602'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2603'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2606'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2607'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC500'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL0'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL2'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL7'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL8'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL9'),
    #     ])))
    #     print("批量获取期货报价")
    #     print(pd.DataFrame(ex_client.get_quotes2([
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2602'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2603'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2606'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC2607'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'IC500'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL0'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL2'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL7'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL8'),
    #         (EX_CATEGORY.CFFEX_FUTURES, 'ICL9'),
    #     ])))

    #     print(ex_client.get_table())
    #     print(ex_client.get_table_detail())

    #     print("获取商品历史成交")
    #     print(pd.DataFrame(ex_client.get_history_transaction(EX_CATEGORY.US_STOCK, 'FHN-C', date(2025, 10, 28))))
        
    #     print("获取商品历史分时图")
    #     print(pd.DataFrame(ex_client.get_tick_chart(EX_CATEGORY.US_STOCK, 'HIMS', date(2026, 3, 12))))
        
    #     print("获取基金信息")
    #     print(ex_client.call(file.Download('iwshop_jj/000010.htm')))

    #     print("获取商品K线")
    #     print(pd.DataFrame(ex_client.get_kline(EX_CATEGORY.US_STOCK, 'TSLA', PERIOD.DAILY)))

    #     print("又一个获取商品K线")
    #     print(pd.DataFrame(ex_client.call(goods.K_Line2(EX_CATEGORY.US_STOCK, 'TSLA', PERIOD.DAILY))))
        
        
    #     print("获取商品分时图")
    #     df = pd.DataFrame(ex_client.get_tick_chart(EX_CATEGORY.HK_MAIN_BOARD, '09988'))
    #     print(df)
    #     # 图表1：主图 
    #     plt.subplot(2, 1, 1)
    #     ax1 = plt.gca()
    #     # 绘制price曲线
    #     ax1.plot(df.index, df['price'])
    #     # 绘制fast曲线（等于price的100倍）
    #     ax1.plot(df.index, df['avg'])

    #     # 图表2：成交量柱状图
    #     plt.subplot(2, 1, 2)
    #     ax3 = plt.gca()
    #     ax3.bar(df.index, df['vol'])

    #     plt.show()

    #     print("获取商品分时缩略图")
    #     chart = pd.Series(ex_client.call(goods.ChartSampling(EX_CATEGORY.HK_MAIN_BOARD, '09988')))
    #     chart.plot()
    #     plt.show()


    #     print(ex_client.download_file('cfg/ggqqcode.txt'))
    #     print(ex_client.download_file('cfg/neeqcode.txt'))
    #     print(ex_client.download_file('cfg/szqqcode.txt'))
    #     print(ex_client.download_file('iwshop_hk/00006.htm'))
    #     print(ex_client.download_file('tdxbase/code2name.ini'))
    #     print(ex_client.download_file('tdxbase/code2name_hk.ini'))
    #     print(ex_client.download_file('tdxbase/code2name_qq.ini'))
    #     print(ex_client.download_file('tdxbase/code2qhidx.ini'))
    #     print(ex_client.download_file('tdxbase/code2targ.ini'))
    #     print(ex_client.download_file('tdxbase/hkcodeuse.cfg'))

        
    #     # print(pd.DataFrame(ex_client.call(goods.f2562(1))))
    #     # print(pd.DataFrame(ex_client.call(goods.f2562(3))))
    #     # print(ex_client.call(goods.f23f6()))
    #     # print(ex_client.call(goods.f2487(EX_CATEGORY.HK_MAIN_BOARD, '09988')))
    #     # print(ex_client.call(goods.f2488(EX_CATEGORY.HK_MAIN_BOARD, '09988')))