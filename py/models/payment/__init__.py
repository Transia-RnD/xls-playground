
from xrpl.clients import Client
from xrpl.wallet import Wallet

from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.trust_set import TrustSet
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount

from xrpl.utils import xrp_to_drops, str_to_hex
from models.utils import symbol_to_hex
from models.account import get_ic_balance

from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
    submit_transaction
)

def fund_ic(client: Client, currency_code: str, cold_wallet: Wallet, to_wallet: Wallet):
    tl_amount: int = 1000000
    amount: int = 100000
    balance: float = get_ic_balance(
        client, 
        to_wallet.classic_address,
        cold_wallet.classic_address,
        currency_code
    )
    if balance and balance['balance'] >= amount:
        balance_f: float = balance['balance']
        print(f'{to_wallet.classic_address}/{currency_code} ALREADY EXISTS WITH {balance_f} BALANCE')
        return True

    # Create trust line from hot to cold address -----------------------------------
    trust_set_tx = TrustSet(
        account=to_wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value=str(tl_amount), # Large limit, arbitrarily chosen
        )
    )
    ts_prepared = safe_sign_and_autofill_transaction(
        transaction=trust_set_tx,
        wallet=to_wallet,
        client=client,
    )
    print(f"Creating trust line from {to_wallet.classic_address} to {cold_wallet.classic_address}...")
    response = submit_transaction(ts_prepared, client)
    print(response.result)
    
    send_token_tx = Payment(
        account=cold_wallet.classic_address,
        destination=to_wallet.classic_address,
        amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value=amount
        )
    )
    pay_prepared = safe_sign_and_autofill_transaction(
        transaction=send_token_tx,
        wallet=cold_wallet,
        client=client,
    )
    print(f"Sending {amount} {currency_code} to {to_wallet.classic_address}...")
    response = submit_transaction(pay_prepared, client)
    print(response.result)


def xrp_payment(
  client: Client,
  wallet: Wallet,
  destination: str,
  amount: float
):
    drop_value = xrp_to_drops(float(amount))
    send_token_tx = Payment(
        account=wallet.classic_address,
        destination=destination,
        amount=drop_value
    )
    pay_prepared = safe_sign_and_autofill_transaction(
        transaction=send_token_tx,
        wallet=wallet,
        client=client,
    )
    response = submit_transaction(pay_prepared, client)
    return response


def trust_set(
  client: Client,
  wallet: Wallet,
  currency: str,
  issuer: str,
  value: float
):
    # Create trust line from hot to cold address -----------------------------------
    tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency),
            issuer=issuer,
            value=value, # Large limit, arbitrarily chosen
        )
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = submit_transaction(prepared, client)
    print(response.result)