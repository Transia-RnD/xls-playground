#!/usr/bin/env python
# coding: utf-8

# import json
import logging
from typing import Dict, Any, List  # noqa: F401

from testing_config import BaseTestConfig

# -----------------------------------------------------------------------------

import os
import binascii

# xrpl
from xrpl.core.binarycodec import encode
from xrpl.clients import WebsocketClient
from xrpl.wallet import Wallet
from xrpl.transaction import (
    submit_transaction,
    sign,
)
from xrpl.ledger import get_fee_estimate
from xrpl.utils import calculate_hook_on, hex_namespace

from xls_playground.models.hooks import build_hook, prepare_hook, set_hook

# -----------------------------------------------------------------------------

logger = logging.getLogger('app')


class TestXlsHooks(BaseTestConfig):

    def test_xls_hooks(cls):
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            network_id: int = 21338
            
            wallet = Wallet(cls.masterSecret, 0)

            # CreateCode
            CONTRACT_PATH = os.path.join(cls.BASE_DIR, 'tests/fixtures/starter.c.wasm')
            with open(CONTRACT_PATH, 'rb') as f:
                content = f.read()
            binary = binascii.hexlify(content).decode('utf-8').upper()

            # HookOn
            invoke_on: List[str] = ['ttACCOUNT_SET']
            hook_on_values: List[str] = [v for v in invoke_on]
            hook_on: str = calculate_hook_on(hook_on_values)

            # NameSpace
            namespace: str = hex_namespace('starter')
            
            # Hook Object
            hook = build_hook(binary, 1, hook_on, 0, namespace)
            
            # Set Hook
            prepared_tx = prepare_hook(client, network_id, wallet.classic_address, [hook])
            
            # Estimate Fee
            tx_blob = encode(prepared_tx.to_xrpl())
            estimated_fee = get_fee_estimate(client, tx_blob)

            # Sign Tx
            prepared_tx = set_hook(
                client,
                network_id,
                wallet,
                estimated_fee,
                [hook]
            )

            # Submit Tx
            response = submit_transaction(prepared_tx, client)
            cls.assertEqual(response.result['engine_result'], 'tesSUCCESS')



    