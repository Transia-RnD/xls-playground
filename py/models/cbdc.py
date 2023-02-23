
import time
from typing import List, Dict, Any

from xrpl.core import keypairs
from xrpl.clients import WebsocketClient, Client
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.transactions.payment import Payment
from xrpl.models.transactions.offer_cancel import OfferCancel
from xrpl.models.transactions.offer_create import OfferCreate, OfferCreateFlag
from xrpl.models.transactions.trust_set import TrustSet
from xrpl.models.transactions.account_set import AccountSet, AccountSetFlag
from xrpl.models.transactions.signer_list_set import SignerListSet, SignerEntry
from xrpl.models.requests import SubmitMultisigned
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
    submit_transaction
)
from xrpl.core import addresscodec, keypairs

from models.nftoken import mint
from models.token import buy_token, sell_token
from models.utils import symbol_to_hex
from xrpl.utils import xrp_to_drops

from models.nftoken import (
    nftoken_mint,
    nftoken_mint_build,
    nftoken_mint_append
)
from models.multisign import multi_sign
from xrpl.account import get_next_valid_seq_number

def deploy_token(
    client: Client,
    currency_code: str,
    cold_seed: str,
    hot_seed: str,
):
    cold_wallet = Wallet(cold_seed, 0)
    hot_wallet = Wallet(hot_seed, 0)

    # Configure issuer (cold address) settings -------------------------------------
    cold_settings_tx = AccountSet(
        account=cold_wallet.classic_address,
        transfer_rate=0,
        # tick_size=0,
        domain=bytes.hex('https://usd.transia.io'.encode("ASCII")),
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
            value="10000000000", # Large limit, arbitrarily chosen
        )
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
            value=issue_quantity
        )
    )
    pay_prepared = safe_sign_and_autofill_transaction(
        transaction=send_token_tx,
        wallet=cold_wallet,
        client=client,
    )
    print(f"Sending {issue_quantity} {currency_code} to {hot_wallet.classic_address}...")
    response = submit_transaction(pay_prepared, client)
    print(response.result)
    
    return response


def update_cbdc(
    rates: List[float], 
    pinned: float, 
    currency_code: str,
    cold_seed: str,
    hot_seed: str,
):
     with w3 as client:
        print("CONNECTED")
        cold_wallet = Wallet(cold_seed, 0)
        hot_wallet = Wallet(hot_seed, 0)
        for rate in rates:
            # Remove offers ------------------------------------------------------------------


            # Set offers -------------------------------------------------------------------
            price: float = pinned / rate
            send_token_tx = OfferCreate(
                account=hot_wallet.classic_address,
                taker_gets=IssuedCurrencyAmount(
                    currency=symbol_to_hex(currency_code),
                    issuer=cold_wallet.classic_address,
                    value=str(round(pinned, 2))
                ),
                taker_pays=xrp_to_drops(round(price, 2))
            )
            pay_prepared = safe_sign_and_autofill_transaction(
                transaction=send_token_tx,
                wallet=hot_wallet,
                client=client,
            )
            print(f"Setting Offer {currency_code} at ${rate} ...")
            response = send_reliable_submission(pay_prepared, client)
            print(response.result)
            client.close()
            return response

def cancel_sell_order(offer_sequence: int, seed: str):
    wallet = Wallet(seed, 0)
    with w3 as client:
        print("CONNECTED")
        offer_tx = OfferCancel(
            account=wallet.classic_address,
            offer_sequence=offer_sequence,
        )
        ts_prepared = safe_sign_and_autofill_transaction(
            transaction=offer_tx,
            wallet=wallet,
            client=client,
        )
        print(f"Canceling offer for {offer_sequence}...")
        response = send_reliable_submission(ts_prepared, client)
        print(response.result)
        return response


def sell_token_order(currency: str, issuer: str, seed: str, pinned: float, rate: float, amount: float):
    issuer_wallet = Wallet(seed, 0)
    with w3 as client:
        print("CONNECTED")
        price: float = (pinned / rate) * amount
        offer_tx = OfferCreate(
            account=issuer_wallet.classic_address,
            flags=OfferCreateFlag.TF_SELL,
            taker_gets=IssuedCurrencyAmount(
                currency=symbol_to_hex(currency),
                issuer=issuer,
                value=str(pinned * amount)
            ),
            taker_pays=xrp_to_drops(round(price, 2))
        )
        ts_prepared = safe_sign_and_autofill_transaction(
            transaction=offer_tx,
            wallet=issuer_wallet,
            client=client,
        )
        print(f"Creating offer for {currency}...")
        response = send_reliable_submission(ts_prepared, client)
        print(response.result)
        return response


def buy_token_order(currency: str, issuer: str, seed: str, pinned: float, rate: float, amount: float):
    buy_wallet = Wallet(seed, 0)
    with w3 as client:
        print("CONNECTED")

        # Create trust line from hot to cold address -----------------------------------
        trust_set_tx = TrustSet(
            account=buy_wallet.classic_address,
            limit_amount=IssuedCurrencyAmount(
                currency=symbol_to_hex(currency),
                issuer=issuer,
                value="10000000000", # Large limit, arbitrarily chosen
            )
        )
        ts_prepared = safe_sign_and_autofill_transaction(
            transaction=trust_set_tx,
            wallet=buy_wallet,
            client=client,
        )
        print("Creating trust line from hot address to issuer...")
        response = send_reliable_submission(ts_prepared, client)
        print(response.result)

        price: float = (pinned / rate) * amount
        offer_tx = OfferCreate(
            account=buy_wallet.classic_address,
            taker_pays=IssuedCurrencyAmount(
                currency=symbol_to_hex(currency),
                issuer=issuer,
                value=str(pinned * amount)
            ),
            taker_gets=xrp_to_drops(round(price, 2))
        )
        ts_prepared = safe_sign_and_autofill_transaction(
            transaction=offer_tx,
            wallet=buy_wallet,
            client=client,
        )
        print(f"Creating offer for {currency}...")
        response = send_reliable_submission(ts_prepared, client)
        print(response.result)
        return response