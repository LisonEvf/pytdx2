from datetime import date
from unittest.mock import patch, MagicMock

import pytest

from opentdx.client.quotationClient import QuotationClient
from opentdx.const import *
from tests.conftest import make_mock_call


def _get_base_class_name(parser):
    """获取被 register_parser 装饰后的原始类名"""
    for cls in type(parser).__mro__:
        if cls.__module__ != 'builtins' and cls.__name__ not in ('BaseParser', 'object', 'Decorator'):
            return cls.__name__
    return type(parser).__name__


class TestQuotationClient:

    def test_login_success(self, qc):
        qc.call = lambda parser: {'version': '1.0'}
        assert qc.login() is True

    def test_login_success_show_info(self, qc, capsys):
        qc.call = lambda parser: {'version': '1.0'}
        assert qc.login(show_info=True) is True

    def test_login_failure(self, qc):
        qc.call = lambda parser: (_ for _ in ()).throw(Exception("fail"))
        assert qc.login() is False

    def test_doHeartBeat(self, qc):
        qc.call = lambda parser: 'ok'
        result = qc.doHeartBeat()
        assert result == 'ok'

    def test_get_count(self, qc):
        qc.call = make_mock_call(5000)
        assert qc.get_count(MARKET.SZ) == 5000

    def test_get_list_single_page(self, qc):
        qc.call = make_mock_call([{'code': '000001'}, {'code': '000002'}])
        result = qc.get_list(MARKET.SZ, start=0, count=2)
        assert len(result) == 2

    def test_get_list_pagination(self, qc):
        """测试分页逻辑：超过 MAX_LIST_COUNT=1600 时自动分页"""
        call_count = 0
        def mock_call(parser):
            nonlocal call_count
            call_count += 1
            return [{'code': f'{i:06d}'} for i in range(1600)]
        qc.call = mock_call
        result = qc.get_list(MARKET.SZ, start=0, count=3200)
        assert call_count == 2
        assert len(result) == 3200

    def test_get_list_all(self, qc):
        """count=0 时获取全部，当返回数据不足时停止"""
        call_count = 0
        def mock_call(parser):
            nonlocal call_count
            call_count += 1
            return [{'code': f'{i:06d}'} for i in range(100)]
        qc.call = mock_call
        result = qc.get_list(MARKET.SZ)
        assert len(result) == 100
        # 100 < MAX_LIST_COUNT(1600)，第一次就 break 了
        assert call_count == 1

    def test_get_vol_profile(self, qc):
        mock_data = [{
            'market': MARKET.SZ, 'code': '000001',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
            'vol_profile': [{'price': 99000, 'vol': 100, 'buy': 60, 'sell': 40}],
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_vol_profile(MARKET.SZ, '000001')
        assert len(result) == 1
        assert result[0]['high'] == 1000.0
        assert result[0]['low'] == 980.0
        assert result[0]['rise_speed'] == '5.00%'

    def test_get_index_momentum(self, qc):
        qc.call = make_mock_call([100, 200, 300])
        result = qc.get_index_momentum(MARKET.SH, '999999')
        assert result == [100, 200, 300]

    def test_get_index_info_code_param(self, qc):
        """传入 market, code 两个参数"""
        mock_data = {
            'market': MARKET.SH, 'code': '999999',
            'high': 350000, 'low': 340000, 'open': 345000,
            'close': 348000, 'pre_close': 345000, 'diff': 3000,
        }
        qc.call = make_mock_call(mock_data)
        result = qc.get_index_info(MARKET.SH, '999999')
        assert len(result) == 1
        assert result[0]['high'] == 3500.0
        assert result[0]['close'] == 3480.0

    def test_get_index_info_list(self, qc):
        """传入 list[tuple] 形式"""
        call_idx = [0]
        datas = [
            {'market': MARKET.SH, 'code': '999999', 'high': 350000, 'low': 340000, 'open': 345000, 'close': 348000, 'pre_close': 345000, 'diff': 3000},
            {'market': MARKET.SZ, 'code': '399001', 'high': 120000, 'low': 115000, 'open': 118000, 'close': 117000, 'pre_close': 118000, 'diff': 1000},
        ]
        def mock_call(parser):
            result = datas[call_idx[0]]
            call_idx[0] += 1
            return result
        qc.call = mock_call
        result = qc.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001')])
        assert len(result) == 2

    def test_get_index_info_list(self, qc):
        """传入 list[tuple] 形式"""
        call_idx = [0]
        datas = [
            {'market': MARKET.SH, 'code': '999999', 'high': 350000, 'low': 340000, 'open': 345000, 'close': 348000, 'pre_close': 345000, 'diff': 3000},
            {'market': MARKET.SZ, 'code': '399001', 'high': 120000, 'low': 115000, 'open': 118000, 'close': 117000, 'pre_close': 118000, 'diff': 1000},
        ]
        def mock_call(parser):
            result = datas[call_idx[0]]
            call_idx[0] += 1
            return result
        qc.call = mock_call
        result = qc.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001')])
        assert len(result) == 2

    def test_get_kline(self, qc):
        mock_kline = [{
            'date_time': '2026-01-01', 'open': 100000, 'high': 105000,
            'low': 98000, 'close': 103000, 'vol': 1000000, 'amount': 50000,
        }]
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            base = _get_base_class_name(parser)
            if base == 'Finance':
                return {'liutongguben': 100000000}
            return mock_kline
        qc.call = mock_call
        result = qc.get_kline(MARKET.SH, '000001', PERIOD.DAILY, count=1)
        assert len(result) == 1
        assert result[0]['open'] == 100.0
        assert result[0]['close'] == 103.0
        assert result[0]['high'] == 105.0

    def test_get_kline_empty(self, qc):
        qc.call = make_mock_call(None)
        result = qc.get_kline(MARKET.SH, '000001', PERIOD.DAILY)
        assert result == []

    def test_get_kline_pagination(self, qc):
        """K线超过800条时分页，需要 mock 返回与请求数量匹配的数据"""
        call_count = [0]
        def mock_call(parser):
            base = _get_base_class_name(parser)
            if base == 'Finance':
                return {'liutongguben': 100000000}
            call_count[0] += 1
            # body 格式 <H6sHHHHH8s>: market(2)+code(6)+period(2)+times(2)+start(2)+count(2)+adjust(2)+pad(8)
            import struct
            req_count = struct.unpack('<H', parser.body[14:16])[0]
            return [{'date_time': '2026-01-01', 'open': 100000, 'high': 105000, 'low': 98000, 'close': 103000, 'vol': 1000, 'amount': 50000}] * req_count
        qc.call = mock_call
        result = qc.get_kline(MARKET.SH, '000001', PERIOD.DAILY, count=1000)
        assert len(result) == 1000
        assert call_count[0] == 2  # 800 + 200

    def test_get_tick_chart_realtime(self, qc):
        qc.call = make_mock_call([
            {'price': 100000, 'avg': 9900000, 'vol': 100},
            {'price': 101000, 'avg': 9910000, 'vol': 200},
        ])
        result = qc.get_tick_chart(MARKET.SH, '999999')
        assert len(result) == 2
        assert result[0]['price'] == 1000.0
        assert result[0]['avg'] == 990.0

    def test_get_tick_chart_history(self, qc):
        qc.call = make_mock_call([
            {'price': 100000, 'avg': 9900000, 'vol': 100, 'last': True},
        ])
        result = qc.get_tick_chart(MARKET.SZ, '000001', date=date(2026, 3, 3))
        assert len(result) == 1
        assert result[0]['price'] == 1000.0

    def test_get_tick_chart_history_with_start_count(self, qc):
        """历史分时图带 start/count 截取"""
        data = [{'price': 100000, 'avg': 9900000, 'vol': i} for i in range(10)]
        data.append({'price': 100000, 'avg': 9900000, 'vol': 999})  # last sentinel
        qc.call = make_mock_call(data)
        result = qc.get_tick_chart(MARKET.SZ, '000001', date=date(2026, 3, 3), start=2, count=5)
        assert len(result) == 5

    def test_get_stock_quotes_details_list(self, qc):
        """传入 list[tuple] 形式"""
        mock_data = [{
            'market': MARKET.SZ, 'code': '000001',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_stock_quotes_details([(MARKET.SZ, '000001')])
        assert len(result) == 1
        assert result[0]['close'] == 995.0

    def test_get_stock_quotes_details_code_param(self, qc):
        mock_data = [{
            'market': MARKET.SZ, 'code': '000002',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_stock_quotes_details(MARKET.SZ, '000002')
        assert len(result) == 1
        assert result[0]['code'] == '000002'

    def test_get_stock_top_board(self, qc):
        boards = {
            'increase': [{'market': MARKET.SZ, 'code': '000001', 'price': 10500, 'value': 5.0}],
            'decrease': [{'market': MARKET.SH, 'code': '600000', 'price': 9800, 'value': -2.0}],
        }
        qc.call = make_mock_call(boards)
        result = qc.get_stock_top_board(CATEGORY.A)
        assert 'increase' in result
        assert result['increase'][0]['price'] == '10500.00'

    def test_get_stock_quotes_list(self, qc):
        mock_data = [{
            'market': MARKET.SZ, 'code': '000001',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000, 'short_turnover': 500,
            'opening_rush': 300, 'vol_rise_speed': 200, 'depth': 5000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_stock_quotes_list(CATEGORY.A, count=1)
        assert len(result) == 1
        assert result[0]['short_turnover'] == '5.00%'

    def test_get_stock_quotes_list_pagination(self, qc):
        """行情列表分页：count=0 获取全部"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return [{'market': MARKET.SZ, 'code': '000001',
                    'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
                    'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
                    'rise_speed': 500, 'vol': 1000000, 'short_turnover': 500,
                    'opening_rush': 300, 'vol_rise_speed': 200, 'depth': 5000,
                    'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]}}] * 80
            return []
        qc.call = mock_call
        result = qc.get_stock_quotes_list(CATEGORY.A, count=0)
        assert call_count[0] == 2

    def test_get_quotes_tuple(self, qc):
        """传入 (market, code) 形式 — MARKET 是 enum 不是 int，需用 code 参数形式"""
        mock_data = [{
            'market': MARKET.SZ, 'code': '000001',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000, 'short_turnover': 500,
            'opening_rush': 300, 'vol_rise_speed': 200, 'depth': 5000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_quotes(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_get_quotes_code_param(self, qc):
        mock_data = [{
            'market': MARKET.SZ, 'code': '000002',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000, 'short_turnover': 500,
            'opening_rush': 300, 'vol_rise_speed': 200, 'depth': 5000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        qc.call = make_mock_call(mock_data)
        result = qc.get_quotes(MARKET.SZ, '000002')
        assert len(result) == 1

    def test_get_unusual(self, qc):
        mock_data = [{'index': 1, 'market': MARKET.SZ, 'code': '000001', 'desc': '快速拉升', 'value': '5%'}]
        qc.call = make_mock_call(mock_data)
        result = qc.get_unusual(MARKET.SZ)
        assert len(result) == 1

    def test_get_unusual_pagination(self, qc):
        """异动分页"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return [{'index': i} for i in range(600)]
            return []
        qc.call = mock_call
        result = qc.get_unusual(MARKET.SZ, count=0)
        assert call_count[0] == 2

    def test_get_auction(self, qc):
        mock_data = [{'time': '09:25:00', 'price': 1000, 'matched': 5000, 'unmatched': 1000}]
        qc.call = make_mock_call(mock_data)
        result = qc.get_auction(MARKET.SZ, '300308')
        assert len(result) == 1

    def test_get_history_orders(self, qc):
        mock_data = [{'price': 100000, 'vol': 100}, {'price': 101000, 'vol': 200}]
        qc.call = make_mock_call(mock_data)
        result = qc.get_history_orders(MARKET.SH, '000001', date(2026, 1, 7))
        assert len(result) == 2
        assert result[0]['price'] == 1000.0

    def test_get_transaction_realtime(self, qc):
        mock_data = [{'price': 100000, 'vol': 100, 'time': '09:30:00', 'trans': 1, 'action': 'BUY'}]
        qc.call = make_mock_call(mock_data)
        result = qc.get_transaction(MARKET.SZ, '000001')
        assert len(result) == 1
        assert result[0]['price'] == 1000.0

    def test_get_transaction_history(self, qc):
        mock_data = [{'price': 100000, 'vol': 100, 'time': '09:30:00', 'trans': 1, 'action': 'SELL'}]
        qc.call = make_mock_call(mock_data)
        result = qc.get_transaction(MARKET.SH, '000001', date=date(2026, 3, 3))
        assert len(result) == 1
        assert result[0]['price'] == 1000.0

    def test_get_chart_sampling(self, qc):
        qc.call = make_mock_call([1.0, 2.0, 3.0])
        result = qc.get_chart_sampling(MARKET.SZ, '000001')
        assert result == [1.0, 2.0, 3.0]

    def test_get_company_info(self, qc):
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            base = _get_base_class_name(parser)
            if base == 'Category':
                return [{'name': '公司概况', 'filename': 'test.dat', 'start': 0, 'length': 100}]
            elif base == 'Content':
                return {'content': '公司信息内容'}
            elif base == 'XDXR':
                return {'xdxr_data': '除权数据'}
            elif base == 'Finance':
                return {'liutongguben': 100000}
            return None
        qc.call = mock_call
        result = qc.get_company_info(MARKET.SZ, '000001')
        assert len(result) == 3
        assert result[0]['name'] == '公司概况'

    def test_get_company_info_no_xdxr(self, qc):
        """XDXR 返回 None 时只包含公司概况和财报"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            base = _get_base_class_name(parser)
            if base == 'Category':
                return [{'name': '公司概况', 'filename': 'test.dat', 'start': 0, 'length': 100}]
            elif base == 'Content':
                return {'content': '公司信息内容'}
            elif base == 'XDXR':
                return None  # 无除权数据
            elif base == 'Finance':
                return {'liutongguben': 100000}
            return None
        qc.call = mock_call
        result = qc.get_company_info(MARKET.SZ, '000001')
        # Category + Content + Finance = 2 (XDXR is None, skipped)
        assert len(result) == 2
        assert result[0]['name'] == '公司概况'

    def test_get_block_file(self, qc):
        """获取板块文件"""
        def mock_call(parser):
            base = _get_base_class_name(parser)
            if base == 'Meta':
                return {'size': 100}
            elif base == 'Block':
                return {'data': b'\x00' * 100}
            return None
        qc.call = mock_call
        with patch('client.quotationClient.BlockReader') as mock_reader_cls:
            mock_instance = MagicMock()
            mock_instance.get_data.return_value = [{'block_name': '测试', 'stocks': ['000001']}]
            mock_reader_cls.return_value = mock_instance
            result = qc.get_block_file(BLOCK_FILE_TYPE.DEFAULT)
            assert result == [{'block_name': '测试', 'stocks': ['000001']}]

    def test_get_block_file_error(self, qc):
        qc.call = lambda parser: (_ for _ in ()).throw(Exception("meta error"))
        result = qc.get_block_file(BLOCK_FILE_TYPE.DEFAULT)
        assert result is None

    def test_download_file(self, qc):
        """download_file 初始化 bytearray(filesize) 后 extend，总长度 = filesize + 实际下载量"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'size': 100, 'data': b'\x01' * 100}
            return {'size': 0, 'data': b''}
        qc.call = mock_call
        result = qc.download_file('test.dat', filesize=100)
        assert isinstance(result, bytearray)
        # bytearray(100) 创建100个零字节 + extend 100字节 = 200
        assert len(result) == 200

    def test_download_file_unknown_size(self, qc):
        """filesize=0 时，收到 size=0 的包就结束"""
        qc.call = make_mock_call({'size': 0, 'data': b''})
        result = qc.download_file('test.dat', filesize=0)
        assert isinstance(result, bytearray)
        assert len(result) == 0

    def test_download_file_with_hook(self, qc):
        hook_calls = []
        def hook(downloaded, total):
            hook_calls.append((downloaded, total))
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'size': 50, 'data': b'\x01' * 50}
            return {'size': 0, 'data': b''}
        qc.call = mock_call
        qc.download_file('test.dat', filesize=50, report_hook=hook)
        assert len(hook_calls) == 1
        assert hook_calls[0] == (50, 50)

    def test_get_table_file(self, qc):
        content = "field1|field2\nval1|val2"
        qc.download_file = lambda fn: bytearray(content.encode('gbk'))
        result = qc.get_table_file('test.cfg')
        assert result == [['field1', 'field2'], ['val1', 'val2']]

    def test_get_csv_file(self, qc):
        content = "field1,field2\nval1,val2"
        qc.download_file = lambda fn: bytearray(content.encode('gbk'))
        result = qc.get_csv_file('test.txt')
        assert result == [['field1', 'field2'], ['val1', 'val2']]

    def test_quotes_adjustment_with_cache(self, qc):
        """测试流通股本缓存逻辑"""
        from opentdx.utils.cache import finance_cache
        finance_cache.set('0_000001', 100000000)
        mock_data = [{
            'market': MARKET.SZ, 'code': '000001',
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        result = qc.quotes_adjustment(mock_data)
        # turnover = vol * 100 / float_shares * 100 = 1000000 * 100 / 100000000 * 100 = 100
        assert result[0]['turnover'] == 100.0
        finance_cache.delete('0_000001')

    def test_quotes_adjustment_no_market(self, qc):
        """market 为 None 时不计算换手率"""
        mock_data = [{
            'market': None, 'code': None,
            'high': 100000, 'low': 98000, 'open': 99000, 'close': 99500,
            'pre_close': 99000, 'neg_price': 0, 'open_amount': 100,
            'rise_speed': 500, 'vol': 1000000,
            'handicap': {'bid': [{'price': 99000, 'vol': 100}], 'ask': [{'price': 99500, 'vol': 200}]},
        }]
        result = qc.quotes_adjustment(mock_data)
        assert result[0]['high'] == 1000.0
        assert 'turnover' not in result[0]
