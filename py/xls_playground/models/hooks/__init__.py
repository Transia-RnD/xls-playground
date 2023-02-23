#!/usr/bin/env python
# coding: utf-8

from typing import Any, Dict, List

from xrpl.clients import Client
from xrpl.wallet import Wallet

from xrpl.models.transactions import SetHook, Hook

from xrpl.transaction import (
    autofill,
    safe_sign_and_autofill_transaction,
)

def build_hook(
    binary: str,
    flags: int = None,
    hook_on: str = None,
    hook_api_version: int = None,
    hook_namespace: str = None,
):
    return Hook(
        create_code=binary,
        hook_on=hook_on,
        flags=flags,
        hook_api_version=hook_api_version,
        hook_namespace=hook_namespace
    )

def prepare_hook(
    client: Client,
    network_id: int,
    account: str,
    hooks: List[Hook] = [],
    signers_count: int = 0,
):
    tx = SetHook(
        account=account,
        network_id=network_id,
        hooks=hooks,
    )
    hook_prepared = autofill(
        transaction=tx,
        client=client,
        signers_count=signers_count,
    )

    return hook_prepared

def set_hook(
    client: Client,
    network_id: int,
    wallet: Wallet,
    fee: int,
    hooks: List[Hook] = [],
    signers_count: int = 0,
):
    tx = SetHook(
        account=wallet.classic_address,
        network_id=network_id,
        fee=fee,
        hooks=hooks,
    )
    hook_prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
        check_fee=False
    )

    return hook_prepared