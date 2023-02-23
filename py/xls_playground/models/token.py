

from xrpl.models.transactions import OfferCreate, OfferCreateFlag, OfferCancel, TrustSet
from xrpl.utils import xrp_to_drops
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from models.utils import symbol_to_hex

from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission
)

# Buy Token
# [START] Buy Token
def buy_token(
    client,
    wallet,
    issuer,
    currency,
    amount,
    rate,
):
    """buy."""
    curr_value = IssuedCurrencyAmount(
        currency=currency,
        issuer=issuer,
        value=str(round(amount, 2))
    )
    drop_value = xrp_to_drops(float(round(amount, 2)) * rate)
    built_transaction = OfferCreate(
        account=wallet.classic_address,
        taker_pays=curr_value,
        taker_gets=drop_value,
        # flags=OfferCreateFlag.TF_PASSIVE
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=client,
    )
    return send_reliable_submission(signed_tx, client)
# [END] Buy Token

# Sell Token
# [START] Sell Token
def sell_token(
    client,
    wallet,
    issuer,
    currency,
    amount,
    total_cost,
):
    """sell."""
    curr_value = IssuedCurrencyAmount(
        currency=currency,
        issuer=issuer,
        value=str(round(amount, 2))
    )
    drop_value = xrp_to_drops(total_cost)
    built_transaction = OfferCreate(
        account=wallet.classic_address,
        taker_pays=drop_value,
        taker_gets=curr_value,
        flags=OfferCreateFlag.TF_SELL
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=client,
    )
    return send_reliable_submission(signed_tx, client)
# [END] Sell Token

def sell_token_ic(
    client,
    wallet,
    tp_issuer,
    tp_currency,
    tp_acount,
    tg_issuer,
    tg_currency,
    tg_amount,
):
    offer_tx = OfferCreate(
        account=wallet.classic_address,
        flags=OfferCreateFlag.TF_SELL,
        taker_pays=IssuedCurrencyAmount(
            currency=symbol_to_hex(tp_currency),
            issuer=tp_issuer,
            value=tp_acount
        ),
        taker_gets=IssuedCurrencyAmount(
            currency=symbol_to_hex(tg_currency),
            issuer=tg_issuer,
            value=tg_amount
        )
    )
    ts_prepared = safe_sign_and_autofill_transaction(
        transaction=offer_tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(ts_prepared, client)
    print(response.result)


def trustline(
    client,
    wallet,
    issuer: str,
    currency: str,
    amount: str = "10000000000",
):
    # Create trust line from hot to cold address -----------------------------------
    trust_set_tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency),
            issuer=issuer,
            value=amount, # Large limit, arbitrarily chosen
        )
    )
    ts_prepared = safe_sign_and_autofill_transaction(
        transaction=trust_set_tx,
        wallet=wallet,
        client=client,
    )
    print(f"Creating trust line from {wallet.classic_address} to {currency}...")
    response = send_reliable_submission(ts_prepared, client)
    print(response.result)
    return response


def cancel_offer(
    client,
    wallet,
    offer_sequence: int
):
    offer_tx = OfferCancel(
        account=wallet.classic_address,
        offer_sequence=int(offer_sequence),
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