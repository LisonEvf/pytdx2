from datetime import date

from opentdx.const import (
    BLOCK_FILE_TYPE,
    CATEGORY,
    MARKET,
    PERIOD,
)


class TestQuotationClientLogin:
    """登录和心跳"""

    def test_connected(self, qc):
        assert qc.connected is True

    def test_heartbeat(self, qc):
        result = qc.do_heartbeat()
        assert result is not None


class TestQuotationClientStock:
    """A 股行情 API"""

    def test_get_count(self, qc):
        result = qc.get_count(MARKET.SZ)
        assert isinstance(result, int)
        assert result > 0

    def test_get_count_sh(self, qc):
        result = qc.get_count(MARKET.SH)
        assert isinstance(result, int)
        assert result > 0

    def test_get_list(self, qc):
        result = qc.get_list(MARKET.SZ, start=0, count=5)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'code' in result[0] and 'name' in result[0]

    def test_get_kline(self, qc):
        result = qc.get_kline(MARKET.SH, '000001', PERIOD.DAILY, count=10)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'datetime' in result[0]

    def test_get_quotes(self, qc):
        result = qc.get_quotes(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'code' in result[0]

    def test_get_quotes_multi(self, qc):
        result = qc.get_quotes([(MARKET.SZ, '000001'), (MARKET.SH, '600000')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_stock_quotes_details(self, qc):
        result = qc.get_stock_quotes_details(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'handicap' in result[0]

    def test_get_stock_quotes_details_multi(self, qc):
        result = qc.get_stock_quotes_details([(MARKET.SZ, '000001'), (MARKET.SH, '600000')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_stock_top_board(self, qc):
        result = qc.get_stock_top_board(CATEGORY.A)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_stock_quotes_list(self, qc):
        result = qc.get_stock_quotes_list(CATEGORY.A, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_stock_quotes_list_all(self, qc):
        result = qc.get_stock_quotes_list(CATEGORY.A, count=0)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_tick_chart(self, qc):
        result = qc.get_tick_chart(MARKET.SH, '999999')
        assert isinstance(result, list)

    def test_get_transaction(self, qc):
        result = qc.get_transaction(MARKET.SZ, '000001')
        assert isinstance(result, list)

    def test_get_transaction_history(self, qc):
        result = qc.get_transaction(MARKET.SZ, '000001', date(2026, 4, 10))
        assert isinstance(result, list)

    def test_get_company_info(self, qc):
        result = qc.get_company_info(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'name' in result[0]

    def test_get_auction(self, qc):
        result = qc.get_auction(MARKET.SZ, '300308')
        assert isinstance(result, list)

    def test_get_unusual(self, qc):
        result = qc.get_unusual(MARKET.SZ)
        assert isinstance(result, list)

    def test_get_unusual_all(self, qc):
        result = qc.get_unusual(MARKET.SZ, count=0)
        assert isinstance(result, list)

    def test_get_index_info(self, qc):
        result = qc.get_index_info(MARKET.SH, '999999')
        assert isinstance(result, list)

    def test_get_index_info_multi(self, qc):
        result = qc.get_index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_index_momentum(self, qc):
        result = qc.get_index_momentum(MARKET.SH, '999999')
        assert isinstance(result, list)

    def test_get_vol_profile(self, qc):
        result = qc.get_vol_profile(MARKET.SZ, '000001')
        assert result is None or isinstance(result, list)

    def test_get_chart_sampling(self, qc):
        result = qc.get_chart_sampling(MARKET.SZ, '000001')
        assert isinstance(result, list)

    def test_get_block_file(self, qc):
        result = qc.get_block_file(BLOCK_FILE_TYPE.DEFAULT)
        assert result is not None
        assert isinstance(result, list)

    def test_get_history_orders(self, qc):
        result = qc.get_history_orders(MARKET.SZ, '000001', date(2026, 4, 10))
        assert isinstance(result, list)


class TestQuotationClientQuotesAdjustment:
    """quotes_adjustment 数据处理（内联数据）"""

    def test_quotes_adjustment(self, qc):
        data = [{
            'high': 100000, 'low': 99000, 'open': 99500,
            'close': 100000, 'pre_close': 99500, 'neg_price': -100,
            'open_amount': 100, 'rise_speed': 500,
            'handicap': {'bid': [{'price': 99500, 'vol': 100}], 'ask': [{'price': 100000, 'vol': 100}]},
            'market': None, 'code': None, 'vol': 0,
        }]
        result = qc.quotes_adjustment(data)
        assert len(result) == 1
        assert result[0]['close'] == 1000.0
        assert result[0]['rise_speed'] == '5.00%'
        assert result[0]['handicap']['bid'][0]['price'] == 995.0
        assert 'turnover' not in result[0]
