#!/usr/bin/env python
# coding: utf-8

import time
from typing import List, Dict, Any, Union

from xrpl.core.keypairs import generate_seed
from xrpl.clients import Client, WebsocketClient
from xrpl.models.requests.ledger_entry import RippleState
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.requests import GenericRequest, LedgerEntry, AccountInfo
from xrpl.models.transactions import (
    Transaction,
    Payment,
    TrustSet,
    AccountSet,
    AccountSetFlag
)
from xrpl.transaction import (
    get_transaction_from_hash,
    safe_sign_and_autofill_transaction,
    submit_transaction,
)
from xrpl.utils import xrp_to_drops
from xrpl.wallet import Wallet
from xrpl.core.addresscodec import decode_classic_address

from xrpl_helpers.sdk.utils import symbol_to_hex

from testing_config import BaseTestConfig

LEDGER_ACCEPT_REQUEST = GenericRequest(method="ledger_accept")


def wait_for_result(client: WebsocketClient, tx_hash: str):
    """"""
    timeout: int = 0
    while timeout <= 8:
        client.request(LEDGER_ACCEPT_REQUEST)
        response = get_transaction_from_hash(tx_hash=tx_hash, client=client)
        if 'validated' in response.result and response.result['validated'] is True:
            return response
        time.sleep(1)
        timeout += 1
    raise ValueError('test transaction timeout')


class Account(object):
    """"""
    name: str
    account: str
    wallet: Wallet

    def __init__(self, name: str = None, seed: str = None) -> None:
        if seed:
            self.wallet = Wallet(seed, 0)
            self.account = self.wallet.classic_address
            pass

        self.name = name
        if name == 'gw':
            self.wallet = Wallet("sEdSmmFciyvxYaQcdRCv4FhYEJ1aqpn", 0)
            self.account = self.wallet.classic_address
        if name == 'alice':
            self.wallet = Wallet("sEd7mHoS84UWye8epfNvHXkeET1Btfd", 0)
            self.account = self.wallet.classic_address
        if name == 'bob':
            self.wallet = Wallet("sEdTQgHLuZVjcYGoBRV2hvq2iDXUDWZ", 0)
            self.account = self.wallet.classic_address
        if name == 'carol':
            self.wallet = Wallet("sEdSbbjTvsKZ8xNkJSyHVBYPNY3jkR9", 0)
            self.account = self.wallet.classic_address
        if name == 'dave':
            self.wallet = Wallet("sEdSmJx74N6UiDm2uwVzLBmkVuR3HTy", 0)
            self.account = self.wallet.classic_address
        if name == 'elsa':
            self.wallet = Wallet("sEdTeiqmPdUob32gyD6vPUskq1Z7TP3", 0)
            self.account = self.wallet.classic_address

        if not self.wallet:
            self.wallet = Wallet.create()
            self.account = self.wallet.classic_address
        pass


class ICXRP(object):
    """"""
    issuer: str
    currency: str = 'XRP'
    value: float
    amount: str

    def __init__(self, value: float) -> None:
        self.value = value
        self.amount = xrp_to_drops(value)
        pass


class IC(object):
    """"""
    issuer: str
    currency: str
    value: float
    amount: IssuedCurrencyAmount

    @staticmethod
    def gw(name: str, gw: Account) -> 'IC':
        self = IC()
        self.issuer = gw.account
        self.currency = symbol_to_hex(name)
        return self

    def __call__(self, value: float) -> Any:
        self.value = value
        self.amount = IssuedCurrencyAmount(
            issuer=self.issuer,
            currency=self.currency,
            value=self.value,
        )
        return self

    def __init__(self) -> None:
        pass


def xrp_balance(ctx: WebsocketClient, account: Account) -> float:
    response = ctx.request(
        AccountInfo(
            account=account.account,
        ),
    )
    if "error" in response.result and response.result["error"] == "actNotFound":
        # print(response.result["error"])
        return 0
    return float(response.result["account_data"]["Balance"])


def ic_balance(ctx: WebsocketClient, account: Account, ic: IC) -> float:
    rs = RippleState(
        currency=ic.currency,
        accounts=[
            account.account,
            ic.issuer,
        ],
    )
    request = LedgerEntry(ripple_state=rs)
    response = ctx.request(request)
    if "error" in response.result:
        # print(response.result["error"])
        return 0
    return abs(float(response.result['node']['Balance']['value']))


