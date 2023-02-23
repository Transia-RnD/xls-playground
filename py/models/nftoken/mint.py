#!/usr/bin/env python
# coding: utf-8

import time
from typing import Dict, Any, List

from xrpl.clients import WebsocketClient
from xrpl.wallet import Wallet
from xrpl.account import get_next_valid_seq_number
from xrpl.models import Signer
from xrpl.models.transactions import NFTokenMintFlag, NFTokenMint
from xrpl.models.requests import (
    Tx,
)
from xrpl.transaction import (
    autofill,
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)
from xrpl.utils import str_to_hex

from .utils import get_token_id_from_meta


# Mint
# [START] Mint
def nftoken_mint(
    w3: WebsocketClient,
    wallet: Wallet,
    nftoken_taxon: int,
    transfer_fee: int,
    uri: str,
):
    """nftoken_mint."""
    built_transaction = NFTokenMint(
        account=wallet.classic_address,
        nftoken_taxon=nftoken_taxon,
        transfer_fee=transfer_fee,
        uri=str_to_hex(uri),
        flags=[
            NFTokenMintFlag.TF_TRANSFERABLE,
            NFTokenMintFlag.TF_BURNABLE
        ],

    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    response = send_reliable_submission(signed_tx, w3)
    time.sleep(1)
    print(response.result)
    print(response.result['meta'])
    tx_hash: str = response.result['hash']
    post_response = w3.request(Tx(transaction=tx_hash))
    print(post_response.result)
    nftoken_id: str = get_token_id_from_meta(post_response.result['meta'])
    print(nftoken_id)
    return nftoken_id
# [END] Mint

# Mint Build
# [START] Mint Build
def nftoken_mint_build(
    w3: WebsocketClient,
    account: str,
    nftoken_taxon: int,
    transfer_fee: int,
    uri: str
) -> Dict[str, Any]:
    """nftoken_mint."""
    built_transaction = NFTokenMint(
        account=account,
        nftoken_taxon=nftoken_taxon,
        transfer_fee=transfer_fee,
        uri=str_to_hex(uri),
        flags=[
            NFTokenMintFlag.TF_TRANSFERABLE,
            NFTokenMintFlag.TF_BURNABLE
        ],
        fee='100'
    )
    return autofill(built_transaction, w3)
# [END] Mint Build


# Mint Append
# [START] Mint Append
def nftoken_mint_append(
    fee: str,
    sequence: str,
    lls: str,
    signers: List[Signer],
    account: str,
    nftoken_taxon: int,
    transfer_fee: int,
    uri: str
) -> Dict[str, Any]:
    """nftoken_mint_append."""
    built_transaction = NFTokenMint(
        account=account,
        nftoken_taxon=nftoken_taxon,
        transfer_fee=transfer_fee,
        uri=str_to_hex(uri),
        flags=[
            NFTokenMintFlag.TF_TRANSFERABLE,
            NFTokenMintFlag.TF_BURNABLE
        ],
        signers=signers,
        fee="100",
        sequence=sequence,
        last_ledger_sequence=lls,
    )
    return built_transaction
# [END] Mint Build