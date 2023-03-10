#!/usr/bin/env python
# coding: utf-8

import binascii
# import json
import logging
import os
from typing import Any, Dict, List  # noqa: F401

from xrpl.clients import WebsocketClient
# xrpl
from xrpl.core.binarycodec import encode
from xrpl.ledger import get_network_id
from xrpl.wallet import Wallet

from testing_config import BaseTestConfig

# XRPL
# -----------------------------------------------------------------------------



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
