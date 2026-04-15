from opentdx.const import ADJUST, BOARD_TYPE, EX_BOARD_TYPE, MARKET, PERIOD, SORT_TYPE, SORT_ORDER


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

    def test_get_board_members_with_sort_type(self, mqc):
        """测试 sort_type 和 sort_order 参数是否生效"""
        board_code = '880761'
        count = 10

        # 测试按成交量降序排序 (默认通常是降序，但显式指定更稳妥)
        result_desc = mqc.get_board_members_quotes(board_code, count=count, sort_type=SORT_TYPE.VOLUME, sort_order=SORT_ORDER.DESC)
        assert isinstance(result_desc, list)
        assert len(result_desc) > 1, "返回数据不足以进行排序验证"

        vols_desc = [item.get('vol', 0) for item in result_desc if isinstance(item, dict)]
        assert len(vols_desc) == len(result_desc), "部分数据缺失 vol 字段"
        
        # 检查是否是降序排列 (从大到小)
        for i in range(len(vols_desc) - 1):
            assert vols_desc[i] >= vols_desc[i+1], f"降序排序错误: 索引 {i} 的 vol ({vols_desc[i]}) 小于 索引 {i+1} 的 vol ({vols_desc[i+1]})"

        # 测试按成交量升序排序
        result_asc = mqc.get_board_members_quotes(board_code, count=count, sort_type=SORT_TYPE.VOLUME, sort_order=SORT_ORDER.ASC)
        assert isinstance(result_asc, list)
        assert len(result_asc) > 1, "返回数据不足以进行排序验证"

        vols_asc = [item.get('vol', 0) for item in result_asc if isinstance(item, dict)]
        assert len(vols_asc) == len(result_asc), "部分数据缺失 vol 字段"

        # 检查是否是升序排列 (从小到大)
        for i in range(len(vols_asc) - 1):
            assert vols_asc[i] <= vols_asc[i+1], f"升序排序错误: 索引 {i} 的 vol ({vols_asc[i]}) 大于 索引 {i+1} 的 vol ({vols_asc[i+1]})"


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
