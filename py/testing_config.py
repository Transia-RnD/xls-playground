#!/usr/bin/env python
# coding: utf-8

import os
from typing import Any, Dict, List  # noqa: F401
from unittest import TestCase

from xrpl.clients import WebsocketClient
# from xrpl.ledger import get_network_id
from xrpl.wallet import Wallet


class BaseTestConfig(TestCase):
    """BaseTestConfig."""

    masterSecret = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
    wallet: Wallet = Wallet(masterSecret, 0)

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    WSS_RPC_URL = "ws://127.0.0.1:6006"
    LOCK_RPC_URL = "ws://127.0.0.1:6006"
    ISSUE_RPC_URL = "ws://127.0.0.1:6008"

    @classmethod
    def setUpUnit(cls):
        """setUpUnit."""
        print("SETUP UNIT")

    @classmethod
    def setUpClient(cls):
        cls.client = WebsocketClient(cls.WSS_RPC_URL)
        cls.client.open()

        cls.issue_client = WebsocketClient(cls.LOCK_RPC_URL)
        cls.issue_client.open()

        cls.lock_client = WebsocketClient(cls.ISSUE_RPC_URL)
        cls.lock_client.open()

    @classmethod
    def setUpIntegration(cls):
        """setUpIntegration."""
        print("SETUP INTEGRATION")

    @classmethod
    def tearDownIntegration(cls):
        """tearDownIntegration."""
        print("TEAR DOWN INTEGRATION")

    @classmethod
    def setUpClass(cls):
        """setUpClass."""
        print("SETUP CLASS")
        cls.setUpClient()
        cls.setUpIntegration()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass."""
        print("TEAR DOWN CLASS")

    def setUp(cls):
        """setUp."""
        print("SETUP APP")
        cls.setUpUnit()

    def tearDown(cls):
        """tearDown."""
        print("TEAR DOWN")
        # print(ee)
