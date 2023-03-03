import json
import time
from datetime import datetime

from models.account import get_escrows, get_ic_balance
from models.cbdc import deploy_token
from models.payment.channel import (
    claim_payment_channel,
    create_payment_channel,
    fund_payment_channel,
    get_channel_hex,
)
from models.utils import symbol_to_hex
from xrpl.account import get_next_valid_seq_number
from xrpl.clients import Client, JsonRpcClient, WebsocketClient
from xrpl.core import keypairs
from xrpl.core.binarycodec.main import encode_for_signing_claim
from xrpl.models import IssuedCurrencyAmount
from xrpl.models.requests import LedgerCurrent, ServerInfo, Subscribe
from xrpl.models.transactions import (
    AccountSet,
    AccountSetFlag,
    EscrowCancel,
    EscrowCreate,
    EscrowFinish,
    Payment,
    PaymentChannelClaimFlag,
    TrustSet,
)
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.utils import datetime_to_ripple_time
from xrpl.wallet import Wallet, generate_faucet_wallet

bene_seed = "sEdTkfapJTnAstJAYRSUX7BYLahrPaJ"
bene_address = "rpBE9db55fF1eCN8ab6t8GDy9BT1v2AVi5"

player_one_seed = "ssXz5VFS7BRySXerihypXi5iFRVLn"
player_one_address = "rhJ9HNN5qMt8Pg7xFdoDZHT5qF7i2Q8nNA"

player_two_seed = "shvTMb9NF8LzSjbkAVD9uQL7UTkJW"
player_two_address = "rPPa9coh8PMfHbaAkYQJ1gZvJ6FCtLqZTr"

# Cold Wallet
cold_seed = "snDGsELFq5YFuMtmpeyhTVDsVQJqh"
cold_address = "r3hdfcuH53qNTVugRi7hXfh9qQbcGg5G2r"

# Hot Wallet
hot_seed = "snJVtLwDZQhXaqb4oGkvsxF7brrCU"
hot_address = "rGp5XvRbyXAdskg6Rt57fiN6XKapk9CGXB"

WSS_RPC_URL = "wss://vala.ws.transia.co"
w3 = WebsocketClient(WSS_RPC_URL)

with w3 as client:

    currency_code: str = "USD"

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
