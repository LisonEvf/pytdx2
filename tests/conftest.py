import pytest

from opentdx.client.exQuotationClient import exQuotationClient
from opentdx.client.macQuotationClient import macQuotationClient
from opentdx.client.quotationClient import QuotationClient
from opentdx.tdxClient import TdxClient


@pytest.fixture(scope="session")
def tdx():
    client = TdxClient()
    client.quotation_client = QuotationClient(multithread=True, heartbeat=True)
    client.ex_quotation_client = exQuotationClient(multithread=True, heartbeat=True)
    client.quotation_client.connect().login()
    client.ex_quotation_client.connect().login()
    yield client
    if client.quotation_client.connected:
        client.quotation_client.disconnect()
    if client.ex_quotation_client.connected:
        client.ex_quotation_client.disconnect()


@pytest.fixture(scope="session")
def qc():
    client = QuotationClient(multithread=True, heartbeat=True)
    client.connect().login()
    yield client
    client.disconnect()


@pytest.fixture(scope="session")
def eqc():
    client = exQuotationClient(multithread=True, heartbeat=True)
    client.connect().login()
    yield client
    client.disconnect()


@pytest.fixture(scope="session")
def mqc():
    client = macQuotationClient(multithread=True, heartbeat=True)
    client.connect()
    yield client
    client.disconnect()
