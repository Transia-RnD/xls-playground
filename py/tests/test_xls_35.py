#!/usr/bin/env python
# coding: utf-8
import time
import logging

from testing_config import BaseTestConfig
import json
from typing import Any, Dict, List  # noqa: F401

# playground
from xls_playground.models.xls35 import uritoken_mint, uritoken_burn
from xrpl_helpers.sdk.utils import get_object_id

# XRPL
# -----------------------------------------------------------------------------
from xrpl.clients import WebsocketClient
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    submit_transaction,
    get_transaction_from_hash
)
from xrpl.models import IssuedCurrencyAmount
from xrpl.models.requests import (
    AccountObjects,
    AccountObjectType,
    GenericRequest
)
from xrpl.models.transactions import (
    URITokenMint,
    URITokenBurn,
    URITokenBuy,
    URITokenCancelSellOffer,
    URITokenMint,
    URITokenMintFlag,
    URITokenCreateSellOffer,
)
from xrpl.utils import str_to_hex
LEDGER_ACCEPT_REQUEST = GenericRequest(method="ledger_accept")

# INSTALLING
# -----------------------------------------------------------------------------
# pip3 install -e git+https://github.com/Transia-RnD/xrpl-py.git@uritoken#egg=xrpl-py

logger = logging.getLogger("app")


def wait_for_result(client: WebsocketClient, tx_hash: str):
    timeout: int = 0
    while timeout <= 8:
        client.request(LEDGER_ACCEPT_REQUEST)
        response = get_transaction_from_hash(tx_hash=tx_hash, client=client)
        if 'validated' in response.result and response.result['validated'] is True:
            return response
        time.sleep(1)
        timeout += 1
    raise ValueError('test transaction timeout')


