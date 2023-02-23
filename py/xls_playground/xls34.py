import json
import time
from datetime import datetime
from xrpl.clients import WebsocketClient, JsonRpcClient, Client
from xrpl.models.requests import ServerInfo, LedgerCurrent
from xrpl.models.requests import (
    Subscribe,
)
from xrpl.core import keypairs
from xrpl.account import get_next_valid_seq_number
from xrpl.models import IssuedCurrencyAmount
from xrpl.models.transactions import EscrowCreate, EscrowCancel, EscrowFinish
from xrpl.utils import datetime_to_ripple_time
from xrpl.models.transactions import Payment, AccountSet, AccountSetFlag, TrustSet, PaymentChannelClaimFlag
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.core.binarycodec.main import (
    encode_for_signing_claim,
)

from models.utils import symbol_to_hex
from models.account import get_escrows, get_ic_balance
from models.cbdc import deploy_token
from models.payment.channel import (
    create_payment_channel,
    fund_payment_channel,
    claim_payment_channel,
    get_channel_hex
)

bene_seed = 'sEdTkfapJTnAstJAYRSUX7BYLahrPaJ'
bene_address = 'rpBE9db55fF1eCN8ab6t8GDy9BT1v2AVi5'

player_one_seed = 'ssXz5VFS7BRySXerihypXi5iFRVLn'
player_one_address = 'rhJ9HNN5qMt8Pg7xFdoDZHT5qF7i2Q8nNA'

player_two_seed = 'shvTMb9NF8LzSjbkAVD9uQL7UTkJW'
player_two_address = 'rPPa9coh8PMfHbaAkYQJ1gZvJ6FCtLqZTr'

# Cold Wallet
cold_seed = 'snDGsELFq5YFuMtmpeyhTVDsVQJqh'
cold_address = 'r3hdfcuH53qNTVugRi7hXfh9qQbcGg5G2r'

# Hot Wallet
hot_seed = 'snJVtLwDZQhXaqb4oGkvsxF7brrCU'
hot_address = 'rGp5XvRbyXAdskg6Rt57fiN6XKapk9CGXB'

WSS_RPC_URL = "wss://vala.ws.transia.co"
w3 = WebsocketClient(WSS_RPC_URL)

def fund_ic(currency_code: str, cold_wallet: Wallet, to_wallet: Wallet):
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
    response = send_reliable_submission(ts_prepared, client)
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
    response = send_reliable_submission(pay_prepared, client)
    print(response.result)


def escrow_create(
    client: Client,
    wallet: Wallet,
    owner: str,
    finish_after: int = None,
    cancel_after: int = None
):
    # ESCROW CREATE
    if finish_after:
        finish_after = datetime_to_ripple_time(datetime.now()) + finish_after
    if cancel_after:
        cancel_after = datetime_to_ripple_time(datetime.now()) + cancel_after
    # escrow_amount: int = 10
    tx = EscrowCreate(
        account=wallet.classic_address,
        amount=IssuedCurrencyAmount(
            currency=symbol_to_hex(currency_code),
            issuer=cold_wallet.classic_address,
            value="10"
        ),
        destination=owner,
        finish_after=finish_after,
        cancel_after=cancel_after
    )
    escrow_prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(escrow_prepared, client)
    print(response.result)
    if response.result['meta']['TransactionResult'] != 'tesSUCCESS':
        tx_result: str = response.result['meta']['TransactionResult']
        print(json.dumps(response.result, indent=4, sort_keys=True))
        raise ValueError(f'invalid response result: {tx_result}')
    
    return response.result['Sequence']


def escrow_cancel(
    client: Client,
    wallet: Wallet,
    owner: str,
    sequence: str
):
    tx = EscrowCancel(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=sequence
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    print(response.result)

def escrow_finish(
    client: Client,
    wallet: Wallet,
    owner: str,
    sequence: str,
    condition: str = None,
    fulfillment: str = None,
):
    tx = EscrowFinish(
        account=wallet.classic_address,
        owner=owner,
        offer_sequence=sequence,
        condition=condition,
        fulfillment=fulfillment,
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    # print(response.result)

with w3 as client:

    currency_code: str = 'USD'
    
    cold_wallet = Wallet(cold_seed, 0)
    hot_wallet = Wallet(hot_seed, 0)
    p_one = Wallet(player_one_seed, 0)
    p_two = Wallet(player_two_seed, 0)

    # get_objects(client)

    # generate_faucet_wallet(client, cold_wallet, True, 'vala.faucet.transia.co')
    # generate_faucet_wallet(client, hot_wallet,  True, 'vala.faucet.transia.co')
    # deploy_token(client, currency_code, cold_seed, hot_seed)

    # generate_faucet_wallet(client, p_one,  True, 'vala.faucet.transia.co')
    fund_ic(currency_code, cold_wallet, p_one)

    # generate_faucet_wallet(client, p_two,  True, 'vala.faucet.transia.co')
    fund_ic(currency_code, cold_wallet, p_two)

    # escrows = get_escrows(client, p_one.classic_address)
    # for escrow in escrows:
    #     print(json.dumps(escrow, indent=4, sort_keys=True))

    # sequence: int = escrow_create(
    #     client,
    #     p_one,
    #     p_one.classic_address,
    #     5,
    # )
    # time.sleep(1)


    # escrow_finish(
    #     client,
    #     p_two,
    #     p_one.classic_address,
    #     sequence
    # )
    # sequence: int = escrow_create(
    #     client,
    #     p_one,
    #     p_one.classic_address,
    #     1,
    #     2,
    # )
    # time.sleep(1)
    # escrow_cancel(
    #     client,
    #     p_two,
    #     p_one.classic_address,
    #     sequence
    # )

    # create_result = create_payment_channel(
    #     client,
    #     p_one,
    #     p_two.classic_address,
    #     amount=IssuedCurrencyAmount(
    #         currency=symbol_to_hex(currency_code),
    #         issuer=cold_wallet.classic_address,
    #         value="10"
    #     ),
    #     public_key=p_one.public_key,
    #     settle_delay=5
    # )

    # channel: str = get_channel_hex(create_result['meta'])
    # print(channel)
    
    # fund_result = fund_payment_channel(
    #     client,
    #     p_one,
    #     channel,
    #     amount=IssuedCurrencyAmount(
    #         currency=symbol_to_hex(currency_code),
    #         issuer=cold_wallet.classic_address,
    #         value="10"
    #     ),
    #     expiration=None
    # )

    # print(fund_result)

    # # drops_amount = xrp_to_drops(10)

    # amount =IssuedCurrencyAmount(
    #     currency=symbol_to_hex(currency_code),
    #     issuer=cold_wallet.classic_address,
    #     value="10"
    # )
    # _json = {"amount": amount.to_dict(), "channel": channel}
    # encoded = encode_for_signing_claim(_json)
    # signature = keypairs.sign(bytes.fromhex(encoded), p_one.private_key)

    # claim_result = claim_payment_channel(
    #     client,
    #     p_one,
    #     channel,
    #     amount=IssuedCurrencyAmount(
    #         currency=symbol_to_hex(currency_code),
    #         issuer=cold_wallet.classic_address,
    #         value="10"
    #     ),
    #     balance=IssuedCurrencyAmount(
    #         currency=symbol_to_hex(currency_code),
    #         issuer=cold_wallet.classic_address,
    #         value="10"
    #     ),
    #     signature=signature,
    #     public_key=p_one.public_key,
    #     flags=PaymentChannelClaimFlag.TF_CLOSE
    # )

    # print(claim_result)