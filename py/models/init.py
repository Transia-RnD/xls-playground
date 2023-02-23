#!/usr/bin/env python
# coding: utf-8

import time
from typing import List, Dict, Any
from random import randint

from xrpl.clients import WebsocketClient, Client
from xrpl.wallet import Wallet
from xrpl.core import keypairs
from xrpl.core.binarycodec.types.account_id import AccountID

from xrpl.models.transactions.payment import Payment

from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
    submit_transaction
)
from xrpl.utils import xrp_to_drops, str_to_hex

from models.payment import xrp_payment, trust_set
from models.account import (
    disable_master,
    account_set,
    ticket_create,
    set_regular_key
)
from models.multisign import signer_list_set

w3 = WebsocketClient('wss://hooks-testnet-v2.xrpl-labs.com')


# signers = {
#     f'{owner_account}': 1,
#     f'{emp_one_account}': 1,
# }
def initialize_core(
  client: Client,
  seed: str,
  wallet: Wallet,
  xrp_balance: float,
  quorum: int,
  signers: Dict[str, Any],
  ticketCount: int,
  backup: str,
):
    # 1. Payment
    response = xrp_payment(
        client,
        Wallet(seed, 0),
        wallet.classic_address,
        xrp_balance,
    )
    print(response)
    # 2. AccountSet - (Set Domain + Require Auth)
    response = account_set(
        client,
        wallet,
        'issuer.transia.co'
    )
    print(response)
    # 3. SignerListSet
    response = signer_list_set(
        client,
        wallet,
        quorum,
        signers
    )
    print(response)
    # 4. TicketCreate
    response = ticket_create(
        client,
        wallet,
        ticketCount,
    )
    print(response)
    # 5. SetRegularKey
    response = set_regular_key(
        client,
        wallet,
        backup,
    )
    print(response)
    # 6. Account Set - (Disable Master)
    # response = disable_master(
    #     client,
    #     wallet
    # )
    # print(response)


def initialize_user(
  client: Client,
  seed: str,
  wallet: Wallet,
  xrp_balance: float,
  currency: float,
  issuer: float,
  cur_limit: float,
  cur_balance: float,
  quorum: int,
  signers: Dict[str, Any],
  ticketCount: int,
  backup: str,
):
    print('INITIALIZING USER')
    # 1. Payment
    response = xrp_payment(
      client,
      Wallet(seed, 0),
      wallet.classic_address,
      xrp_balance,
    )
    print(response)
    # 2. AccountSet - (Set Domain + Require Auth)
    response = account_set(
        client,
        wallet,
        'user.transia.co'
    )
    print(response)
    # 3. TrustSet
    response = trust_set(
        client,
        wallet,
        currency,
        issuer,
        cur_limit,
    )
    print(response)
    # 4. SignerListSet
    response = signer_list_set(
        client,
        wallet,
        quorum,
        signers
    )
    print(response)
    # 5. TicketCreate
    response = ticket_create(
        client,
        wallet,
        ticketCount,
    )
    print(response)
    # 6. SetRegularKey
    response = set_regular_key(
        client,
        wallet,
        backup,
    )
    print(response)
    # 7. Account Set - (Disable Master)
    # response = disable_master(
    #   client, 
    #   wallet
    # )
    # print(response)
