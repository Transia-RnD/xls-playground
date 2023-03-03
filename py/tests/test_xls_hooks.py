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
from xrpl.ledger import get_fee_estimate, get_network_id
from xrpl.models import Hook, SetHook
from xrpl.transaction import safe_sign_and_autofill_transaction, submit_transaction
from xrpl.utils import calculate_hook_on, hex_namespace
from xrpl.wallet import Wallet

from testing_config import BaseTestConfig
from xls_playground.models.hooks import build_hook, prepare_hook, set_hook

# XRPL
# -----------------------------------------------------------------------------


# INSTALLING
# -----------------------------------------------------------------------------
# pip3 install -e git+https://github.com/Transia-RnD/xrpl-py.git@hooks#egg=xrpl-py

logger = logging.getLogger("app")


class TestXlsHooks(BaseTestConfig):
    def test_xls_hooks(cls):
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            client.network_id = get_network_id(client)
            wallet = Wallet(cls.masterSecret, 0)

            # CreateCode
            CONTRACT_PATH = os.path.join(cls.BASE_DIR, "tests/fixtures/starter.c.wasm")
            with open(CONTRACT_PATH, "rb") as f:
                content = f.read()
            binary = binascii.hexlify(content).decode("utf-8").upper()

            # HookOn
            invoke_on: List[str] = ["ttACCOUNT_SET"]
            hook_on_values: List[str] = [v for v in invoke_on]
            hook_on: str = calculate_hook_on(hook_on_values)

            # NameSpace
            namespace: str = hex_namespace("starter")

            # Hook Object
            hook = Hook(
                create_code=binary,
                hook_on=hook_on,
                flags=1,
                hook_api_version=0,
                hook_namespace=namespace,
            )

            # Set Hook
            hook_transaction = SetHook(
                account=wallet.classic_address,
                hooks=[hook],
            )

            # Estimate Fee
            tx_blob = encode(hook_transaction.to_xrpl())
            estimated_fee = get_fee_estimate(client, tx_blob)

            # Sign Tx
            hook_transaction = SetHook(
                account=wallet.classic_address,
                fee=estimated_fee,
                hooks=[hook],
            )
            hook_signed_tx = safe_sign_and_autofill_transaction(
                transaction=hook_transaction,
                wallet=wallet,
                client=client,
            )

            # Submit Tx
            response = submit_transaction(hook_signed_tx, client)
            cls.assertEqual(response.result["engine_result"], "tesSUCCESS")