class TestXls35(BaseTestConfig):

    def test_xls_35_mint(cls):
        alice = cls.wallets[0]
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            pre_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            built_transaction = URITokenMint(
                account=alice.classic_address,
                uri=str_to_hex(f"ipfs://MINT{len(pre_response.result['account_objects'])}"),
                # digest=str_to_hex(json.dumps({'my': 'json'})),
                flags=[
                    URITokenMintFlag.TF_BURNABLE
                ],
            )
            mint_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            submit_response = submit_transaction(mint_signed_tx, client)
            cls.assertEqual(submit_response.result["engine_result"], "tesSUCCESS")
            tx_hash: str = submit_response.result["tx_json"]["hash"]
            _ = wait_for_result(client, tx_hash)
            post_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            # print(json.dumps(response.result, indent=4, sort_keys=True))
            cls.assertEqual(len(post_response.result['account_objects']), len(pre_response.result['account_objects']) + 1)

    def test_xls_35_burn(cls):
        alice = cls.wallets[0]
        bob = cls.wallets[0]
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            pre_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            built_transaction = URITokenMint(
                account=alice.classic_address,
                uri=str_to_hex(f"ipfs://BURN{len(pre_response.result['account_objects'])}"),
                # digest=str_to_hex(uri),
                flags=[
                    URITokenMintFlag.TF_BURNABLE
                ],
            )
            mint_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            mint_response = submit_transaction(mint_signed_tx, client)
            cls.assertEqual(mint_response.result["engine_result"], "tesSUCCESS")

            tx_hash: str = mint_response.result["tx_json"]["hash"]
            wait_response = wait_for_result(client, tx_hash)
            token_id = get_object_id(wait_response.result["meta"], "URIToken")

            post_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            cls.assertEqual(len(post_response.result['account_objects']), len(pre_response.result['account_objects']) + 1)

            built_transaction = URITokenBurn(account=alice.classic_address, uritoken_id=token_id)
            burn_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            burn_response = submit_transaction(burn_signed_tx, client)
            cls.assertEqual(burn_response.result["engine_result"], "tesSUCCESS")
            final_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            cls.assertEqual(len(final_response.result['account_objects']), len(post_response.result['account_objects']) - 1)

    def test_xls_35_create_sell_offer(cls):
        alice = cls.wallets[0]
        bob = cls.wallets[0]
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            pre_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            built_transaction = URITokenMint(
                account=alice.classic_address,
                uri=str_to_hex(f"ipfs://SELL{len(pre_response.result['account_objects'])}"),
                # digest=str_to_hex(uri),
                flags=[
                    URITokenMintFlag.TF_BURNABLE
                ],
            )
            mint_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            mint_response = submit_transaction(mint_signed_tx, client)
            cls.assertEqual(mint_response.result["engine_result"], "tesSUCCESS")

            tx_hash: str = mint_response.result["tx_json"]["hash"]
            wait_response = wait_for_result(client, tx_hash)
            token_id = get_object_id(wait_response.result["meta"], "URIToken")

            post_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            cls.assertEqual(len(post_response.result['account_objects']), len(pre_response.result['account_objects']) + 1)

            built_transaction = URITokenCreateSellOffer(
                account=alice.classic_address,
                uritoken_id=token_id,
                amount='10000000',
                destination=bob.classic_address,
            )
            sell_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            sell_response = submit_transaction(sell_signed_tx, client)
            cls.assertEqual(sell_response.result["engine_result"], "tesSUCCESS")

    def test_xls_35_cancel_sell_offer(cls):
        alice = cls.wallets[0]
        bob = cls.wallets[0]
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            pre_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            built_transaction = URITokenMint(
                account=alice.classic_address,
                uri=str_to_hex(f"ipfs://SELL{len(pre_response.result['account_objects'])}"),
                # digest=str_to_hex(uri),
                flags=[
                    URITokenMintFlag.TF_BURNABLE
                ],
            )
            mint_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            mint_response = submit_transaction(mint_signed_tx, client)
            cls.assertEqual(mint_response.result["engine_result"], "tesSUCCESS")

            tx_hash: str = mint_response.result["tx_json"]["hash"]
            wait_response = wait_for_result(client, tx_hash)
            token_id = get_object_id(wait_response.result["meta"], "URIToken")

            post_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            cls.assertEqual(len(post_response.result['account_objects']), len(pre_response.result['account_objects']) + 1)

            built_transaction = URITokenCreateSellOffer(
                account=alice.classic_address,
                uritoken_id=token_id,
                amount='10000000',
                destination=bob.classic_address,
            )
            sell_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            sell_response = submit_transaction(sell_signed_tx, client)
            cls.assertEqual(sell_response.result["engine_result"], "tesSUCCESS")

            cancel_transaction = URITokenCancelSellOffer(
                account=alice.classic_address,
                uritoken_id=token_id,
            )
            cancel_signed_tx = safe_sign_and_autofill_transaction(
                transaction=cancel_transaction,
                wallet=alice,
                client=client,
            )
            sell_response = submit_transaction(cancel_signed_tx, client)
            cls.assertEqual(sell_response.result["engine_result"], "tesSUCCESS")

    def test_xls_35_buy(cls):
        alice = cls.wallets[0]
        bob = cls.wallets[0]
        w3 = WebsocketClient(cls.WSS_RPC_URL)
        with w3 as client:
            pre_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            built_transaction = URITokenMint(
                account=alice.classic_address,
                uri=str_to_hex(f"ipfs://SELL{len(pre_response.result['account_objects'])}"),
                # digest=str_to_hex(uri),
                flags=[
                    URITokenMintFlag.TF_BURNABLE
                ],
            )
            mint_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            mint_response = submit_transaction(mint_signed_tx, client)
            cls.assertEqual(mint_response.result["engine_result"], "tesSUCCESS")

            tx_hash: str = mint_response.result["tx_json"]["hash"]
            wait_response = wait_for_result(client, tx_hash)
            token_id = get_object_id(wait_response.result["meta"], "URIToken")

            post_response = client.request(
                AccountObjects(account=alice.classic_address, type=AccountObjectType.URI_TOKEN)
            )
            cls.assertEqual(len(post_response.result['account_objects']), len(pre_response.result['account_objects']) + 1)

            built_transaction = URITokenCreateSellOffer(
                account=alice.classic_address,
                uritoken_id=token_id,
                amount='10000000',
                destination=bob.classic_address,
            )
            sell_signed_tx = safe_sign_and_autofill_transaction(
                transaction=built_transaction,
                wallet=alice,
                client=client,
            )
            sell_response = submit_transaction(sell_signed_tx, client)
            cls.assertEqual(sell_response.result["engine_result"], "tesSUCCESS")

            buy_transaction = URITokenBuy(
                account=bob.classic_address,
                uritoken_id=token_id,
                amount='10000000',
            )
            buy_signed_tx = safe_sign_and_autofill_transaction(
                transaction=buy_transaction,
                wallet=bob,
                client=client,
            )
            buy_response = submit_transaction(buy_signed_tx, client)
            cls.assertEqual(buy_response.result["engine_result"], "tesSUCCESS")