def balance(ctx: WebsocketClient, account: Account, ic: IC = None) -> float:
    if not ic:
        return xrp_balance(ctx, account)
    return ic_balance(ctx, account, ic)


def limit(ctx: WebsocketClient, account: Account, ic: IC) -> float:
    rs = RippleState(
        currency=ic.currency,
        accounts=[
            account.account,
            ic.issuer,
        ],
    )
    is_high_limit: bool = decode_classic_address(account.account) > decode_classic_address(ic.issuer)
    request = LedgerEntry(ripple_state=rs)
    response = ctx.request(request)
    if "error" in response.result:
        # print(response.result["error"])
        return 0
    node: Dict[str, Any] = response.result['node']
    return float(node['HighLimit']['value'] if is_high_limit else node['LowLimit']['value'])


def fund(ctx: WebsocketClient, wallet: Wallet, uicx: Union[IC, ICXRP], *accts: Account):
    for acct in accts:
        prepared_tx = Payment(
            account=wallet.classic_address,
            destination=acct.account,
            amount=uicx.amount,
            # network_id=client.network_id,
        )
        signed_tx = safe_sign_and_autofill_transaction(
            transaction=prepared_tx,
            wallet=wallet,
            client=ctx,
        )
        response = submit_transaction(signed_tx, ctx)
        if "error" in response.result:
            print(response.result["error"])
        tx_result: str = response.result['engine_result']
        if tx_result != 'tesSUCCESS':
            print(f'FUND FAILED: {tx_result}')
        tx_hash: str = response.result["tx_json"]["hash"]
        wait_for_result(ctx, tx_hash)


def pay(ctx: WebsocketClient, uicx: Union[IC, ICXRP], signer: Account, *accts: Account):
    for acct in accts:
        prepared_tx = Payment(
            account=signer.account,
            destination=acct.account,
            amount=uicx.amount,
            # network_id=client.network_id,
        )
        signed_tx = safe_sign_and_autofill_transaction(
            transaction=prepared_tx,
            wallet=signer.wallet,
            client=ctx,
        )
        response = submit_transaction(signed_tx, ctx)
        if "error" in response.result:
            print(response.result["error"])
        tx_result: str = response.result['engine_result']
        if tx_result != 'tesSUCCESS':
            print(f'PAY FAILED: {tx_result}')
        tx_hash: str = response.result["tx_json"]["hash"]
        wait_for_result(ctx, tx_hash)


def trust(ctx: WebsocketClient, uicx: Union[IC, ICXRP], *accts: Account):
    for acct in accts:
        prepared_tx = TrustSet(
            account=acct.account,
            limit_amount=uicx.amount,
        )
        signed_tx = safe_sign_and_autofill_transaction(
            transaction=prepared_tx,
            wallet=acct.wallet,
            client=ctx,
        )
        response = submit_transaction(signed_tx, ctx)
        if "error" in response.result:
            print(response.result["error"])
        tx_result: str = response.result['engine_result']
        if tx_result != 'tesSUCCESS':
            print(f'TRUST FAILED: {tx_result}')
        tx_hash: str = response.result["tx_json"]["hash"]
        wait_for_result(ctx, tx_hash)


def account_set(ctx: WebsocketClient, account: Account):
    tx = AccountSet(
        account=account.account,
        transfer_rate=0,
        # tick_size=0,
        domain=bytes.hex("https://usd.transia.io".encode("ASCII")),
        set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=account.wallet,
        client=ctx,
    )
    response = submit_transaction(signed_tx, ctx)
    if "error" in response.result:
        print(response.result["error"])
    tx_result: str = response.result['engine_result']
    if tx_result != 'tesSUCCESS':
        print(f'FUND FAILED: {tx_result}')
    tx_hash: str = response.result["tx_json"]["hash"]
    wait_for_result(ctx, tx_hash)


def rpc(ctx: WebsocketClient, account: Account, txjson: Dict[str, Any]):
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=Transaction.from_xrpl(txjson),
        wallet=account.wallet,
        client=ctx,
    )
    response = submit_transaction(signed_tx, ctx)
    if "error" in response.result:
        print(response.result["error"])
    tx_result: str = response.result['engine_result']
    if tx_result != 'tesSUCCESS':
        print(f'FUND FAILED: {tx_result}')
    tx_hash: str = response.result["tx_json"]["hash"]
    wait_for_result(ctx, tx_hash)


def close(ctx: WebsocketClient):
    ctx.request(LEDGER_ACCEPT_REQUEST)
