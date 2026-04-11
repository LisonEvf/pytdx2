import pytest

from client.macQuotationClient import macQuotationClient, macExQuotationClient
from const import *
from tests.conftest import make_mock_call


class TestMacQuotationClient:

    def test_get_board_count(self, mqc):
        mqc.call = make_mock_call({'count': 100})
        result = mqc.get_board_count(BOARD_TYPE.HY)
        assert result == {'count': 100}

    def test_get_board_list(self, mqc):
        mock_data = [{'code': '880001', 'name': '煤炭'}]
        mqc.call = make_mock_call(mock_data)
        result = mqc.get_board_list(BOARD_TYPE.HY)
        assert len(result) == 1
        assert result[0]['code'] == '880001'

    def test_get_board_list_pagination(self, mqc):
        """分页：MAX_LIST_COUNT=150"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            return [{'code': f'880{i:03d}', 'name': f'板块{i}'} for i in range(150)]
        mqc.call = mock_call
        result = mqc.get_board_list(BOARD_TYPE.HY, count=300)
        assert len(result) == 300
        assert call_count[0] == 2  # range(0, 300, 150) -> [0, 150]

    def test_get_board_list_ex_board_type(self, mqc):
        """测试扩展板块类型"""
        mqc.call = make_mock_call([{'code': 'HK0281', 'name': '港股科技'}])
        result = mqc.get_board_list(EX_BOARD_TYPE.HK_ALL)
        assert len(result) == 1

    def test_get_board_members_quotes(self, mqc):
        mqc.call = make_mock_call({'stocks': [{'market': 1, 'code': '600000', 'price': 10.0}]})
        result = mqc.get_board_members_quotes('880761')
        assert len(result) == 1
        assert result[0]['code'] == '600000'

    def test_get_board_members_quotes_pagination(self, mqc):
        """分页：MAX_LIST_COUNT=80"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            return {'stocks': [{'market': 1, 'code': f'{i:06d}'} for i in range(80)]}
        mqc.call = mock_call
        result = mqc.get_board_members_quotes('880761', count=160)
        assert len(result) == 160
        assert call_count[0] == 2

    def test_get_board_members(self, mqc):
        mqc.call = make_mock_call({'stocks': [{'market': 1, 'code': '000001'}]})
        result = mqc.get_board_members('880761')
        assert len(result) == 1
        assert result[0]['code'] == '000001'

    def test_get_board_members_pagination(self, mqc):
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            if call_count[0] <= 2:
                return {'stocks': [{'market': 1, 'code': f'{i:06d}'} for i in range(80)]}
            return {'stocks': []}
        mqc.call = mock_call
        result = mqc.get_board_members('000683', count=160)
        assert len(result) == 160

    def test_get_symbol_belong_board(self, mqc):
        mqc.call = make_mock_call([{'block_code': '880001', 'block_name': '煤炭'}])
        result = mqc.get_symbol_belong_board('000100', MARKET.SZ)
        assert len(result) == 1

    def test_get_symbol_bars(self, mqc):
        mock_data = [{'date_time': '2026-01-01', 'open': 10.0, 'high': 11.0, 'low': 9.5, 'close': 10.5, 'vol': 1000}]
        mqc.call = make_mock_call(mock_data)
        result = mqc.get_symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=1)
        assert len(result) == 1
        assert result[0]['close'] == 10.5

    def test_get_symbol_bars_pagination(self, mqc):
        """分页：MAX_LIST_COUNT=700"""
        call_count = [0]
        def mock_call(parser):
            call_count[0] += 1
            return [{'date_time': f'2026-01-{i:02d}', 'open': 10.0} for i in range(700)]
        mqc.call = mock_call
        result = mqc.get_symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=1400)
        assert len(result) == 1400
        assert call_count[0] == 2

    def test_get_symbol_bars_with_adjust(self, mqc):
        """测试复权参数"""
        mqc.call = make_mock_call([{'date_time': '2026-01-01', 'open': 10.0, 'close': 10.5, 'vol': 100}])
        result = mqc.get_symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, fq=ADJUST.HFQ, count=1)
        assert len(result) == 1


class TestMacExQuotationClient:

    def test_inherits_mac_methods(self, meqc):
        """macExQuotationClient 继承 macQuotationClient 所有方法"""
        meqc.call = make_mock_call([{'code': 'HK0281', 'name': '港股科技'}])
        result = meqc.get_board_list(EX_BOARD_TYPE.HK_ALL)
        assert len(result) == 1

    def test_get_board_members(self, meqc):
        meqc.call = make_mock_call({'stocks': [{'market': 31, 'code': '00700'}]})
        result = meqc.get_board_members('HK0281')
        assert len(result) == 1

    def test_get_symbol_bars(self, meqc):
        meqc.call = make_mock_call([{'date_time': '2026-01-01', 'open': 400.0, 'close': 410.0, 'vol': 1000}])
        result = meqc.get_symbol_bars(EX_MARKET.HK_MAIN_BOARD, '09988', PERIOD.WEEKLY, count=1)
        assert len(result) == 1

    def test_hosts_is_mac_ex(self):
        """macExQuotationClient 使用 mac_ex_hosts"""
        client = macExQuotationClient()
        from const import mac_ex_hosts
        assert client.hosts == mac_ex_hosts
