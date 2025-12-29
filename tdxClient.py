from datetime import date
import math
import threading
from time import time
from typing import override
from baseStockClient import BaseStockClient, update_last_ack_time
from utils.block_reader import BlockReader, BlockReader_TYPE_FLAT
from utils.log import log
from const import BLOCK_FILE_TYPE, CATEGORY, KLINE_TYPE, MARKET, tdx_hosts
from parser import stock, server, company_info, block
from parser.baseparser import BaseParser

import pandas as pd

class TdxClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, parser: BaseParser):
        resp = super().send(parser.serialize())
        if resp is None:
            return None
        else:
            return parser.deserialize(resp)

    def login(self, show_info=False):
        try:
            info = self.call(server.Login())
            if show_info:
                print(to_df(info))
            
            # self.call(remote.Notice())
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False

    @override
    def connect(self, ip=None, port=7709, time_out=5, bindport=None, bindip='0.0.0.0'):
        if ip is None:
            # 选择延迟最低的服务器连接
            infos = []
            def get_latency(ip, port, timeout):
                try:
                    start_time = time()
                    c = TdxClient().connect(ip, port, timeout)
                    # info = c.call(server.Info())
                    infos.append({
                        'ip': ip,
                        'port': port,
                        # 'delay': info['delay'],
                        'time': time() - start_time,
                    })
                except Exception as e:
                    pass
            # 多线程赛跑
            threads = []
            for host in tdx_hosts:
                t = threading.Thread(target=get_latency, args=(host[1], host[2], 1))
                threads.append(t)
                t.start()
            for t in threads:
                t.join()
            
            infos.sort(key=lambda x: x['time'])
            if len(infos) == 0:
                raise Exception("no available server")

            return super().connect(infos[0]['ip'], infos[0]['port'], time_out, bindport, bindip)
        else:
            return super().connect(ip, port, time_out, bindport, bindip)

    @override
    def doHeartBeat(self):
        self.call(server.HeartBeat())

    @update_last_ack_time
    def get_security_bars(self, market: MARKET, code: str, kline_type: KLINE_TYPE, start, count):
        # k线数据最多800条
        MAX_KLINE_COUNT = 800
        bars = []
        while len(bars) < count:
            part = self.call(stock.K_Line(market, code, kline_type, start, min(count - len(bars), MAX_KLINE_COUNT)))
            if not part:
                break
            bars = [*part, *bars]
            if len(part) < MAX_KLINE_COUNT:
                break
            start = start + len(part)

        return bars

    @update_last_ack_time
    def get_security_quotes(self, all_stock, code=None):
        """
        支持三种形式的参数
        get_security_quotes(market, code )
        get_security_quotes((market, code))
        get_security_quotes([(market1, code1), (market2, code2)] )
        :param all_stock （market, code) 的数组
        :param code{optional} code to query
        :return:
        """

        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]

        return self.call(stock.Quotes(all_stock))

    @update_last_ack_time
    def get_security_quotes_by_category(self, category: CATEGORY, start:int = 0, count: int = 0x50):
        return client.call(stock.QuotesList(category, start, count))

    @update_last_ack_time
    def get_security_count(self, market: MARKET):
        return self.call(stock.Count(market))

    @update_last_ack_time
    def get_security_list(self, market: MARKET, start, count = 1600):
        return self.call(stock.List(market, start, count))

    @update_last_ack_time
    def get_orders(self, market: MARKET, code: str):
        return self.call(stock.Orders(market, code))

    @update_last_ack_time
    def get_history_orders(self, market: MARKET, code: str, date: date):
        return self.call(stock.HistoryOrders(market, code, date))

    @update_last_ack_time
    def get_transaction(self, market: MARKET, code: str):
        # 这里最多就1800条
        MAX_TRANSACTION_COUNT = 1800
        start = 0
        transaction = []
        while True:
            part = self.call(stock.Transaction(market, code, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
        return transaction

    @update_last_ack_time
    def get_history_transaction(self, market: MARKET, code: str, date: date):
        # ref : https://github.com/rainx/pytdx/issues/7
        # 分笔行情最多2000条
        MAX_TRANSACTION_COUNT = 2000
        start = 0
        transaction = []
        while True:
            part = self.call(stock.HistoryTransaction(market, code, date, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
            
        return transaction

    @update_last_ack_time
    def get_company_info(self, market: MARKET, code: str):
        category = self.call(company_info.Category(market, code))

        info = []
        for part in category:
            content = self.call(company_info.Content(market, code, part['filename'], part['start'], part['length']))
            info.append({
                'name': part['name'],
                'content': content['content'],
            })

        xdxr = self.call(company_info.XDXR(market, code))
        if xdxr:
            info.append({
                'name': '除权分红',
                'content': xdxr,
            })

        finance = self.call(company_info.Finance(market, code))
        if finance:
            info.append({
                'name': '财报',
                'content': finance,
            })
        return info

    @update_last_ack_time
    def get_block_info(self, block_file_type: BLOCK_FILE_TYPE):
        try:
            meta = self.call(block.Meta(block_file_type))
        except Exception as e:
            log.error(e)
            return None

        if not meta:
            return None

        size = meta['size']
        one_chunk = 0x7530

        file_content = bytearray()
        for seg in range(math.ceil(size / one_chunk)):
            start = seg * one_chunk
            piece_data = self.call(block.Info(block_file_type, start, one_chunk))["data"]
            file_content.extend(piece_data)

        return BlockReader().get_data(file_content, BlockReader_TYPE_FLAT)

    @update_last_ack_time
    def get_report_file(self, filename: str, filesize=0, reporthook=None):
        """
        Download file from proxy server

        :param filename the filename to download
        :param filesize the filesize to download , if you do not known the actually filesize, leave this value 0
        """
        filecontent = bytearray(filesize)
        current_downloaded_size = 0
        get_zero_length_package_times = 0
        while current_downloaded_size < filesize or filesize == 0:
            response = self.call(block.Report(filename, current_downloaded_size))
            if response["size"] > 0:
                current_downloaded_size = current_downloaded_size + \
                    response["size"]
                filecontent.extend(response["data"])
                if reporthook is not None:
                    reporthook(current_downloaded_size,filesize)
            else:
                get_zero_length_package_times = get_zero_length_package_times + 1
                if filesize == 0:
                    break
                elif get_zero_length_package_times > 2:
                    break

        return filecontent.decode("gbk")
    
    def get_k_data(self, code, start_date, end_date):
        # 具体详情参见 https://github.com/rainx/pytdx/issues/5
        # 具体详情参见 https://github.com/rainx/pytdx/issues/21
        def __select_market_code(code):
            code = str(code)
            if code[0] in ['5', '6', '9'] or code[:3] in ["009", "126", "110", "201", "202", "203", "204"]:
                return MARKET.SH
            return MARKET.SZ
        # 新版一劳永逸偷懒写法zzz
        market_code = 1 if str(code)[0] == '6' else 0
        # https://github.com/rainx/pytdx/issues/33
        # 0 - 深圳， 1 - 上海
        

        data = pd.concat(
            [
                to_df(
                    self.get_security_bars(__select_market_code(code), code, KLINE_TYPE.DAY_K, (9 - i) * 800, 800)
                ) for i in range(10)
            ], axis=0)
 
        data = data.assign(date=data['datetime'].apply(lambda x: str(x)[0:10]))\
            .assign(code=str(code))\
            .set_index('date', drop=False, inplace=False)\
            .drop(['datetime'], axis=1)[start_date:end_date]
        return data.assign(date=data['date'].apply(lambda x: str(x)[0:10]))

def to_df(v):
    if isinstance(v, list):
        return pd.DataFrame(data=v)
    elif isinstance(v, dict):
        return pd.DataFrame(data=[v, ])
    else:
        return pd.DataFrame(data=[{'value': v}])

if __name__ == "__main__":
    import pprint

    def print_df(data):
        pprint.pprint(to_df(data))

    client = TdxClient()
    if client.connect().login():
        log.info("心跳包")
        print_df(client.call(server.HeartBeat()))
        log.info("获取服务器公告")
        print_df(client.call(server.Announcement()))
        # print_df(client.call(server.TodoFDE()))
        log.info("获取升级提示")
        print_df(client.call(server.UpgradeTip()))
        log.info("获取交易所公告--需要登录")
        print_df(client.call(server.ExchangeAnnouncement()))


        log.info("获取 深市 股票数量")
        print_df(client.get_security_count(MARKET.SZ))
        log.info("获取股票列表")
        print_df(client.get_security_list(MARKET.SZ, 0))
        log.info("另一个获取股票列表")
        print_df(client.call(stock.ListB(MARKET.SZ, 0)))
        log.info("获取k线")
        print_df(client.get_security_bars(MARKET.SZ, '000001', KLINE_TYPE.DAY_K, 0, 500))
        log.info("获取指数k线")
        print_df(client.get_security_bars(MARKET.SH, '999999', KLINE_TYPE.DAY_K, 0, 2000))
        log.info("查询分时行情")
        print_df(client.get_orders(MARKET.SZ, '000001'))
        log.info("查询历史分时行情")
        print_df(client.get_history_orders(MARKET.SZ, '000001', date(2025, 6, 5)))
        log.info("查询分时成交")
        print_df(client.get_transaction(MARKET.SZ, '000001'))
        log.info("查询历史分时成交")
        print_df(client.get_history_transaction(MARKET.SZ, '000001', date(2025, 6, 5)))
        log.info("查询公司信息")
        print_df(client.get_company_info(MARKET.SZ, '000001'))
        log.info("日线级别k线获取函数")
        pprint.pprint(client.get_k_data('000001', '2017-07-01', '2017-07-10'))
        log.info("获取板块信息")
        pprint.pprint(client.get_block_info(BLOCK_FILE_TYPE.ZS))
        log.info("获取报告文件")
        print(client.get_report_file('tdxzsbase.cfg'))
                
        log.info("获取分时图缩略数据")
        chart = client.call(stock.ChartSampling(MARKET.SZ, '000001'))
        import matplotlib.pyplot as plt
        chart = pd.Series(chart['prices'])
        chart.plot()
        plt.show()


        log.info("获取简略行情")
        print_df(client.get_security_quotes([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')]))
        log.info("获取详细行情")
        print_df(client.call(stock.QuotesDetail([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SZ, '000004'), (MARKET.SZ, '000006'), (MARKET.SZ, '000007'), (MARKET.SZ, '000008'), (MARKET.SZ, '000009')
        , (MARKET.SZ, '000010'), (MARKET.SZ, '000011'), (MARKET.SZ, '000012'), (MARKET.SZ, '000014'), (MARKET.SZ, '000016'), (MARKET.SZ, '000017')])))
        log.info("获取行情列表")
        print_df(client.call(stock.QuotesList(CATEGORY.SZ, 0)))
        log.info("获取行情全景")
        print_df(client.call(stock.TopStocksBoard(CATEGORY.A)))

        # print_df(client.call(stock.TODO547([(MARKET.SZ, '000001')])))
        # print_df(client.call(stock.TODO547([(MARKET.SZ, '000001'), (MARKET.SZ, '000002')])))
        # print_df(client.call(stock.TODO547([(MARKET.SH, '600009'), (MARKET.SH, '600009')])))
        # print_df(client.call(stock.TODO547([(MARKET.SZ, '000001'), (MARKET.SZ, '000002'), (MARKET.SH, '999998'), (MARKET.SH, '999997')])))
        
        
        log.info("获取指数概况")
        print_df(client.call(stock.IndexInfo(MARKET.SH, '999999')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399001')))
        # print_df(client.call(stock.IndexInfo(MARKET.BJ, '899050')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399006')))
        # print_df(client.call(stock.IndexInfo(MARKET.SH, '000688')))
        # print_df(client.call(stock.IndexInfo(MARKET.SH, '880008')))
        # print_df(client.call(stock.IndexInfo(MARKET.SH, '000888')))
        # print_df(client.call(stock.IndexInfo(MARKET.SH, '000680')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399330')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399673')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399106')))
        # print_df(client.call(stock.IndexInfo(MARKET.SZ, '399102')))

        log.info("获取指数k线")
        data = client.call(stock.IndexChartSampling(MARKET.SZ, '399006'))
        import matplotlib.pyplot as plt
        df = pd.DataFrame(data)
        print(df)
        fig, ax1 = plt.subplots(figsize=(14, 7))
        ax2 = ax1.twinx()
        # 绘制price曲线
        ax1.plot(df.index, df['price'])
        # 绘制fast曲线（等于price的100倍）
        ax1.plot(df.index, df['fast'] / 100)
        # 绘制amount柱状图
        ax2.bar(df.index, df['amount'])
        plt.show()

        log.info("获取异动")
        print_df(client.call(stock.Unusual(MARKET.SZ, 3000, 400)))
        print_df(client.call(stock.Unusual(MARKET.SH, 5750)))

        client.disconnect()