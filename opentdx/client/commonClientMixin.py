from typing import Union

import pandas as pd

from .baseStockClient import update_last_ack_time
from opentdx.const import ADJUST, BOARD_TYPE, CATEGORY, EX_CATEGORY, MARKET, PERIOD, EX_BOARD_TYPE, SORT_TYPE, SORT_ORDER, mac_hosts, mac_ex_hosts
from opentdx.parser.mac_quotation import BoardCount, BoardList, BoardMembers, BoardMembersQuotes, SymbolBar, SymbolBelongBoard, SymbolZJLX
from opentdx.utils.log import log
from functools import wraps


def require_sp_mode(func):
    """装饰器：要求必须先调用 sp() 方法"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, '_check_sp_mode'):
            self._check_sp_mode()
        return func(self, *args, **kwargs)
    return wrapper


# ---------------------- 公共接口  ----------------------
class CommonClientMixin:
    _sp_mode_enabled = False
    
    def sp(self, hosts=None):
        """启动sp模式,支持mac协议调用.

        Args:
            hosts (list of str): List of hosts to use. 如果为None，则根据子类类型自动选择

        Returns:
            self
        """
        # 如果未传入 hosts，根据子类类型自动选择默认值
        if hosts is None:
            # 获取调用者的类名
            class_name = self.__class__.__name__
            
            # 根据类名判断使用哪个默认 hosts
            if class_name == "QuotationClient":
                hosts = mac_hosts
            elif class_name == "exQuotationClient":
                hosts = mac_ex_hosts
            else:
                # 默认使用 mac_hosts
                hosts = mac_hosts
        
        self.hosts = hosts
        self._sp_mode_enabled = True
        return self

    def _check_sp_mode(self):
        """检查是否已启用sp模式"""
        if not self._sp_mode_enabled:
            raise RuntimeError(
                "必须先调用 sp() 方法启用sp模式后才能使用此方法。\n"
                "示例: client.sp().get_board_members_quotes(...)"
            )
            
    @require_sp_mode
    @update_last_ack_time
    def get_board_count(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE]):
        return self.call(BoardCount(market))

    @require_sp_mode
    @update_last_ack_time
    def get_board_list(self, market: Union[BOARD_TYPE, EX_BOARD_TYPE], count=10000):
        MAX_LIST_COUNT = 150
        security_list = []
        page_size = min(count, MAX_LIST_COUNT)
        
        msg = f"TDX 板块列表：{market} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, page_size):
            current_count = min(page_size, count - start)
            part = self.call(BoardList(board_type=market, start=start, page_size=current_count))
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break
                
        return security_list

    @require_sp_mode
    @update_last_ack_time
    def get_board_members_quotes(self, board_symbol: str | CATEGORY | EX_CATEGORY = "881001", count=100000, sort_type: SORT_TYPE = SORT_TYPE.CHANGE_PCT, sort_order=SORT_ORDER.DESC, filter=0):
        """
        获取板块成分股的实时行情报价
        
        分页获取指定板块成分股的实时行情数据，支持按涨跌幅、成交量等字段排序。
        与 get_board_members 不同的是，此方法返回的是带有实时行情数据的成分股列表。
        内部会自动处理分页逻辑，每次最多获取80条记录。
        
        Args:
            board_symbol: 板块代码，如 "881001"（全部A股）
                - 行业板块: 880xxx（如 "880761" 半导体）
                - 概念板块: 880xxx（如 "880521" 人工智能）
                - 地区板块: 880xxx
                - 美股板块: HKxxxx （如"HK0287" 港股-药明系）
                - 美股板块: USxxxx （如"US0495" 美股-加密货币）
            count: 需要获取的最大记录数，默认100000
            sort_type: 排序类型，默认按涨跌幅排序（SORT_TYPE.CHANGE_PCT）
                - SORT_TYPE.CHANGE_PCT: 按涨跌幅排序（最常用）
                - SORT_TYPE.VOLUME: 按成交量排序
                - SORT_TYPE.AMOUNT: 按成交额排序
                - SORT_TYPE.CODE: 按股票代码排序
                - SORT_TYPE.PRICE: 按价格排序
                - 其他排序类型参见 SORT_TYPE 枚举
            sort_order: 排序顺序，默认降序（SORT_ORDER.DESC）
                - SORT_ORDER.ASC: 升序（从小到大）
                - SORT_ORDER.DESC: 降序（从大到小，如涨幅排行榜）
                - SORT_ORDER.NONE: 不排序
            filter: 过滤条件，默认0（不过滤）
                - 0: 不过滤
                - 1: 过滤停牌股票
                
        Returns:
            list: 包含板块成分股实时行情的列表，每个元素为一个字典，包含：
                - code: 股票代码（如 "000001"）
                - name: 股票名称（如 "平安银行"）
                - price: 当前价格
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - pre_close: 昨收价
                - change: 涨跌额
                - change_pct: 涨跌幅（百分比）
                - vol: 成交量（手）
                - amount: 成交额（元）
                - buy_price: 买一价
                - sell_price: 卖一价
                - 等其他实时行情字段
                
        Example:
            >>> # 获取板块涨幅排行（默认按涨跌幅降序）
            >>> top_stocks = client.get_board_members_quotes('880761', count=10)
            >>> for stock in top_stocks:
            ...     print(f"{stock['name']}: {stock['change_pct']:.2f}%")
            >>> 
            >>> # 获取板块成交量排行（按成交量降序）
            >>> volume_stocks = client.get_board_members_quotes('880761', count=20,
            ...                                                  sort_type=SORT_TYPE.VOLUME,
            ...                                                  sort_order=SORT_ORDER.DESC)
            >>> 
            >>> # 获取板块跌幅排行（按涨跌幅升序）
            >>> drop_stocks = client.get_board_members_quotes('880761', count=10,
            ...                                                sort_type=SORT_TYPE.CHANGE_PCT,
            ...                                                sort_order=SORT_ORDER.ASC)
            
        Note:
            - 此方法需要在 SP 模式下使用
            - 内部会自动处理分页，每次请求最多80条记录
            - 当返回的数据量小于请求数量时，会自动停止分页
            - 默认按涨跌幅降序排序，适合获取涨幅排行榜
            - 返回的是实时行情数据，价格会随市场变化
            - 如果板块不存在或无成分股，返回空列表
            - 与 get_board_members 的区别：
                * get_board_members: 返回基本信息列表
                * get_board_members_quotes: 返回带实时行情的完整数据
        """
        MAX_LIST_COUNT = 80
        security_list = []
        
        msg = f"TDX 板块成分报价：{board_symbol} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, MAX_LIST_COUNT):
            current_count = min(MAX_LIST_COUNT, count - start)
            rs = self.call(BoardMembersQuotes(board_symbol=board_symbol, start=start, page_size=current_count, sort_type=sort_type, sort_order=sort_order, filter=filter))
            part = rs["stocks"]
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break
                
                
        return security_list

    @require_sp_mode
    @update_last_ack_time
    def top_board_members(self, board_symbol: str | CATEGORY | EX_CATEGORY = "881001", count=20):
        """
        获取板块活跃成分股排行榜(简单示例:如何使用filter或许自己需要的数据)
        
        分页获取指定板块成分股的实时行情数据，并自动在 filter 中启用 ACTIVITY（活跃度）字段。
        支持按任意字段排序，默认按活跃度降序排列，适合获取最活跃的股票列表。
        内部会自动处理分页逻辑，每次最多获取80条记录。
        
        Args:
            board_symbol: 板块代码，如 "881001"（全部A股）
                - 行业板块: 880xxx（如 "880761" 半导体）
                - 概念板块: 880xxx（如 "880521" 人工智能）
                - 地区板块: 880xxx
                - 美股板块: HKxxxx （如"HK0287" 港股-药明系）
                - 美股板块: USxxxx （如"US0495" 美股-加密货币）
            count: 需要获取的最大记录数，默认20
                

        """
        # ACTIVITY 字段的位位置是 0x59 (89)
        ACTIVITY_BIT = 0x59
        FLOAT_SHARES= 0xb
        # 在用户提供的 filter 基础上，启用 ACTIVITY 字段
        enhanced_filter = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << ACTIVITY_BIT) | (1 << FLOAT_SHARES)

        
        
        return self.get_board_members_quotes(
            board_symbol=board_symbol,
            count=count,
            sort_type=SORT_TYPE.ACTIVITY,
            sort_order=SORT_ORDER.DESC,
            filter=enhanced_filter
        )

    @require_sp_mode
    @update_last_ack_time
    def get_board_members(self, board_symbol: str | CATEGORY | EX_CATEGORY = "881001", count=100000, sort_type: SORT_TYPE = SORT_TYPE.CODE, sort_order=SORT_ORDER.NONE, filter=0):
        """
        获取板块成分股列表
        
        分页获取指定板块的成分股信息，支持排序和过滤。
        内部会自动处理分页逻辑，每次最多获取80条记录。
        
        Args:
            board_symbol: 板块代码，如 "881001"（全部A股）
                - 行业板块: 880xxx
                - 概念板块: 880xxx  
                - 地区板块: 880xxx
            count: 需要获取的最大记录数，默认100000
            sort_type: 排序类型，默认按代码排序（SORT_TYPE.CODE）
                - SORT_TYPE.CODE: 按股票代码排序
                - SORT_TYPE.VOLUME: 按成交量排序
                - SORT_TYPE.AMOUNT: 按成交额排序
                - 其他排序类型参见 SORT_TYPE 枚举
            sort_order: 排序顺序，默认不排序（SORT_ORDER.NONE）
                - SORT_ORDER.ASC: 升序
                - SORT_ORDER.DESC: 降序
                - SORT_ORDER.NONE: 不排序
            filter: 过滤条件，默认0（不过滤）
                
        Returns:
            list: 包含板块成分股信息的列表，每个元素为一个字典，包含：
                - code: 股票代码
                - name: 股票名称
                
        Example:
            >>> # 获取行业板块成分股
            >>> members = client.get_board_members('880761', count=50)
            >>> print(f"共获取 {len(members)} 只股票")
            >>> 
            >>> # 按成交量降序获取板块成分股
            >>> members = client.get_board_members('880761', count=20, 
            ...                                    sort_type=SORT_TYPE.VOLUME,
            ...                                    sort_order=SORT_ORDER.DESC)
            
        Note:
            - 此方法需要在 SP 模式下使用
            - 内部会自动处理分页，每次请求最多80条记录
            - 当返回的数据量小于请求数量时，会自动停止分页
            - 如果板块不存在或无成分股，返回空列表
        """
        MAX_LIST_COUNT = 80
        security_list = []
        
        msg = f"TDX 板块成员：{board_symbol} 查询总量{count}"
        log.debug(msg)
        
        for start in range(0, count, MAX_LIST_COUNT):
            current_count = min(MAX_LIST_COUNT, count - start)
            rs = self.call(BoardMembers(board_symbol=board_symbol, start=start, page_size=current_count, sort_type=sort_type, sort_order=sort_order, filter=filter))
            part = rs["stocks"]
            
            if len(part) > 0:
                security_list.extend(part)
            
            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足，获取结束")
                break

        return security_list
    
    @require_sp_mode
    @update_last_ack_time
    def count_board_members(self, board_symbol: str | CATEGORY | EX_CATEGORY = "881001", count=1, sort_type: SORT_TYPE = SORT_TYPE.CODE, sort_order=SORT_ORDER.NONE, filter=0):

        msg = f"TDX 板块成员：{board_symbol} 查询总量{count}"
        log.debug(msg)
        
        rs = self.call(BoardMembers(board_symbol=board_symbol, start=0, page_size=count, sort_type=sort_type, sort_order=sort_order, filter=filter))
        # total = rs["total"]

        return rs
    
    @require_sp_mode
    @update_last_ack_time
    def get_symbol_belong_board(self, symbol: str, market: MARKET) -> pd.DataFrame:
        parser = SymbolBelongBoard(symbol=symbol, market=market)
        df = self.call(parser)
        return df
    
    @require_sp_mode
    @update_last_ack_time
    def get_symbol_zjlx(self, symbol: str, market: MARKET) -> pd.DataFrame:
        """
        获取股票资金流向数据
        
        Args:
            symbol: 股票代码
            market: 市场类型（仅支持 MARKET 类型，不支持 EX_MARKET）
            
        Returns:
            DataFrame: 包含资金流向信息的DataFrame，包含以下列：
                - 今日主力流入: 今日主力资金流入金额
                - 今日主力流出: 今日主力资金流出金额
                - 今日散户流入: 今日散户资金流入金额
                - 今日散户流出: 今日散户资金流出金额
                - 5日主买: 5日主力买入金额
                - 5日主卖: 5日主力卖出金额
                - 5日超大单净额: 5日超大单净流入金额
                - 5日大单净额: 5日大单净流入金额
                - 5日中单净额: 5日中单净流入金额
                - 5日小单净额: 5日小单净流入金额
                
                衍生指标：
                - 今日主力净流入: 今日主力流入 - 今日主力流出
                - 今日散户净流入: 今日散户流入 - 今日散户流出
                - 5日主力净流入: 5日主买 - 5日主卖
                
        Raises:
            TypeError: 当 market 参数不是 MARKET 类型时抛出
        """
        # 仅支持 MARKET 类型（A股市场），不支持 EX_MARKET（扩展市场）
        if not isinstance(market, MARKET):
            raise TypeError(f"market 参数必须为 MARKET 类型，当前类型: {type(market).__name__}")
            
        parser = SymbolZJLX(symbol=symbol, market=market)
        df = self.call(parser)
        return df

    @require_sp_mode    
    @update_last_ack_time
    def get_symbol_bars(
        self, market: MARKET, code: str, period: PERIOD, times: int = 1, start: int = 0, count: int = 800, fq: ADJUST = ADJUST.NONE
    ):
        MAX_LIST_COUNT = 700
        page_size = min(count, MAX_LIST_COUNT)
        security_list = []
        start = 0

        msg = f"TDX bar :{market} {code} {period} 查询总量{count} {start}  "
        log.debug(msg)

        for start in range(0, count, page_size):
            # 计算本次请求的实际数量，最后一次根据剩余数据减少
            current_count = min(page_size, count - start)

            parser = SymbolBar(market=market, code=code, period=period, times=times, start=start, count=current_count, fq=fq)
            part = self.call(parser)

            if len(part) > 0:
                security_list.extend(part)

            if len(part) < current_count:
                log.debug(f"{msg} 数据量不足,获取结束")
                break

        return security_list