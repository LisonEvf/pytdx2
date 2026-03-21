import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from client.quotationClient import QuotationClient
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
import time
from datetime import date
from const import CATEGORY, MARKET, PERIOD

# 配置日志
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# 延迟初始化客户端
class QuotationClientManager:
    _instance = None
    _client = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        if not self._initialized:
            self._client = QuotationClient()
            self._client.connect().login()
            self._initialized = True
            log.info("TDX MCP Server client initialized")
        return self._client

    def check_connection(self):
        try:
            client = self.get_client()
            result = client.doHeartBeat()
            return result
        except Exception as e:
            log.error(f"Connection check failed: {e}")
            return False

client_manager = QuotationClientManager()

def safe_json_response(result):
    if result is None:
        return json.dumps({"error": "No data returned", "timestamp": time.time()})
    return json.dumps(result, ensure_ascii=False, indent=2)

# ==================== 健康检查 ====================
def health_check():
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
def get_Index_Overview():
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
    except Exception as e:
        log.error(f"get_Index_Overview error: {e}")
        return safe_json_response({"error": str(e)})

def get_index_momentum(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_index_momentum(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_index_momentum error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票报价 ====================
def stock_quotes(code_list, code=None):
    try:
        client = client_manager.get_client()
        result = client.get_quotes(code_list, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"stock_quotes error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== K线数据 ====================
def stock_kline(market, code, period, start=0, count=800, times=1):
    try:
        client = client_manager.get_client()
        result = client.get_kline(market, code, period, start, count, times)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"stock_kline error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 排行榜 ====================
def stock_top_board(category=CATEGORY.A):
    try:
        client = client_manager.get_client()
        result = client.get_stock_top_board(category)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"stock_top_board error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 板块股票列表 ====================
def get_top_stock(category=CATEGORY.A, start=0, count=80):
    try:
        client = client_manager.get_client()
        result = client.get_stock_quotes_list(category, start, count)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_top_stock error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 公司信息 ====================
def get_company_info(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_company_info(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_company_info error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史分时图 ====================
def get_history_tick_chart(market, code, date):
    try:
        client = client_manager.get_client()
        result = client.get_history_tick_chart(market, code, date)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_history_tick_chart error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史成交 ====================
def get_history_transaction(market, code, date):
    try:
        client = client_manager.get_client()
        result = client.get_history_transaction(market, code, date)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_history_transaction error: {e}")
        return safe_json_response({"error": str(e)})

def get_history_transaction_with_trans(market, code, date):
    try:
        client = client_manager.get_client()
        result = client.get_history_transaction_with_trans(market, code, date)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_history_transaction_with_trans error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 历史委托 ====================
def get_history_orders(market, code, date):
    try:
        client = client_manager.get_client()
        result = client.get_history_orders(market, code, date)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_history_orders error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 实时成交 ====================
def get_transaction(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_transaction(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_transaction error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 集合竞价 ====================
def get_auction(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_auction(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_auction error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 异动监控 ====================
def get_unusual(market, start=0, count=0):
    try:
        client = client_manager.get_client()
        result = client.get_unusual(market, start, count)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_unusual error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 量价分布 ====================
def get_vol_profile(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_vol_profile(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_vol_profile error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 图表采样 ====================
def get_chart_sampling(market, code):
    try:
        client = client_manager.get_client()
        result = client.get_chart_sampling(market, code)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_chart_sampling error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票列表 ====================
def get_stock_list(market, start=0, count=0):
    try:
        client = client_manager.get_client()
        result = client.get_list(market, start, count)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_stock_list error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== 股票数量 ====================
def get_stock_count(market):
    try:
        client = client_manager.get_client()
        result = client.get_count(market)
        return safe_json_response(result)
    except Exception as e:
        log.error(f"get_stock_count error: {e}")
        return safe_json_response({"error": str(e)})

# ==================== HTTP 服务器 ====================
class MCPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(health_check().encode())
        elif self.path == '/api/get_Index_Overview':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(get_Index_Overview().encode())
        elif self.path == '/api/health_check':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(health_check().encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "error": "Not found",
                "path": self.path
            })
            self.wfile.write(response.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            # 解析 JSON 参数
            params = json.loads(post_data.decode())

            # 路由到对应的函数
            result = None
            if self.path == '/api/stock_quotes':
                result = stock_quotes(params.get('code_list'), params.get('code'))
            elif self.path == '/api/stock_kline':
                result = stock_kline(
                    params.get('market'),
                    params.get('code'),
                    params.get('period'),
                    params.get('start', 0),
                    params.get('count', 800),
                    params.get('times', 1)
                )
            elif self.path == '/api/stock_top_board':
                result = stock_top_board(params.get('category', CATEGORY.A))
            elif self.path == '/api/get_top_stock':
                result = get_top_stock(
                    params.get('category', CATEGORY.A),
                    params.get('start', 0),
                    params.get('count', 80)
                )
            elif self.path == '/api/get_company_info':
                result = get_company_info(params.get('market'), params.get('code'))
            elif self.path == '/api/get_history_tick_chart':
                result = get_history_tick_chart(
                    params.get('market'),
                    params.get('code'),
                    date(params.get('date', date.today()))
                )
            elif self.path == '/api/get_history_transaction':
                result = get_history_transaction(
                    params.get('market'),
                    params.get('code'),
                    date(params.get('date', date.today()))
                )
            elif self.path == '/api/get_transaction':
                result = get_transaction(params.get('market'), params.get('code'))
            elif self.path == '/api/get_auction':
                result = get_auction(params.get('market'), params.get('code'))
            elif self.path == '/api/get_unusual':
                result = get_unusual(
                    params.get('market'),
                    params.get('start', 0),
                    params.get('count', 0)
                )
            elif self.path == '/api/get_stock_list':
                result = get_stock_list(
                    params.get('market'),
                    params.get('start', 0),
                    params.get('count', 0)
                )
            elif self.path == '/api/get_stock_count':
                result = get_stock_count(params.get('market'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
                return

            # 返回结果
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode())

        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"error": "Invalid JSON", "details": str(e)})
            self.wfile.write(response.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"error": str(e)})
            self.wfile.write(response.encode())

    def send_response(self, code):
        super().send_response(code)
        self.send_header('Server', 'TDX MCP Server')

def main():
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    log.info("TDX MCP Server started on http://0.0.0.0:8000")
    log.info("Available endpoints:")
    log.info("  GET  /health - Health check")
    log.info("  POST /api/stock_quotes - Get stock quotes")
    log.info("  POST /api/stock_kline - Get K-line data")
    log.info("  POST /api/stock_top_board - Get stock rankings")
    log.info("  POST /api/get_top_stock - Get stock list by category")
    log.info("  POST /api/get_company_info - Get company info")
    log.info("  POST /api/get_history_tick_chart - Get history tick chart")
    log.info("  POST /api/get_history_transaction - Get history transaction")
    log.info("  POST /api/get_transaction - Get real-time transaction")
    log.info("  POST /api/get_auction - Get auction data")
    log.info("  POST /api/get_unusual - Get unusual stocks")
    log.info("  POST /api/get_stock_list - Get stock list")
    log.info("  POST /api/get_stock_count - Get stock count")
    log.info("\nPress Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("\nShutting down...")
        httpd.shutdown()

if __name__ == '__main__':
    main()
