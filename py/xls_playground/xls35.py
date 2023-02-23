import json
import time
from datetime import datetime
from xrpl.clients import WebsocketClient
from xrpl.models.requests import AccountInfo, AccountObjects, AccountObjectType
from xrpl.wallet import Wallet

from xrpl.models import IssuedCurrencyAmount
from models.utils import symbol_to_hex, get_object_id
from models.account import get_ic_balance
from models.payment import xrp_payment, fund_ic
from models.cbdc import deploy_token
from models.uritoken import (
    uritoken_mint, 
    uritoken_burn,
    uritoken_sell,
    uritoken_clear,
    uritoken_buy
)

# -----------------------------------------------------------------------------

masterAccount: str = 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh'
masterSecret = 'snoPBrXtMeMyMHUVTgbuqAfg1SUTb'

cold_seed = 'sEd7yKm7WVSDkYvpMjvyma7vUiVZiXa'
hot_seed = 'sEd7b6dwNM1J7fM3aLRZ53JXRqJ99Gf'
buyer_seed = 'sEdTF2b3WePkNbmBBborKEXR9Vk3eBB'
seller_seed = 'sEdTVG8mVTxNRoCJ7YiYhqmgGCzfTZ1'


WSS_RPC_URL = "ws://localhost:6006"
w3 = WebsocketClient(WSS_RPC_URL)

with w3 as client:

    currency_code: str = 'USD'
    
    cold_wallet = Wallet(cold_seed, 0)
    # cold_wallet = Wallet.create()
    hot_wallet = Wallet(hot_seed, 0)
    # hot_wallet = Wallet.create()
    buyer_wallet = Wallet(buyer_seed, 0)
    # buyer_wallet = Wallet.create()
    seller_wallet = Wallet(seller_seed, 0)
    # seller_wallet = Wallet.create()

    # get_objects(client)

    # cold_response = xrp_payment(
    #     client,
    #     Wallet(masterSecret, 0),
    #     cold_wallet.classic_address,
    #     1000,
    # )
    # hot_response = xrp_payment(
    #     client,
    #     Wallet(masterSecret, 0),
    #     hot_wallet.classic_address,
    #     1000,
    # )
    # seller_response = xrp_payment(
    #     client,
    #     Wallet(masterSecret, 0),
    #     seller_wallet.classic_address,
    #     1000,
    # )
    # buyer_response = xrp_payment(
    #     client,
    #     Wallet(masterSecret, 0),
    #     buyer_wallet.classic_address,
    #     1000,
    # )
    # deploy_token(client, currency_code, cold_wallet.seed, hot_wallet.seed)

    # fund_ic(client, currency_code, cold_wallet, seller_wallet)

    # fund_ic(client, currency_code, cold_wallet, buyer_wallet)

    # wallet = Wallet(masterSecret, 0)
    # print(wallet.classic_address)
    # result = client.request(
    #     AccountInfo(
    #         account=wallet.classic_address,
    #     ),
    # )
    # balance = int(result.result["account_data"]["Balance"])
    # print(balance)

    # object_id = get_object_id(result['meta'], 'URIToken')
    # print(object_id)
    # object_id = '510220E76365AD511225F8039CE5B4DFDF9A6AA81F23B935397E29AF035B0952'
    # print(object_id)

    # expected = "1"
    # max_fee = drops_to_xrp(expected)
    # result = get_fee(client, max_fee=max_fee)
    # print(result)

    # response = client.request(
    #     Tx(transaction='9611FA845F71075EC78890FA90D2AC88EB98DDAEF00AE77B6E6EA58E965A52A8')
    # )
    # print(json.dumps(response.result, indent=4, sort_keys=True))

    # MINT
    # -----------------------------------------------------------------------------

    # mint_response = uritoken_mint(
    #     client,
    #     seller_wallet,
    #     'ipfs://QmaCtDKZFVvvfufvbdy4estZbhQH7DXh16CTpv1howmBGy'
    # )
    # print(json.dumps(mint_response.result, indent=4, sort_keys=True))

    # BURN
    # -----------------------------------------------------------------------------
    object_id = 'C6B2BE3C1D59B127F36BC0EE8642B3E8B5AC61C8389B8F0E3DDA0B1EFB35029A'
    # burn_response = uritoken_burn(
    #     client,
    #     seller_wallet,
    #     object_id
    # )
    # print(json.dumps(burn_response.result, indent=4, sort_keys=True))

    # SELL
    # -----------------------------------------------------------------------------

    # amount = IssuedCurrencyAmount(
    #     currency=symbol_to_hex(currency_code),
    #     issuer=cold_wallet.classic_address,
    #     value="10"
    # )

    # sell_response = uritoken_sell(
    #     client,
    #     seller_wallet,
    #     object_id,
    #     amount
    # )
    # print(json.dumps(sell_response.result, indent=4, sort_keys=True))

    # CLEAR
    # -----------------------------------------------------------------------------
    # clear_response = uritoken_clear(
    #     client,
    #     wallet,
    #     object_id,
    # )
    # print(json.dumps(clear_response.result, indent=4, sort_keys=True))

    # BUY
    # -----------------------------------------------------------------------------

    amount = IssuedCurrencyAmount(
        currency=symbol_to_hex(currency_code),
        issuer=cold_wallet.classic_address,
        value="10"
    )

    buy_response = uritoken_buy(
        client,
        buyer_wallet,
        object_id,
        amount
    )
    print(json.dumps(buy_response.result, indent=4, sort_keys=True))

    # ACCOUNT OBJECTS - URITOKEN
    # -----------------------------------------------------------------------------

    req = AccountObjects(account=seller_wallet.classic_address, type=AccountObjectType.URI_TOKEN)
    response = client.request(req)
    print(json.dumps(response.result, indent=4, sort_keys=True))
    req = AccountObjects(account=buyer_wallet.classic_address, type=AccountObjectType.URI_TOKEN)
    response = client.request(req)
    print(json.dumps(response.result, indent=4, sort_keys=True))