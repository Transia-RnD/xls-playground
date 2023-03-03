#!/usr/bin/env python
# coding: utf-8

import time
from typing import List, Dict, Any

from xrpl.clients import Client, WebsocketClient
from xrpl.models.requests.ledger_entry import RippleState
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.requests import AccountLines, LedgerEntry, AccountInfo
from xrpl.models.transactions import Payment, TrustSet, AccountSet, AccountSetFlag
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    submit_transaction,
)
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet


def symbol_to_hex(symbol):
    """symbol_to_hex."""
    if len(symbol) > 3:
        bytes_string = bytes(str(symbol).encode("utf-8"))
        return bytes_string.hex().upper().ljust(40, "0")
    return symbol


def get_rs(client: Client, account: str, issuer: str, currency: str) -> LedgerEntry:
    """get_rs.

    Args:
        client (Client): client
        account (str): account
        issuer (str): issuer
        currency (str): currency

    Returns:
        LedgerEntry: ledger entry
    """
    rs = RippleState(
        currency=currency,
        accounts=[
            account,
            issuer,
        ],
    )
    le = LedgerEntry(ripple_state=rs)
    return client._request_impl(le)


# # Get LE
# # [START] Get LE
# def get_le(client: Client, account: str, issuer: str, currency: str):
#     """get_le."""
#     rs = RippleState(
#         currency=currency,
#         accounts=[
#             account,
#             issuer,
#         ],
#     )
#     le = LedgerEntry(ripple_state=rs)
#     return client._request_impl(le)


# # [END]Get LE


def fund_ic(client: Client, currency_code: str, cold_wallet: Wallet, to_wallet: Wallet):
    tl_amount: int = 1000000
    amount: int = 100000
    balance: float = get_rs(
        client, to_wallet.classic_address, cold_wallet.classic_address, currency_code
    )
    if balance and balance["balance"] >= amount:
        balance_f: float = balance["balance"]
        print(
            f"{to_wallet.classic_address}/{currency_code} ALREADY EXISTS WITH {balance_f} BALANCE"
        )
        return True

    # Create trust line from hot to cold address -----------------------------------
    trust_set_tx = TrustSet(
        account=to_wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value=str(tl_amount),  # Large limit, arbitrarily chosen
        ),
    )
    ts_prepared = safe_sign_and_autofill_transaction(
        transaction=trust_set_tx,
        wallet=to_wallet,
        client=client,
    )
    print(
        f"Creating trust line from {to_wallet.classic_address} to {cold_wallet.classic_address}..."
    )
    response = submit_transaction(ts_prepared, client)
    print(response.result)

    send_token_tx = Payment(
        account=cold_wallet.classic_address,
        destination=to_wallet.classic_address,
        amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value=amount,
        ),
    )
    pay_prepared = safe_sign_and_autofill_transaction(
        transaction=send_token_tx,
        wallet=cold_wallet,
        client=client,
    )
    print(f"Sending {amount} {currency_code} to {to_wallet.classic_address}...")
    response = submit_transaction(pay_prepared, client)
    print(response.result)


def fund(client: Client, wallet: Wallet, destination: str, amount: float):
    drop_value = xrp_to_drops(float(amount))
    if needs_funding(client, drop_value, destination):
        send_token_tx = Payment(
            account=wallet.classic_address,
            destination=destination,
            amount=drop_value,
            # network_id=client.network_id,
        )
        pay_prepared = safe_sign_and_autofill_transaction(
            transaction=send_token_tx,
            wallet=wallet,
            client=client,
        )
        response = submit_transaction(pay_prepared, client)
        return response


def trust_set(client: Client, wallet: Wallet, currency: str, issuer: str, value: float):
    # Create trust line from hot to cold address -----------------------------------
    tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency),
            issuer=issuer,
            value=value,  # Large limit, arbitrarily chosen
        ),
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = submit_transaction(prepared, client)
    print(response.result)


def deploy_token(
    client: Client,
    currency_code: str,
    cold_wallet: Wallet,
    hot_wallet: Wallet,
):

    # Configure issuer (cold address) settings -------------------------------------
    cold_settings_tx = AccountSet(
        account=cold_wallet.classic_address,
        transfer_rate=0,
        # tick_size=0,
        domain=bytes.hex("https://usd.transia.io".encode("ASCII")),
        set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
    )
    cst_prepared = safe_sign_and_autofill_transaction(
        transaction=cold_settings_tx,
        wallet=cold_wallet,
        client=client,
    )
    print("Sending cold address AccountSet transaction...")
    response = submit_transaction(cst_prepared, client)
    print(response.result)

    # Configure hot address settings -----------------------------------------------
    hot_settings_tx = AccountSet(
        account=hot_wallet.classic_address,
        clear_flag=AccountSetFlag.ASF_REQUIRE_AUTH,
    )
    hst_prepared = safe_sign_and_autofill_transaction(
        transaction=hot_settings_tx,
        wallet=hot_wallet,
        client=client,
    )
    print("Sending hot address AccountSet transaction...")
    response = submit_transaction(hst_prepared, client)
    print(response.result)

    # Create trust line from hot to cold address -----------------------------------
    trust_set_tx = TrustSet(
        account=hot_wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value="10000000000",  # Large limit, arbitrarily chosen
        ),
    )
    ts_prepared = safe_sign_and_autofill_transaction(
        transaction=trust_set_tx,
        wallet=hot_wallet,
        client=client,
    )
    print("Creating trust line from hot address to issuer...")
    response = submit_transaction(ts_prepared, client)
    print(response.result)

    # Send token -------------------------------------------------------------------
    issue_quantity = "1000000"
    send_token_tx = Payment(
        account=cold_wallet.classic_address,
        destination=hot_wallet.classic_address,
        amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value=issue_quantity,
        ),
    )
    pay_prepared = safe_sign_and_autofill_transaction(
        transaction=send_token_tx,
        wallet=cold_wallet,
        client=client,
    )
    print(
        f"Sending {issue_quantity} {currency_code} to {hot_wallet.classic_address}..."
    )
    response = submit_transaction(pay_prepared, client)
    print(response.result)

    return response


def needs_funding(client: WebsocketClient, exp_balance: int, account: str):
    result = client.request(
        AccountInfo(
            account=account,
        ),
    )
    if "error" in result.result and result.result["error"] == "actNotFound":
        print("actNotFound")
        return True

    balance = result.result["account_data"]["Balance"]
    if int(balance) < int(exp_balance):
        return True
    return False
