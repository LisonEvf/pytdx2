from opentdx.const import ADJUST, BOARD_TYPE, EX_BOARD_TYPE, MARKET, PERIOD


class TestMacQuotationClientLogin:
    """登录"""

    def test_connected(self, mqc):
        assert mqc.connected is True


class TestMacQuotationClientBoard:
    """板块 API"""

    def test_get_board_count(self, mqc):
        result = mqc.get_board_count(BOARD_TYPE.HY)
        assert result is not None
        assert 'total' in result
        assert result['total'] > 0

    def test_get_board_list(self, mqc):
        result = mqc.get_board_list(BOARD_TYPE.HY, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_board_members_quotes(self, mqc):
        result = mqc.get_board_members_quotes('880761', count=5)
        assert isinstance(result, list)

    def test_get_board_members(self, mqc):
        result = mqc.get_board_members('880761', count=5)
        assert isinstance(result, list)

    def test_get_symbol_belong_board(self, mqc):
        result = mqc.get_symbol_belong_board('000100', MARKET.SZ)
        assert result is not None

    def test_get_symbol_bars(self, mqc):
        result = mqc.get_symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=5)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_symbol_bars_with_adjust(self, mqc):
        result = mqc.get_symbol_bars(MARKET.SZ, '000100', PERIOD.DAILY, count=5, fq=ADJUST.QFQ)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_board_list_ex_board_type(self, mqc):
        result = mqc.get_board_list(EX_BOARD_TYPE.HK_ALL, count=5)
        assert result is None or isinstance(result, list)
