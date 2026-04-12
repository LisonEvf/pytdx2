from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from opentdx.tdxClient import TdxClient
from opentdx.const import *


@pytest.fixture
def tdx():
    """创建一个 mock 好的 TdxClient 实例，不真正连接"""
    client = TdxClient.__new__(TdxClient)
    client.quotation_client = MagicMock()
    client.ex_quotation_client = MagicMock()
    return client


class TestTdxClientContextManager:

    def test_enter(self):
        with patch('tdxClient.QuotationClient') as MockQC, \
             patch('tdxClient.exQuotationClient') as MockEQC:
            mock_qc = MagicMock()
            mock_eqc = MagicMock()
            MockQC.return_value = mock_qc
            MockEQC.return_value = mock_eqc
            MockQC.__bool__ = MagicMock(return_value=True)
            MockEQC.__bool__ = MagicMock(return_value=True)

            with TdxClient() as client:
                assert client is not None
                MockQC.assert_called_once_with(True, True)
                MockEQC.assert_called_once_with(True, True)

    def test_exit_disconnects(self):
        with patch('tdxClient.QuotationClient') as MockQC, \
             patch('tdxClient.exQuotationClient') as MockEQC:
            mock_qc = MagicMock(connected=True)
            mock_eqc = MagicMock(connected=True)
            MockQC.return_value = mock_qc
            MockEQC.return_value = mock_eqc

            with TdxClient() as client:
                pass
            mock_qc.disconnect.assert_called_once()
            mock_eqc.disconnect.assert_called_once()

    def test_exit_not_connected(self):
        with patch('tdxClient.QuotationClient') as MockQC, \
             patch('tdxClient.exQuotationClient') as MockEQC:
            mock_qc = MagicMock(connected=False)
            mock_eqc = MagicMock(connected=False)
            MockQC.return_value = mock_qc
            MockEQC.return_value = mock_eqc

            with TdxClient() as client:
                pass
            mock_qc.disconnect.assert_not_called()
            mock_eqc.disconnect.assert_not_called()


