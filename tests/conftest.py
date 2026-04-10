import sys
import os
from unittest.mock import MagicMock, patch
from datetime import date, time as dt_time, datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client.quotationClient import QuotationClient
from client.exQuotationClient import exQuotationClient
from client.macQuotationClient import macQuotationClient, macExQuotationClient
from const import *


@pytest.fixture
def qc():
    """不连接的 QuotationClient 实例"""
    client = QuotationClient.__new__(QuotationClient)
    client.client = None
    client.ip = None
    client.port = None
    client.lock = None
    client.heartbeat = False
    client.heartbeat_thread = None
    client.stop_event = None
    client.connected = True
    client.auto_retry = False
    client.raise_exception = False
    client.retry_strategy = None
    client.hosts = []
    return client


@pytest.fixture
def eqc():
    """不连接的 exQuotationClient 实例"""
    client = exQuotationClient.__new__(exQuotationClient)
    client.client = None
    client.ip = None
    client.port = None
    client.lock = None
    client.heartbeat = False
    client.heartbeat_thread = None
    client.stop_event = None
    client.connected = True
    client.auto_retry = False
    client.raise_exception = False
    client.retry_strategy = None
    client.hosts = []
    return client


@pytest.fixture
def mqc():
    """不连接的 macQuotationClient 实例"""
    client = macQuotationClient.__new__(macQuotationClient)
    client.client = None
    client.ip = None
    client.port = None
    client.lock = None
    client.heartbeat = False
    client.heartbeat_thread = None
    client.stop_event = None
    client.connected = True
    client.auto_retry = False
    client.raise_exception = False
    client.retry_strategy = None
    client.hosts = []
    return client


@pytest.fixture
def meqc():
    """不连接的 macExQuotationClient 实例"""
    client = macExQuotationClient.__new__(macExQuotationClient)
    client.client = None
    client.ip = None
    client.port = None
    client.lock = None
    client.heartbeat = False
    client.heartbeat_thread = None
    client.stop_event = None
    client.connected = True
    client.auto_retry = False
    client.raise_exception = False
    client.retry_strategy = None
    client.hosts = []
    return client


def make_mock_call(return_value):
    """创建 mock call 方法"""
    def _call(parser):
        return return_value
    return _call
