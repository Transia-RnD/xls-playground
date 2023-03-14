#!/usr/bin/env python
# coding: utf-8
import time
import logging

from testing_config import BaseTestConfig
import json
from typing import Any, Dict, List  # noqa: F401

# playground
from xls_playground.tools import (
    LEDGER_ACCEPT_REQUEST,
    Account,
    IC,
    ICXRP,
    fund,
    pay,
    trust,
    balance,
    wait_for_result,
)
from xrpl_helpers.sdk.utils import get_object_id

# XRPL
# -----------------------------------------------------------------------------
from xrpl.wallet import Wallet
from xrpl.clients import WebsocketClient
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    submit_transaction,
    get_transaction_from_hash
)
from xrpl.models.currencies import Currency, XRP
from xrpl.models import IssuedCurrencyAmount, SignerEntry
from xrpl.models.requests import (
    AccountObjects,
    AccountObjectType,
    GenericRequest
)
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.transactions import (
    XChainCreateBridge,
    SignerListSet
)
from xrpl.utils import str_to_hex

# INSTALLING
# -----------------------------------------------------------------------------
# pip3 install -e git+https://github.com/Transia-RnD/xrpl-py.git@beta#egg=xrpl-py

logger = logging.getLogger("app")


class TestXls38(BaseTestConfig):

    def setUp(cls):

        LOCK_RPC_URL = "ws://127.0.0.1:6006"
        ISSUE_RPC_URL = "ws://127.0.0.1:6008"

        # cls.issue_client = WebsocketClient(cls.LOCK_RPC_URL)
        # cls.issue_client.open()

        # cls.lock_client = WebsocketClient(cls.ISSUE_RPC_URL)
        # cls.lock_client.open()

        lock_door = Account("alice")
        issue_door = Account("bob")
        lock_user = Account("dave")
        issue_user = Account("elsa")
        gw = Account("gw")
        USD: IC = IC.gw("USD", gw)
        cls.lock_door = lock_door
        cls.issue_door = issue_door
        cls.lock_user = lock_user
        cls.issue_user = issue_user
        cls.gw = gw
        cls.usd = USD

        print('INIT LOCKING CHAIN')
        fund(
            cls.lock_client,
            cls.wallet,
            ICXRP(2000),
            gw,
            lock_door,
            lock_user
        )
        # trust(cls.lock_client, USD(2000), door)
        # pay(cls.lock_client, USD(20), gw, door)

        # print(balance(cls.lock_client, door))
        # print(balance(cls.lock_client, door, USD))

        print('INIT ISSUING CHAIN')
        fund(
            cls.issue_client,
            cls.wallet, ICXRP(2000),
            gw,
            issue_door,
            issue_user
        )
        # trust(cls.issue_client, USD(2000), door)
        # pay(cls.issue_client, USD(20), gw, door)

        # print(balance(cls.issue_client, door))
        # print(balance(cls.issue_client, door, USD))
        return super().setUp()

    def test_xls_38_create_bridge(cls):
        # Build XChain Bridge
        bridge = XChainBridge(
            locking_chain_door=cls.lock_door.account,
            locking_chain_issue=XRP(),
            issuing_chain_door=cls.issue_door.account,
            issuing_chain_issue=XRP(),
        )

        built_transaction = XChainCreateBridge(
            account=cls.lock_door.account,
            xchain_bridge=bridge,
            signature_reward='100',
            min_account_create_amount='5000000'
        )
        signed_tx = safe_sign_and_autofill_transaction(
            transaction=built_transaction,
            wallet=cls.lock_door.wallet,
            client=cls.lock_client,
        )
        submit_response = submit_transaction(signed_tx, cls.lock_client)
        print(submit_response)
        tx_hash: str = submit_response.result["tx_json"]["hash"]
        _ = wait_for_result(cls.lock_client, tx_hash)

        # witness: Wallet = Wallet('sn2ioyvM2PmrB1cfhy7huDpfbkJf8', 0)
        # signer_entries = [SignerEntry(account=witness.classic_address, signer_weight=1)]
        # signer_tx1 = SignerListSet(
        #     account=cls.door.account,
        #     signer_quorum=max(1, len(signer_entries) - 1),
        #     signer_entries=signer_entries,
        # )
        # signer_tx1_response = submit_transaction(signer_tx1, cls.lock_client)
        # signer_tx1_hash: str = signer_tx1_response.result["tx_json"]["hash"]
        # _ = wait_for_result(cls.lock_client, signer_tx1_hash)
