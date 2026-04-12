from datetime import date

from opentdx.const import *
from tests.conftest import make_mock_call


class TestExQuotationClient:

    def test_login_success(self, eqc):
        eqc.call = lambda parser: {'version': '1.0'}
        assert eqc.login() is True

    def test_login_failure(self, eqc):
        eqc.call = lambda parser: (_ for _ in ()).throw(Exception("fail"))
        assert eqc.login() is False

    def test_server_info(self, eqc):
        eqc.call = make_mock_call({'version': '2.0', 'count': 100})
        result = eqc.server_info()
        assert result == {'version': '2.0', 'count': 100}

    def test_server_info_error(self, eqc):
        eqc.call = lambda parser: (_ for _ in ()).throw(Exception("err"))
        result = eqc.server_info()
        assert result is None

    def test_get_count(self, eqc):
        eqc.call = make_mock_call(5000)
        assert eqc.get_count() == 5000

    def test_get_category_list(self, eqc):
        eqc.call = make_mock_call([{'market': 1, 'code': 'A', 'name': 'test', 'abbr': 'T'}])
        result = eqc.get_category_list()
        assert len(result) == 1
        assert result[0]['code'] == 'A'

    def test_get_list(self, eqc):
        eqc.call = make_mock_call([{'market': 1, 'code': 'TSLA', 'name': 'Tesla'}])
        result = eqc.get_list()
        assert len(result) == 1

    def test_get_quotes_list(self, eqc):
        mock_data = [{'market': EX_MARKET.US_STOCK, 'code': 'TSLA', 'open': 200.0, 'close': 210.0}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_quotes_list(EX_MARKET.US_STOCK)
        assert len(result) == 1

    def test_get_quotes_list_pagination(self, eqc):
        """分页：count=0 获取全部"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return [{'market': EX_MARKET.US_STOCK, 'code': f'{i}'} for i in range(100)]
            return []
        eqc.call = mock_call
        result = eqc.get_quotes_list(EX_MARKET.US_STOCK, count=0)
        assert call_count[0] == 2

    def test_get_quotes_single(self, eqc):
        eqc.call = make_mock_call({'market': EX_MARKET.US_STOCK, 'code': 'TSLA', 'close': 210.0})
        result = eqc.get_quotes_single(EX_MARKET.US_STOCK, 'TSLA')
        assert result['code'] == 'TSLA'

    def test_get_quotes_list_param(self, eqc):
        """传入 list[tuple] 形式"""
        mock_data = [
            {'market': EX_MARKET.CFFEX_FUTURES, 'code': 'IC2602'},
            {'market': EX_MARKET.CFFEX_FUTURES, 'code': 'IC2603'},
        ]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_quotes([
            (EX_MARKET.CFFEX_FUTURES, 'IC2602'),
            (EX_MARKET.CFFEX_FUTURES, 'IC2603'),
        ])
        assert len(result) == 2

    def test_get_quotes_code_param(self, eqc):
        """传入 market, code 两个参数"""
        eqc.call = make_mock_call([{'market': EX_MARKET.US_STOCK, 'code': 'TSLA'}])
        result = eqc.get_quotes(EX_MARKET.US_STOCK, 'TSLA')
        assert len(result) == 1

    def test_get_quotes2(self, eqc):
        """get_quotes2 的 code 参数是必填的"""
        mock_data = [{'market': EX_MARKET.CFFEX_FUTURES, 'code': 'IC2602'}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_quotes2(EX_MARKET.CFFEX_FUTURES, 'IC2602')
        assert len(result) == 1

    def test_get_quotes2_list(self, eqc):
        """传入 list[tuple] 形式"""
        mock_data = [{'market': EX_MARKET.CFFEX_FUTURES, 'code': 'IC2603'}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_quotes2([(EX_MARKET.CFFEX_FUTURES, 'IC2603')], None)
        assert len(result) == 1

    def test_get_kline(self, eqc):
        mock_data = [{'date_time': '2026-01-01', 'open': 200.0, 'high': 210.0, 'low': 195.0, 'close': 205.0, 'vol': 1000, 'amount': 50000}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY)
        assert len(result) == 1
        assert result[0]['close'] == 205.0

    def test_get_history_transaction(self, eqc):
        mock_data = [{'time': '10:00:00', 'price': 200.0, 'vol': 100, 'action': 'BUY'}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_history_transaction(EX_MARKET.US_STOCK, 'TSLA', date(2025, 10, 28))
        assert len(result) == 1

    def test_get_table(self, eqc):
        """多段拼接"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return ('ctx', 50, '第一段')
            return ('ctx', 0, '')
        eqc.call = mock_call
        result = eqc.get_table()
        assert result == '第一段'
        assert call_count[0] == 2

    def test_get_table_detail(self, eqc):
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return ('ctx', 30, '详情数据')
            return ('ctx', 0, '')
        eqc.call = mock_call
        result = eqc.get_table_detail()
        assert result == '详情数据'

    def test_get_tick_chart_realtime(self, eqc):
        mock_data = [{'time': '10:00:00', 'price': 200.0, 'avg': 198.0, 'vol': 100}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_tick_chart(EX_MARKET.HK_MAIN_BOARD, '09988')
        assert len(result) == 1

    def test_get_tick_chart_history(self, eqc):
        mock_data = [{'time': '10:00:00', 'price': 200.0, 'avg': 198.0, 'vol': 100}]
        eqc.call = make_mock_call(mock_data)
        result = eqc.get_tick_chart(EX_MARKET.US_STOCK, 'HIMS', date=date(2026, 3, 12))
        assert len(result) == 1

    def test_get_chart_sampling(self, eqc):
        eqc.call = make_mock_call([1.0, 2.0, 3.0, 4.0])
        result = eqc.get_chart_sampling(EX_MARKET.HK_MAIN_BOARD, '09988')
        assert result == [1.0, 2.0, 3.0, 4.0]

    def test_download_file(self, eqc):
        """download_file 初始化 bytearray(filesize) 后 extend，总长度 = filesize + 实际下载量"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'size': 50, 'data': b'\x02' * 50}
            return {'size': 0, 'data': b''}
        eqc.call = mock_call
        result = eqc.download_file('cfg/test.txt', filesize=50)
        assert isinstance(result, bytearray)
        assert len(result) == 100  # bytearray(50) + extend 50

    def test_download_file_zero_retry(self, eqc):
        """filesize>0 但连续收到 size=0 超过2次后停止"""
        eqc.call = make_mock_call({'size': 0, 'data': b''})
        result = eqc.download_file('test.txt', filesize=100)
        assert isinstance(result, bytearray)
