#!/usr/bin/env python
# coding: utf-8

import time
from typing import Dict, Any, List

from xrpl.clients import Client
from xrpl.wallet import Wallet

from xrpl.models import IssuedCurrencyAmount
from xrpl.models.transactions import (
    URITokenMintFlag, 
    URITokenMint, 
    URITokenBurn,
    URITokenSell,
    URITokenClear,
    URITokenBuy
)
from xrpl.utils import xrp_to_drops, str_to_hex
from xrpl.transaction import (
    submit_transaction,
    safe_sign_and_autofill_transaction,
)

# Mint
# [START] Mint
def uritoken_mint(
    w3: Client,
    wallet: Wallet,
    uri: str,
    digest: str = None,
):
    """uritoken_mint."""
    built_transaction = URITokenMint(
        account=wallet.classic_address,
        uri=str_to_hex(uri),
        # digest=str_to_hex(uri),
        flags=[
            # URITokenMintFlag.TF_TRANSFERABLE,
            URITokenMintFlag.TF_BURNABLE
        ],

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = submit_transaction(signed_tx, w3)
    return response
# [END] Mint


# Burn
# [START] Burn
def uritoken_burn(
    w3: Client,
    wallet: Wallet,
    id: str,
):
    """uritoken_burn."""
    built_transaction = URITokenBurn(
        account=wallet.classic_address,
        uritoken_id=id

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = submit_transaction(signed_tx, w3)
    return response
# [END] Burn


# Sell
# [START] Sell
def uritoken_sell(
    w3: Client,
    wallet: Wallet,
    id: str,
    amount: IssuedCurrencyAmount,
    destination: str = None,
):
    """uritoken_sell."""
    built_transaction = URITokenSell(
        account=wallet.classic_address,
        uritoken_id=id,
        amount=amount,
        destination=destination

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = submit_transaction(signed_tx, w3)
    return response
# [END] Sell


# Clear
# [START] Clear
def uritoken_clear(
    w3: Client,
    wallet: Wallet,
    id: str
):
    """uritoken_clear."""
    built_transaction = URITokenClear(
        account=wallet.classic_address,
        uritoken_id=id,

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = submit_transaction(signed_tx, w3)
    return response
# [END] Clear

# Buy
# [START] Buy
def uritoken_buy(
    w3: Client,
    wallet: Wallet,
    id: str,
    amount: IssuedCurrencyAmount,
):
    """uritoken_buy."""
    built_transaction = URITokenBuy(
        account=wallet.classic_address,
        uritoken_id=id,
        amount=amount,

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = submit_transaction(signed_tx, w3)
    return response
# [END] Buy