import json
import time
import binascii
import os
from datetime import datetime
from typing import Optional, List

# xrpl
from xrpl.clients import WebsocketClient, Client
from xrpl.wallet import Wallet
from xrpl.models.requests import ServerInfo
from xrpl.models.transactions import (
    Payment,
)
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    submit_transaction,
)
from xrpl.utils import xrp_to_drops

# -----------------------------------------------------------------------------

to_acct: str = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
to_seed: str = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"

from_acct: str = 'rfdxDZK1cW6YBLcbx2BrtQUivjBXe5hqeB'
from_seed: str = 'ssYZKpUET4ZR5Q88DpYHzjnFsYgFj'

WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com"
w3 = WebsocketClient(WSS_RPC_URL)
with w3 as client:
    # response = client.request(ServerInfo())
    # print(json.dumps(response.result, sort_keys=True, indent=4))

    tx = Payment(
        account=from_acct,
        network_id=21338,
        fee='10',
        destination=to_acct,
        amount=xrp_to_drops(1000)
    )
    signed_tx = safe_sign_and_autofill_transaction(tx, Wallet(from_seed, 0), client)
    response = submit_transaction(signed_tx, client)
    print(json.dumps(response.result, sort_keys=True, indent=4))