class TestTdxClientStockMethods:

    def test_stock_count(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_count.return_value = 5000
        result = tdx.stock_count(MARKET.SZ)
        assert result == 5000

    def test_stock_list(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_list.return_value = [{'code': '000001', 'name': '平安银行'}]
        result = tdx.stock_list(MARKET.SZ)
        assert len(result) == 1

    def test_stock_vol_profile(self, tdx):
        tdx.quotation_client.connected = True
        mock_data = [{'market': MARKET.SZ, 'code': '000001', 'high': 100.0}]
        tdx.q_client().get_vol_profile.return_value = mock_data
        result = tdx.stock_vol_profile(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_index_momentum(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_index_momentum.return_value = [100, 200, 300]
        result = tdx.index_momentum(MARKET.SH, '999999')
        assert result == [100, 200, 300]

    def test_index_info(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_index_info.return_value = [{'market': MARKET.SH, 'code': '999999', 'close': 3000.0}]
        result = tdx.index_info([(MARKET.SH, '999999')])
        assert len(result) == 1

    def test_stock_kline(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_kline.return_value = [{'date_time': '2026-01-01', 'open': 10.0, 'close': 10.5}]
        result = tdx.stock_kline(MARKET.SH, '000001', PERIOD.DAILY)
        assert len(result) == 1

    def test_stock_tick_chart(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_tick_chart.return_value = [{'price': 10.0, 'avg': 10.2, 'vol': 100}]
        result = tdx.stock_tick_chart(MARKET.SH, '999999')
        assert len(result) == 1

    def test_stock_tick_chart_history(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_tick_chart.return_value = [{'price': 10.0, 'avg': 10.2, 'vol': 100}]
        result = tdx.stock_tick_chart(MARKET.SZ, '000001', date=date(2026, 3, 3))
        assert len(result) == 1

    def test_stock_quotes_detail(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_stock_quotes_details.return_value = [{'market': MARKET.SZ, 'code': '000001'}]
        result = tdx.stock_quotes_detail(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_stock_quotes_detail_list(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_stock_quotes_details.return_value = [
            {'market': MARKET.SZ, 'code': '000001'},
            {'market': MARKET.SZ, 'code': '000002'},
        ]
        result = tdx.stock_quotes_detail([(MARKET.SZ, '000001'), (MARKET.SZ, '000002')])
        assert len(result) == 2

    def test_stock_top_board(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_stock_top_board.return_value = {'increase': [{'code': '000001', 'price': '10.50'}]}
        result = tdx.stock_top_board(CATEGORY.A)
        assert 'increase' in result

    def test_stock_quotes_list(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_stock_quotes_list.return_value = [{'code': '000001'}]
        result = tdx.stock_quotes_list(CATEGORY.A)
        assert len(result) == 1

    def test_stock_quotes_list_with_sort(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_stock_quotes_list.return_value = [{'code': '000001'}]
        result = tdx.stock_quotes_list(CATEGORY.A, sortType=SORT_TYPE.TOTAL_AMOUNT)
        assert len(result) == 1

    def test_stock_quotes(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_quotes.return_value = [{'code': '000001'}]
        result = tdx.stock_quotes(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_stock_unusual(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_unusual.return_value = [{'desc': '快速拉升'}]
        result = tdx.stock_unusual(MARKET.SZ)
        assert len(result) == 1

    def test_stock_auction(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_auction.return_value = [{'time': '09:25:00', 'price': 10.0}]
        result = tdx.stock_auction(MARKET.SZ, '300308')
        assert len(result) == 1

    def test_stock_history_orders(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_history_orders.return_value = [{'price': 10.0, 'vol': 100}]
        result = tdx.stock_history_orders(MARKET.SZ, '000001', date(2026, 1, 7))
        assert len(result) == 1

    def test_stock_transaction(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_transaction.return_value = [{'price': 10.0, 'vol': 100}]
        result = tdx.stock_transaction(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_stock_transaction_history(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_transaction.return_value = [{'price': 10.0, 'vol': 100}]
        result = tdx.stock_transaction(MARKET.SZ, '000001', date=date(2026, 3, 3))
        assert len(result) == 1

    def test_stock_chart_sampling(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_chart_sampling.return_value = [1.0, 2.0, 3.0]
        result = tdx.stock_chart_sampling(MARKET.SZ, '000001')
        assert result == [1.0, 2.0, 3.0]

    def test_stock_f10(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_company_info.return_value = [{'name': '公司概况', 'content': '信息'}]
        result = tdx.stock_f10(MARKET.SZ, '000001')
        assert len(result) == 1

    def test_stock_block(self, tdx):
        tdx.quotation_client.connected = True
        tdx.q_client().get_block_file.return_value = [{'block_name': '煤炭', 'stocks': ['600000']}]
        result = tdx.stock_block(BLOCK_FILE_TYPE.DEFAULT)
        assert len(result) == 1
        assert result[0]['block_name'] == '煤炭'


class TestTdxClientGoodsMethods:

    def test_goods_count(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_count.return_value = 3000
        result = tdx.goods_count()
        assert result == 3000

    def test_goods_category_list(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_category_list.return_value = [{'market': 1, 'code': 'A'}]
        result = tdx.goods_category_list()
        assert len(result) == 1

    def test_goods_list(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_list.return_value = [{'code': 'TSLA', 'name': 'Tesla'}]
        result = tdx.goods_list()
        assert len(result) == 1

    def test_goods_quotes_list(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_quotes_list.return_value = [{'market': EX_MARKET.US_STOCK, 'code': 'TSLA'}]
        result = tdx.goods_quotes_list(EX_MARKET.US_STOCK)
        assert len(result) == 1

    def test_goods_quotes(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_quotes.return_value = [{'market': EX_MARKET.US_STOCK, 'code': 'TSLA'}]
        result = tdx.goods_quotes(EX_MARKET.US_STOCK, 'TSLA')
        assert len(result) == 1

    def test_goods_quotes_list_param(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_quotes.return_value = [
            {'market': EX_MARKET.US_STOCK, 'code': 'TSLA'},
            {'market': EX_MARKET.HK_MAIN_BOARD, 'code': '09988'},
        ]
        result = tdx.goods_quotes([(EX_MARKET.US_STOCK, 'TSLA'), (EX_MARKET.HK_MAIN_BOARD, '09988')])
        assert len(result) == 2

    def test_goods_kline(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_kline.return_value = [{'date_time': '2026-01-01', 'open': 200.0, 'close': 205.0}]
        result = tdx.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY)
        assert len(result) == 1

    def test_goods_history_transaction(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_history_transaction.return_value = [{'price': 200.0, 'vol': 100}]
        result = tdx.goods_history_transaction(EX_MARKET.US_STOCK, 'TSLA', date(2026, 3, 3))
        assert len(result) == 1

    def test_goods_tick_chart(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_tick_chart.return_value = [{'price': 200.0, 'avg': 198.0, 'vol': 100}]
        result = tdx.goods_tick_chart(EX_MARKET.US_STOCK, 'TSLA')
        assert len(result) == 1

    def test_goods_tick_chart_history(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_tick_chart.return_value = [{'price': 200.0, 'avg': 198.0, 'vol': 100}]
        result = tdx.goods_tick_chart(EX_MARKET.US_STOCK, 'TSLA', date=date(2026, 3, 3))
        assert len(result) == 1

    def test_goods_chart_sampling(self, tdx):
        tdx.ex_quotation_client.connected = True
        tdx.eq_client().get_chart_sampling.return_value = [1.0, 2.0]
        result = tdx.goods_chart_sampling(EX_MARKET.HK_MAIN_BOARD, '09988')
        assert result == [1.0, 2.0]


class TestTdxClientAutoConnect:

    def test_q_client_auto_connect(self, tdx):
        """quotation_client 未连接时自动连接并登录"""
        tdx.quotation_client.connected = False
        tdx.quotation_client.connect.return_value = tdx.quotation_client
        tdx.quotation_client.login.return_value = True
        client = tdx.q_client()
        tdx.quotation_client.connect.assert_called_once()
        tdx.quotation_client.login.assert_called_once()

    def test_eq_client_auto_connect(self, tdx):
        """ex_quotation_client 未连接时自动连接并登录"""
        tdx.ex_quotation_client.connected = False
        tdx.ex_quotation_client.connect.return_value = tdx.ex_quotation_client
        tdx.ex_quotation_client.login.return_value = True
        client = tdx.eq_client()
        tdx.ex_quotation_client.connect.assert_called_once()
        tdx.ex_quotation_client.login.assert_called_once()
