#!/usr/bin/env python
# coding: utf-8

from xrpl.clients import WebsocketClient, Client
from xrpl.wallet import Wallet

from xrpl.models.transactions import NFTokenBurn
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)


# Burn
# [START] Burn
def nftoken_burn(
    w3: Client,
    wallet: Wallet,
    nftoken_id: str,
):
    """burn."""
    built_transaction = NFTokenBurn(
        account=wallet.classic_address,
        nftoken_id=nftoken_id,
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Burn