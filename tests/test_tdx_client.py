from datetime import date

from opentdx.const import (
    ADJUST,
    BLOCK_FILE_TYPE,
    CATEGORY,
    EX_MARKET,
    MARKET,
    PERIOD,
    SORT_TYPE,
)


class TestTdxClientStock:
    """TdxClient A股相关 API"""

    def test_stock_count(self, tdx):
        result = tdx.stock_count(MARKET.SZ)
        assert isinstance(result, int)
        assert result > 0

    def test_stock_list(self, tdx):
        result = tdx.stock_list(MARKET.SZ, start=0, count=5)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'code' in result[0] and 'name' in result[0]

    def test_stock_kline(self, tdx):
        result = tdx.stock_kline(MARKET.SH, '000001', PERIOD.DAILY, count=10)
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'datetime' in result[0] and 'open' in result[0]

    def test_stock_kline_with_adjust(self, tdx):
        result = tdx.stock_kline(MARKET.SH, '000001', PERIOD.DAILY, count=5, adjust=ADJUST.QFQ)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_stock_quotes(self, tdx):
        result = tdx.stock_quotes(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'code' in result[0]

    def test_stock_quotes_multi(self, tdx):
        result = tdx.stock_quotes([(MARKET.SZ, '000001'), (MARKET.SH, '600000')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_stock_quotes_list(self, tdx):
        result = tdx.stock_quotes_list(CATEGORY.A, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_stock_quotes_list_with_sort(self, tdx):
        result = tdx.stock_quotes_list(CATEGORY.A, count=5, sort_type=SORT_TYPE.TOTAL_AMOUNT)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_stock_top_board(self, tdx):
        result = tdx.stock_top_board(CATEGORY.A)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_stock_quotes_detail(self, tdx):
        result = tdx.stock_quotes_detail(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0

    def test_stock_quotes_detail_multi(self, tdx):
        result = tdx.stock_quotes_detail([(MARKET.SZ, '000001'), (MARKET.SH, '600000')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_index_info(self, tdx):
        result = tdx.index_info([(MARKET.SH, '999999'), (MARKET.SZ, '399001')])
        assert isinstance(result, list)
        assert len(result) > 0

    def test_index_momentum(self, tdx):
        result = tdx.index_momentum(MARKET.SH, '999999')
        assert isinstance(result, list)

    def test_stock_tick_chart(self, tdx):
        result = tdx.stock_tick_chart(MARKET.SH, '999999')
        assert isinstance(result, list)

    def test_stock_transaction(self, tdx):
        result = tdx.stock_transaction(MARKET.SZ, '000001')
        assert isinstance(result, list)

    def test_stock_transaction_history(self, tdx):
        result = tdx.stock_transaction(MARKET.SZ, '000001', date(2026, 4, 10))
        assert isinstance(result, list)

    def test_stock_unusual(self, tdx):
        result = tdx.stock_unusual(MARKET.SZ)
        assert isinstance(result, list)

    def test_stock_f10(self, tdx):
        result = tdx.stock_f10(MARKET.SZ, '000001')
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'name' in result[0]

    def test_stock_vol_profile(self, tdx):
        result = tdx.stock_vol_profile(MARKET.SZ, '000001')
        assert result is None or isinstance(result, list)

    def test_stock_chart_sampling(self, tdx):
        result = tdx.stock_chart_sampling(MARKET.SZ, '000001')
        assert isinstance(result, list)

    def test_stock_block(self, tdx):
        result = tdx.stock_block(BLOCK_FILE_TYPE.DEFAULT)
        assert result is not None
        assert isinstance(result, list)


class TestTdxClientGoods:
    """TdxClient 扩展行情 API"""

    def test_goods_count(self, tdx):
        result = tdx.goods_count()
        assert isinstance(result, int)
        assert result >= 0

    def test_goods_category_list(self, tdx):
        result = tdx.goods_category_list()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_goods_list(self, tdx):
        result = tdx.goods_list(start=0, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_goods_quotes(self, tdx):
        result = tdx.goods_quotes(EX_MARKET.US_STOCK, 'TSLA')
        assert isinstance(result, list)
        assert len(result) > 0

    def test_goods_quotes_multi(self, tdx):
        result = tdx.goods_quotes([(EX_MARKET.US_STOCK, 'TSLA'), (EX_MARKET.HK_MAIN_BOARD, '09988')])
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_goods_kline(self, tdx):
        result = tdx.goods_kline(EX_MARKET.US_STOCK, 'TSLA', PERIOD.DAILY, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_goods_tick_chart(self, tdx):
        result = tdx.goods_tick_chart(EX_MARKET.US_STOCK, 'TSLA')
        assert isinstance(result, list)

    def test_goods_chart_sampling(self, tdx):
        result = tdx.goods_chart_sampling(EX_MARKET.US_STOCK, 'TSLA')
        assert isinstance(result, list)
