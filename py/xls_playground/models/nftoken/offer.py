"""offer.py."""

from typing import List

from xrpl.clients import WebsocketClient, Client
from xrpl.wallet import Wallet
from xrpl.models.transactions import (
    Memo,
    NFTokenCreateOffer,
    NFTokenCancelOffer,
    NFTokenAcceptOffer,
    NFTokenCreateOfferFlag
)
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)
from xrpl.utils import xrp_to_drops
from xrpl.models.requests import NFTBuyOffers, NFTSellOffers


# Buy Book
# [START] Buy Book
def nftoken_buy_book(
    w3: WebsocketClient, 
    nftoken_id: str
):
    """buy_book."""
    response =  w3.request(
        NFTBuyOffers(
            nft_id=nftoken_id,
        ),
    )
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    
    print(response.result)
    return response.result['offers']
    
# [END] Buy Book


# Sell Book
# [START] Sell Book
def nftoken_sell_book(
    w3: WebsocketClient, 
    nftoken_id: str
):
    """sell_book."""
    response = w3.request(
        NFTSellOffers(
            nft_id=nftoken_id
        ),
    )
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    
    print(response.result)
    return response.result['offers']
# [END] Sell Book


# Buy
# [START] Buy
def nftoken_buy(
    w3: WebsocketClient,
    wallet: Wallet,
    nftoken_id: str,
    price: float,
    owner: str,
    expiration: int = 0,
    destination: str = None
):
    """nftoken_buy."""
    drop_value = xrp_to_drops(price)
    built_transaction = NFTokenCreateOffer(
        account=wallet.classic_address,
        nftoken_id=nftoken_id,
        amount=drop_value,
        owner=owner,
        # expiration=expiration,
        # destination=destination
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Buy

# Sell
# [START] Sell
def nftoken_sell(
    w3: WebsocketClient,
    wallet: Wallet,
    nftoken_id: str,
    price: float,
    expiration: int = 0,
    destination: str = None
):
    """nftoken_sell."""
    drop_value = xrp_to_drops(price)
    built_transaction = NFTokenCreateOffer(
        account=wallet.classic_address,
        nftoken_id=nftoken_id,
        amount=drop_value,
        # expiration=expiration,
        # destination=destination,
        flags=[NFTokenCreateOfferFlag.TF_SELL_NFTOKEN],
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Sell

# Sell IC
# [START] Sell IC
def nftoken_sell_ic(
    w3: Client,
    wallet: Wallet,
    owner: str,
    nftoken_id: str,
    ica: IssuedCurrencyAmount,
    memos: List[Memo],
    expiration: int = 0,
    destination: str = None
):
    """nftoken_sell_ic."""
    drop_value = xrp_to_drops(0.0001)
    built_transaction = NFTokenCreateOffer(
        account=wallet.classic_address,
        owner=owner,
        nftoken_id=nftoken_id,
        amount=drop_value,
        # amount=ica,
        # expiration=expiration,
        # destination=destination
        memos=memos
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Sell IC


# Accept Buy
# [START] Accept Buy
def nftoken_accept_buy(
    w3,
    wallet,
    account,
    buy_offer,
    sell_offer,
    broker_fee,
):
    """nftoken_accept_buy."""
    built_transaction = NFTokenAcceptOffer(
        account=account,
        buy_offer=buy_offer,
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Accept Buy

# Accept Sell
# [START] Accept Sell
def nftoken_accept_sell(
    w3,
    wallet,
    account,
    buy_offer,
    sell_offer,
    broker_fee,
):
    """accept_sell."""
    built_transaction = NFTokenAcceptOffer(
        account=account,
        sell_offer=sell_offer,
    )
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Accept Sell


# Broker Sell
# [START] Broker Sell
def nftoken_broker(
    w3,
    wallet,
    buy_offer,
    sell_offer,
    broker_fee,
):
    """nftoken_broker."""
    built_transaction = NFTokenAcceptOffer(
        account=wallet.classic_address,
        nftoken_buy_offer=buy_offer,
        nftoken_sell_offer=sell_offer,
    )
    
    if broker_fee > 0:
        built_transaction.nftoken_broker_fee=xrp_to_drops(broker_fee)
    
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
    
# [END] Broker Sell


# Cancel Offer
# [START] Cancel Offer
def nftoken_cancel_offers(
    w3: Client,
    wallet: Wallet,
    nftoken_offers: List[str],
):
    """nftoken_cancel_offers."""
    built_transaction = NFTokenCancelOffer(
        account=wallet.classic_address,
        nftoken_offers=nftoken_offers
    )
    
    signed_tx = safe_sign_and_autofill_transaction(
        transaction=built_transaction,
        wallet=wallet,
        client=w3,
    )
    return send_reliable_submission(signed_tx, w3)
# [END] Cancel Offer