#!/usr/bin/env python
# coding: utf-8

import json
from typing import Dict, Any

from xrpl.clients import Client
from xrpl.models.requests import AccountChannels
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)
from xrpl.models import IssuedCurrencyAmount
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.transactions import (
    PaymentChannelCreate,
    PaymentChannelFund,
    PaymentChannelClaim
)


def account_channels(
    w3,
    account,
    destination,
):
    return w3.request(
        AccountChannels(
            account=account,
            destination_account=destination,
        ),
    )


def create_payment_channel(
    client: Client, 
    wallet: Wallet, 
    destination: str, 
    amount: IssuedCurrencyAmount, 
    public_key: str,
    settle_delay: int
):
    tx = PaymentChannelCreate(
        account=wallet.classic_address,
        amount=amount,
        destination=destination,
        settle_delay=settle_delay,
        public_key=public_key
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response.result


def fund_payment_channel(
    client: Client, 
    wallet: Wallet, 
    channel: str, 
    amount: IssuedCurrencyAmount, 
    expiration: int
):
    tx = PaymentChannelFund(
        account=wallet.classic_address,
        channel=channel,
        amount=amount,
        # expiration=expiration,
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response.result


def claim_payment_channel(
    client: Client, 
    wallet: Wallet, 
    channel: str, 
    balance: IssuedCurrencyAmount, 
    amount: IssuedCurrencyAmount, 
    signature: str,
    public_key: str,
    flags: Any
):
    tx = PaymentChannelClaim(
        account=wallet.classic_address,
        channel=channel,
        # amount=amount,
        # balance=balance,
        # signature=signature,
        # public_key=public_key,
        flags=flags
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    print(prepared)
    response = send_reliable_submission(prepared, client)
    return response.result

def get_channel_hex(meta: Dict[str, Any]):
    print(json.dumps(meta, indent=4, sort_keys=True))
    created_list = [node for node in meta['AffectedNodes'] if 'CreatedNode' in node and node['CreatedNode']['LedgerEntryType'] == 'PayChannel']
    if len(created_list) > 0:
        return created_list[0]['CreatedNode']['LedgerIndex']
    return None