from .baseStockClient import BaseStockClient, update_last_ack_time
from .quotationClient import QuotationClient
from .exQuotationClient import exQuotationClient
from .commonClientMixin import CommonClientMixin
from opentdx.const import mac_hosts, mac_ex_hosts

# class macQuotationClient(BaseStockClient, CommonClientMixin):
class macQuotationClient(QuotationClient, CommonClientMixin):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = mac_hosts
        # CommonClientMixin 需识别到配置 _sp_mode_enabled
        self._sp_mode_enabled = True

# class macExQuotationClient(BaseStockClient, CommonClientMixin):
class macExQuotationClient(exQuotationClient, CommonClientMixin):
    def __init__(self, multithread=False, heartbeat=False, auto_retry=False, raise_exception=False):
        super().__init__(multithread, heartbeat, auto_retry, raise_exception)
        self.hosts = mac_ex_hosts
        # CommonClientMixin 需识别到配置 _sp_mode_enabled
        self._sp_mode_enabled = True