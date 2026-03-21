from client.quotationClient import QuotationClient
from mcp.server.fastmcp import FastMCP

from const import CATEGORY, MARKET, PERIOD
from datetime import date
import json
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

mcp = FastMCP('TDX MCP Server')

# 延迟初始化客户端，避免模块导入时建立连接
class QuotationClientManager:
    _instance = None
    _client = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        """获取或创建客户端实例"""
        if not self._initialized:
            self._client = QuotationClient()
            self._client.connect().login()
            self._initialized = True
            log.info("TDX MCP Server client initialized")
        return self._client

    def check_connection(self):
        """检查连接状态"""
        try:
            client = self.get_client()
            result = client.doHeartBeat()
            if result:
                log.debug("Connection healthy")
            return result
        except Exception as e:
            log.error(f"Connection check failed: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self._client:
            try:
                # TDX client 通常不需要显式断开，但保持连接管理清晰
                self._client = None
                self._initialized = False
                log.info("TDX MCP Server client disconnected")
            except Exception as e:
                log.error(f"Error disconnecting: {e}")

# 全局客户端管理器
client_manager = QuotationClientManager()

def safe_json_response(result):
    """安全返回 JSON 响应"""
    if result is None:
        return json.dumps({"error": "No data returned", "timestamp": time.time()})
    return json.dumps(result, ensure_ascii=False, indent=2)

# ==================== 健康检查 ====================

@mcp.tool()
def health_check() -> str:
    '''健康检查：验证连接状态
    :return: JSON字符串 {"healthy": true/false, "message": "..."}
    '''
    try:
        is_healthy = client_manager.check_connection()
        if is_healthy:
            return json.dumps({
                "healthy": True,
                "message": "TDX MCP Server is running and connected"
            })
        else:
            return json.dumps({
                "healthy": False,
                "message": "TDX MCP Server connection failed"
            })
    except Exception as e:
        return json.dumps({
            "healthy": False,
            "message": f"Error: {str(e)}"
        })

# ==================== 指数相关 ====================

@mcp.tool()
def get_Index_Overview() -> str:
    ''' 获取指数概况
    :return: 上证、深证、北证、创业、科创、沪深指数数据的JSON字符串
    '''
    try:
        client = client_manager.get_client()
        result = client.get_index_info([
            (MARKET.SH, '999999'),
            (MARKET.SZ, '399001'),
            (MARKET.SZ, '399006'),
            (MARKET.BJ, '899050'),
            (MARKET.SH, '000688'),
            (MARKET.SH, '000300')
        ])
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_Index_Overview error: {e}")
        return safe_json_response({"error": str(e)})

@mcp.tool()
def get_index_momentum(market: MARKET, code: str) -> str:
    ''' 获取指数动量指标
    Args:
        market: MARKET
        code: str(code)
    Return: 动量指标数据
    '''
    try:
        client = client_manager.get_client()
        result = client.get_index_momentum(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_index_momentum error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票报价 ====================

@mcp.tool()
def stock_quotes(code_list: MARKET | list[tuple[MARKET, str]], code: str = None) -> str:
    '''
    获取股票报价
    支持三种形式的参数
    stock_quotes(market, code)
    stock_quotes((market, code))
    stock_quotes([(market1, code1), (market2, code2)])
    Args:
        [(market: MARKET(market), code: str(code)), ...]
    Return: 
        [{
            'market': MARKET,
            'code': str(code),
            'name': str(name),
            'open': float(open),
            'high': float(high),
            'low': float(low),
            'price': float(price),
            'pre_close': float(pre_close),
            'server_time': str(server_time),
            'neg_price': int(neg_price),
            'vol': int(vol),
            'cur_vol': int(cur_vol),
            'amount': int(amount),
            's_vol': int(s_vol),
            'b_vol': int(b_vol),
            's_amount': int(s_amount),
            'open_amount': int(open_amount),
            'handicap': {
                'bid': [{'price': float(price), 'vol': int(vol)}, ...],
                'ask': [{'price': float(price), 'vol': int(vol)}, ...],
            },
            'rise_speed': str(rise_speed_percent),
            'short_turnover': str(short_turnover_percent),
            'min2_amount': int(min2_amount),
            'opening_rush': str(opening_rush_percent),
            'vol_rise_speed': str(vol_rise_speed_percent),
            'depth': str(depth_percent),
            'active1': int(active),
        }, ...]
    '''
    try:
        client = client_manager.get_client()
        result = client.get_quotes(code_list, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"stock_quotes error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== K线数据 ====================

@mcp.tool()
def stock_kline(market: MARKET, code: str, period: PERIOD, start = 0, count = 800, times: int = 1) -> str:
    '''
    获取K线数据
    Args:
        market: MARKET
        code: str(code)
        period: PERIOD
        start?: int(start)
        count?: int(count)
        times?: int(times) # 多周期倍数
    Return: 
        [{
            'date_time': str(date_time),
            'open': float(open),
            'high': float(high),
            'low': float(low),
            'close': float(close),
            'vol': int(vol),
            'amount': int(amount),
            'upCount?': int(upcount),
            'downCount?': int(downcount),
        }, ...]
    '''
    try:
        client = client_manager.get_client()
        result = client.get_kline(market, code, period, start, count, times)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"stock_kline error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 排行榜 ====================

@mcp.tool()
def stock_top_board(category: CATEGORY = CATEGORY.A) -> str:
    '''
    获取股票排行榜
    Args:
        category: CATEGORY
            SH: 上证A股
            SZ: 深证A股
            A: 沪深A股
            B: 沪深B股
            BJ: 北证A股
            CYB: 创业板
            KCB: 科创板
    Return: 
        {
            'increase': [{...}], # 涨幅榜
            'decrease': [{...}], # 跌幅榜
            'amplitude': [{...}], # 振幅榜
            'rise_speed': [{...}], # 涨速榜
            'fall_speed': [{...}], # 跌速榜
            'vol_ratio': [{...}], # 量比榜
            'pos_commission_ratio': [{...}], # 委比正序
            'neg_commission_ratio': [{...}], # 委比倒序
            'turnover': [{...}] # 换手率榜
        }
    '''
    try:
        client = client_manager.get_client()
        result = client.get_stock_top_board(category)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"stock_top_board error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 板块股票列表 ====================

@mcp.tool()
def get_top_stock(category: CATEGORY = CATEGORY.A, start: int = 0, count: int = 80) -> str:
    '''
    获取板块内的股票列表
    Args:
        category: 板块分类
            SH: 上证A股
            SZ: 深证A股
            A: 沪深A股
            B: 沪深B股
            BJ: 北证A股
            CYB: 创业板
            KCB: 科创板
        start?: 起始位置
        count?: 获取数量
    Return: 股票列表
    '''
    try:
        client = client_manager.get_client()
        result = client.get_stock_quotes_list(category, start, count)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_top_stock error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 公司信息 ====================

@mcp.tool()
def get_company_info(market: MARKET, code: str) -> str:
    '''
    获取公司信息
    Args:
        market: MARKET
        code: str(code)
    Returns: 公司详细信息
    '''
    try:
        client = client_manager.get_client()
        result = client.get_company_info(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_company_info error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史分时图 ====================

@mcp.tool()
def get_history_tick_chart(market: MARKET, code: str, date: date) -> str:
    '''
    获取历史分时图数据
    Args:
        market: MARKET
        code: str(code)
        date: 查询日期
    Return: 分时图数据
    '''
    try:
        client = client_manager.get_client()
        result = client.get_history_tick_chart(market, code, date)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_history_tick_chart error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史成交 ====================

@mcp.tool()
def get_history_transaction(market: MARKET, code: str, date: date) -> str:
    '''
    获取历史成交数据
    Args:
        market: MARKET
        code: str(code)
        date: 查询日期
    Return: 成交记录
    '''
    try:
        client = client_manager.get_client()
        result = client.get_history_transaction(market, code, date)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_history_transaction error: {e}")
        return safe_json_response({"error": str(e)})

@mcp.tool()
def get_history_transaction_with_trans(market: MARKET, code: str, date: date) -> str:
    '''
    获取历史成交数据（带成交额）
    Args:
        market: MARKET
        code: str(code)
        date: 查询日期
    Return: 成交记录（包含成交额）
    '''
    try:
        client = client_manager.get_client()
        result = client.get_history_transaction_with_trans(market, code, date)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_history_transaction_with_trans error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史委托 ====================

@mcp.tool()
def get_history_orders(market: MARKET, code: str, date: date) -> str:
    '''
    获取历史委托数据
    Args:
        market: MARKET
        code: str(code)
        date: 查询日期
    Return: 委托记录
    '''
    try:
        client = client_manager.get_client()
        result = client.get_history_orders(market, code, date)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_history_orders error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 实时成交 ====================

@mcp.tool()
def get_transaction(market: MARKET, code: str) -> str:
    '''
    获取实时成交数据
    Args:
        market: MARKET
        code: str(code)
    Return: 实时成交记录
    '''
    try:
        client = client_manager.get_client()
        result = client.get_transaction(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_transaction error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 集合竞价 ====================

@mcp.tool()
def get_auction(market: MARKET, code: str) -> str:
    '''
    获取集合竞价数据
    Args:
        market: MARKET
        code: str(code)
    Return: 集合竞价数据
    '''
    try:
        client = client_manager.get_client()
        result = client.get_auction(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_auction error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 异动监控 ====================

@mcp.tool()
def get_unusual(market: MARKET, start: int = 0, count: int = 0) -> str:
    '''
    获取异动股票列表
    Args:
        market: MARKET
        start?: 起始位置
        count?: 获取数量
    Return: 异动股票列表
    '''
    try:
        client = client_manager.get_client()
        result = client.get_unusual(market, start, count)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_unusual error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 量价分布 ====================

@mcp.tool()
def get_vol_profile(market: MARKET, code: str) -> str:
    '''
    获取量价分布数据
    Args:
        market: MARKET
        code: str(code)
    Return: 量价分布数据
    '''
    try:
        client = client_manager.get_client()
        result = client.get_vol_profile(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_vol_profile error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 图表采样 ====================

@mcp.tool()
def get_chart_sampling(market: MARKET, code: str) -> str:
    '''
    获取图表采样数据
    Args:
        market: MARKET
        code: str(code)
    Return: 图表采样数据
    '''
    try:
        client = client_manager.get_client()
        result = client.get_chart_sampling(market, code)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_chart_sampling error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票列表 ====================

@mcp.tool()
def get_stock_list(market: MARKET, start: int = 0, count: int = 0) -> str:
    '''
    获取股票列表
    Args:
        market: MARKET
        start?: 起始位置
        count?: 获取数量（0表示全部）
    Return: 股票列表
    '''
    try:
        client = client_manager.get_client()
        result = client.get_list(market, start, count)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_stock_list error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票数量 ====================

@mcp.tool()
def get_stock_count(market: MARKET) -> str:
    '''
    获取股票数量
    Args:
        market: MARKET
    Return: 股票数量
    '''
    try:
        client = client_manager.get_client()
        result = client.get_count(market)
        return safe_json_response(result)
    except ConnectionError as e:
        log.error(f"Connection failed: {e}")
        return safe_json_response({"error": "Connection failed", "details": str(e)})
    except Exception as e:
        log.error(f"get_stock_count error: {e}")
        return safe_json_response({"error": str(e)})

if __name__ == '__main__':
    mcp.run()
