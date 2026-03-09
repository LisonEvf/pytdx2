from client.baseStockClient import BaseStockClient, update_last_ack_time
from parser.ex_quotation import ex_server, goods
from const import EX_CATEGORY, ex_hosts
from utils.log import log

class exQuotationClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hosts = ex_hosts

    def login(self, show_info=False):
        try:
            info = self.call(ex_server.Login())
            if show_info:
                print(info)
            return True
        except Exception as e:
            log.error("login failed: %s", e)
            return False
    
    def server_info(self):
        try:
            info = self.call(ex_server.Info())
            return info
        except Exception as e:
            log.error("get server info failed: %s", e)
            return None
    
    @update_last_ack_time
    def get_count(self):
        '''
        获取扩展市场商品数量
        :return: {
            'id': 站点ID,
            'count': 产品数量
        } 的JSON字符串
        '''
        return self.call(goods.Count())
    
    @update_last_ack_time
    def get_category_list(self):
        '''
        获取拓展市场类别列表
        :return: [
            {
                'market': 市场类型,
                'name': 类别名称,
                'code': 类别代码,
                'abbr': 类别简称
            },
            ...
        ] 的JSON字符串
        '''
        return self.call(goods.CategoryList())
    
    @update_last_ack_time
    def get_Detail(self, start=0, count=100):
        '''
        获取拓展市场商品详情
        Args:
            start: 起始位置，默认为0
            count: 获取数量，默认为100
        :return: 拓展市场商品详情的JSON字符串
        '''
        return self.call(goods.Detail(start, count))
    
    @update_last_ack_time
    def get_quotes(self, category, code):
        '''
        获取商品行情
        Args:
            category: 商品类别，必填项
            code: 商品代码，必填项 
        :return: 商品行情的JSON字符串
        '''
        return self.call(goods.Quotes(category, code))
    
    @update_last_ack_time
    def get_quotes_list(self, code_list: list[tuple[EX_CATEGORY, str]]):
        '''
        获取多个商品行情
        Args:
            code_list: 商品列表，必填项，格式为 [(category, code), ...]
        :return: 多个商品行情的JSON字符串
        '''
        return self.call(goods.QuotesList(code_list))
    
    @update_last_ack_time
    def get_futures_quotes_list(self, category):
        '''
        获取期货商品行情列表
        Args:
            category: 商品类别，必填项
        :return: 期货商品行情列表的JSON字符串
        '''
        return self.call(goods.Futures_QuotesList(category))
    
    @update_last_ack_time
    def get_futures_quotes(self, futures: list[tuple[EX_CATEGORY, str]]):
        '''
        获取多个期货商品行情
        Args:
            futures: 期货商品列表，必填项，格式为 [(category, code), ...]
        :return: 多个期货商品行情的JSON字符串
        '''
        return self.call(goods.Futures_Quotes(futures))
    
    @update_last_ack_time
    def get_table(self):
        '''
        获取商品名称表
        :return: 表格数据
        '''
        start = 0
        str = ''
        while True:
            _, count, context = self.call(goods.Table(start))
            start += count
            str += context
            if count <= 0:
                break
        return str
    
    @update_last_ack_time
    def get_table_detail(self):
        '''
        获取商品名称表详情
        :return: 表格数据
        '''
        start = 0
        str = ''
        while True:
            _, count, context = self.call(goods.TableDetail(start))
            start += count
            str += context
            if count <= 0:
                break
        return str