#!/usr/bin/env python
# coding: utf-8

import os
from typing import Any, Dict, List  # noqa: F401
from unittest import TestCase

from xrpl.clients import WebsocketClient
# from xrpl.ledger import get_network_id
from xrpl.wallet import Wallet

from xls_playground.models.tools import fund, deploy_token, fund_ic

masterWallet: Wallet = Wallet("snoPBrXtMeMyMHUVTgbuqAfg1SUTb", 0)
SEEDS: List[str] = []


class BaseTestConfig(TestCase):
    """BaseTestConfig."""

    masterSecret = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
    seeds: List[str] = [
        "sEd7yKm7WVSDkYvpMjvyma7vUiVZiXa",
        "sEd7b6dwNM1J7fM3aLRZ53JXRqJ99Gf",
        "sEdTF2b3WePkNbmBBborKEXR9Vk3eBB",
        "sEdTVG8mVTxNRoCJ7YiYhqmgGCzfTZ1",
    ]

    masterWallet: Wallet = Wallet(masterSecret, 0)
    wallets: List[Wallet] = [Wallet(seed, 0) for seed in seeds]

    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    WSS_RPC_URL = "ws://127.0.0.1:6006"

    @classmethod
    def setUpUnit(cls):
        """setUpUnit."""
        print("SETUP UNIT")

    @classmethod
    def setUpClient(cls):
        cls.client = WebsocketClient(cls.WSS_RPC_URL)
        cls.client.open()

    @classmethod
    def setUpIntegration(cls):
        """setUpIntegration."""
        print("SETUP INTEGRATION")
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            # client.network_id = get_network_id(client)
            currency_code: str = "USD"

            for w in cls.wallets:
                response = fund(
                    client,
                    cls.masterWallet,
                    w.classic_address,
                    2000,
                )
                # print(response)
                # if response:
                #     cls.assertEqual(response.result["engine_result"], "tesSUCCESS")

            # cls.cold_wallet = cls.wallets[0]
            # cls.hot_wallet = cls.wallets[1]
            # deploy_token(
            #     client, currency_code, cls.cold_wallet.seed, cls.hot_wallet.seed
            # )

            # [fund_ic(client, currency_code, cls.cold_wallet, w) for w in cls.wallets]
            del cls.wallets[0]
            del cls.wallets[0]

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
