#!/usr/bin/env python
# coding: utf-8

# import json
import logging
from typing import Dict, Any, List  # noqa: F401

from testing_config import BaseTestConfig

# XRPL
# -----------------------------------------------------------------------------

import os
import binascii

# xrpl
from xrpl.core.binarycodec import encode
from xrpl.clients import WebsocketClient
from xrpl.wallet import Wallet
from xrpl.ledger import get_network_id

# INSTALLING
# -----------------------------------------------------------------------------
# pip3 install -e git+https://github.com/Transia-RnD/xrpl-py.git@network-id#egg=xrpl-py

logger = logging.getLogger("app")


class TestXlsNetworkID(BaseTestConfig):
    def test_xls_hooks(cls):
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            expected_network: int = 21338
            cls.assertEqual(client.network_id, 1)
            client.network_id = get_network_id(client)
            cls.assertEqual(client.network_id, expected_network)
