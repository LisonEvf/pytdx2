from datetime import date
from client.marketClient import MarketClient
from client.quotationClient import QuotationClient
from const import EX_CATEGORY, PERIOD, MARKET, BLOCK_FILE_TYPE, CATEGORY
import pandas as pd
from time import sleep
from parser.quotation import file, server, stock
from parser.ex_quotation import futures, server as ex_server
import matplotlib.pyplot as plt
from utils.log import log
import numpy as np

if __name__ == "__main__":

    client = QuotationClient()
    if client.connect().login():
        
        log.info("心跳包")
        print(client.call(server.HeartBeat()))
        log.info("获取服务器公告")
        print(client.call(server.Announcement()))
        print(client.call(server.TodoFDE()))
        log.info("获取升级提示")
        print(client.call(server.UpgradeTip()))
        log.info("获取交易所公告--需要登录")
        print(client.call(server.ExchangeAnnouncement()))
        print(client.call(server.Info()))

        log.info(f"获取 深市 股票数量 {client.get_security_count(MARKET.SZ)}", )
        log.info("获取股票列表")
        print(pd.DataFrame(client.get_security_list(MARKET.SZ, 0, 1000)))
        log.info("另一个获取股票列表")
        print(pd.DataFrame(client.call(stock.ListB(MARKET.SZ, 0))))
        log.info("获取k线")
        print(pd.DataFrame(client.get_KLine_data(MARKET.SZ, '000001', PERIOD.DAY)))
        log.info("获取指数k线")
        print(pd.DataFrame(client.get_KLine_data(MARKET.SH, '999999', PERIOD.DAY, 0, 2000)))
        log.info("查询历史分时行情")
        print(pd.DataFrame(client.get_history_orders(MARKET.SH, '600151', date(2026, 1, 7))['orders']))
        log.info("查询分时成交")
        print(pd.DataFrame(client.get_transaction(MARKET.SH, '600151')))
        log.info("查询历史分时成交")
        print(pd.DataFrame(client.get_history_transaction(MARKET.SH, '600151', date(2026, 1, 7))))


        log.info("获取简略行情")
        print(pd.DataFrame(client.get_security_quotes([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')])))
        log.info("获取详细行情")
        print(pd.DataFrame(client.get_security_quotes_details([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')])))
        log.info("获取行情列表")
        print(pd.DataFrame(client.get_security_quotes_by_category(CATEGORY.SZ)))
        log.info("获取行情全景")
        for name, board in client.get_top_stock_board(CATEGORY.A).items():
            log.info("榜单：%s", name)
            print(pd.DataFrame(board))

        log.info("获取指数概况")
        print(pd.DataFrame(client.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.BJ, '899050'), 
                                                  (MARKET.SZ, '399006'), (MARKET.SH, '000688'), (MARKET.SH, '880008'), 
                                                  (MARKET.SH, '000888'), (MARKET.SH, '000680'), (MARKET.SZ, '399330'), 
                                                  (MARKET.SZ, '399673'), (MARKET.SZ, '399106'), (MARKET.SZ, '399102')])))


        log.info("获取异动")
        print(pd.DataFrame(client.get_unusual(MARKET.SZ)))
        
        def index_Kline():
            log.info("获取指数k线")
            df = pd.DataFrame(client.call(stock.IndexChart(MARKET.SZ, '399006')))
            print(df.to_clipboard())
            # 图表1：主图 
            plt.subplot(2, 1, 1)
            ax1 = plt.gca()
            # 绘制price曲线
            ax1.plot(df.index, df['price'])
            # 绘制fast曲线（等于price的100倍）
            ax1.plot(df.index, df['fast'] / 100)

            # 图表2：成交量柱状图
            plt.subplot(2, 1, 2)
            ax3 = plt.gca()
            ax3.bar(df.index, df['amount'])

            plt.show()
        index_Kline()
        
        def chart_sampling(market, code):
            log.info("获取分时图缩略数据")
            chart = client.get_chart_sampling(market, code)
            chart = pd.Series(chart['prices'])
            chart.plot()
            plt.show()
        chart_sampling(MARKET.SZ, '000001')

        log.info("查询公司信息")
        print(client.get_company_info(MARKET.SZ, '000001'))

        log.info("获取板块信息")
        print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.DEFAULT)))
        print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.ZS)))
        print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.FG)))
        print(pd.DataFrame(client.get_block_file(BLOCK_FILE_TYPE.GN)))
        
        
        # def get_index_detail():
        #     log.info("获取指数信息")
        #     # df = pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', 'capitalization', 'circulating', 'ABcapitalization', 'circulatingValue', 'pe(TTM)', 'date', 'type', 'chg_1ago', 'chg_2ago', 'chg_3ago', 'pb', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'circulatingZ', 'u10', 'u11', 'u12', 'u13', 'amt_1ago', 'amt_2ago'])
        #     # df_base2 = pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', 'open_amt_1ago', 'open_amt_2ago'])
        #     df = pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', '总股本', '流通股', 'AB股总市值', '流通市值', '市盈(动)', 'date', 'type', '昨涨幅', '前日涨幅', '3日前涨幅', '市净率', '3', '4', '5', '6', '7', '8', '流通股本Z', '10', '11', '12', '13', '昨成交额', '前日成交额'])
        #     df_base2 = pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', '昨开盘金额', '前日开盘金额'])
        #     return pd.merge(df, df_base2, on=['market', 'code', 'date'], how='left')
        # print(get_index_detail())
        print(pd.DataFrame(client.get_table_file('tdxzsbase.cfg'), columns=['market', 'code', '总股本', '流通股', 'AB股总市值', '流通市值', '市盈(动)', 'date', 'type', '昨涨幅', '前日涨幅', '3日前涨幅', '市净率', '3', '4', '5', '6', '7', '8', '流通股本Z', '10', '11', '12', '13', '昨成交额', '前日成交额']))
        print(pd.DataFrame(client.get_table_file('tdxzsbase2.cfg'), columns=['market', 'code', 'date', 'u15', 'u16', '昨开盘金额', '前日开盘金额']))


        print(pd.DataFrame(client.get_table_file('tdxhy.cfg'), columns=['market', 'code', '通达信新行业代码', 'unk', 'nown', '申万行业代码'])) # 通信达行业和申万行业对照表
        print(pd.DataFrame(client.get_table_file('infoharbor_spec.cfg')))

        print(client.download_file('infoharbor_block.dat'))
        print(pd.DataFrame(client.get_table_file('infoharbor_ex.name'), columns=['market', 'code', 'name']))

        log.info("获取转债表")
        print(pd.DataFrame(client.get_csv_file('spec/speckzzdata.txt'), columns=['market', 'code', '关联股', '转股价', '票面利率', '发行规模', '1', '2', '转股日', '到期价', '到期日', '3', '4', '上市日期', '5', '信用评级', '信用评级1', '6', '7', '8', '9']))
        
        print(client.download_file('spec/spectfdata.txt')) # bytearray(b'')
        log.info("获取LOF表")
        print(pd.DataFrame(client.get_csv_file('spec/speclofdata.txt'), columns=['market', 'code', '发行批准文号', 'unknown', '基金经理？', 'X']))
        log.info("获取ETF表")
        print(pd.DataFrame(client.get_csv_file('spec/specjjdata.txt'), columns=['code', 'market', '_', 'date', '最新净资产M', '现价？']))

        log.info("获取关联信息表") 
        print(pd.DataFrame(client.get_table_file('infoharbor_ex.code'), columns=['code', 'name', '关联信息']))
        log.info("获取AI行情表") 
        print(pd.DataFrame(client.get_table_file('spec/specgpext.txt'), columns=['market', 'code', 'core_Business', 'safe_score', 'light_spot', '']))

        print(pd.DataFrame(client.get_table_file('spec/speczshot.txt'))) # 指数热点
        print(pd.DataFrame(client.get_table_file('spec/speczsevent.txt'))) # 指数事件
        print(pd.DataFrame(client.get_table_file('spec/speczsevent_ds.txt'))) # 指数事件-大事
        print(client.download_file('spec/spechkblock.txt').decode("gbk"))
        print(client.download_file('specaddinfo.txt')) # bytearray(b'')

        print(client.download_file('bi/bigdata_0.zip'))
        print(client.download_file('bi/bigdata_1.zip'))
        print(client.download_file('customcfg_cfv.zip'))

        with open('zhb.zip', 'wb') as f:
            f.write(client.download_file('zhb.zip'))
        with open('zd.zip', 'wb') as f:
            f.write(client.download_file('zd.zip'))
        print(client.download_file('todayhf/sz000001.img')) # bytearray(b'')
        print(client.download_file('tdxfin/gpcw.txt')) # bytearray(b'')
        print(client.download_file('iwshop/0_000001.htm').decode("utf-8"))

        client.call(stock.TODO547([(MARKET.SZ, '000001')]))
        client.call(stock.TODO547([(MARKET.SZ, '000001'), (MARKET.SZ, '000002')]))
        client.call(stock.TODO547([(MARKET.SH, '600009'), (MARKET.SH, '600009')]))
        client.call(stock.TODO547([(MARKET.SH, '999999'), (MARKET.SZ, '399001'), (MARKET.BJ, '899050'), (MARKET.SZ, '399006'), (MARKET.SH, '000688'), (MARKET.SH, '000300'), (MARKET.SH, '880005')]))
        
        client.disconnect()


    ex_client = MarketClient()
    # for host in market_hosts:
    #     if client.connect(host[1], host[2]):
    #         print(client.call(market.f023()))
    #         client.disconnect()
    if ex_client.connect().login():
        print(ex_client.call(ex_server.Info()))
        print(ex_client.call(ex_server.f2562(MARKET.SH, 4055)))
        
        print(ex_client.call(futures.Count()))
        print(pd.DataFrame(ex_client.call(futures.Category_List())))
        print(ex_client.call(futures.Info(0,100)))

        print(ex_client.call(futures.Quotes(EX_CATEGORY.CFFEX_FUTURES, 'IF2602')))
        print(ex_client.call(futures.QuotesList([
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2602'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2603'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2606'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2607'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC500'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL0'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL2'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL7'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL8'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL9'),
        ])))
        print(pd.DataFrame(ex_client.call(futures.Futures_QuotesList(EX_CATEGORY.DL_FUTURES))))
        ex_client.call(futures.Futures_Quotes([
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2602'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2603'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2606'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC2607'),
            (EX_CATEGORY.CFFEX_FUTURES, 'IC500'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL0'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL2'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL7'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL8'),
            (EX_CATEGORY.CFFEX_FUTURES, 'ICL9'),
        ]))

        start = 0
        while True:
            _, count, context = ex_client.call(futures.Futures_List(start))
            start += count
            print(context)
            if count <= 0:
                break

        print(ex_client.call(futures.Futures_List2(0)))
        ex_client.disconnect()