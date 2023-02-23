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
    SetHook,
    Hook,
)
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    submit_transaction,
    sign
)
from xrpl.utils import xrp_to_drops

from xrpl_helpers.sdk.hooks import calculate_hook_on

# -----------------------------------------------------------------------------

masterAccount: str = 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh'
masterSecret = 'snoPBrXtMeMyMHUVTgbuqAfg1SUTb'

def set_hook(
    client: Client,
    network_id: int,
    wallet: Wallet,
    binary: str,
    hook_on: str = None,
):
    hooks: List[Hook] = [
        Hook(
            create_code=binary,
            hook_on=hook_on,
            flags=1,
            hook_api_version=0,
            hook_namespace='4FF9961269BF7630D32E15276569C94470174A5DA79FA567C0F62251AA9A36B9'
        )
    ]
    # hooks: List[Hook] = [
    #     Hook(
    #         create_code='',
    #         flags=1,
    #     )
    # ]
    tx = SetHook(
        account=wallet.classic_address,
        network_id=network_id,
        hooks=hooks,
        fee='100000000'
    )
    hook_prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
        check_fee=False
    )
    # del hook_prepared['SigningPubKey']
    tx_blob = sign(hook_prepared, wallet)

    response = submit_transaction(tx_blob, client)
    if response.result['engine_result'] != 'tesSUCCESS':
        tx_result: str = response.result['engine_result']
        print(json.dumps(response.result, indent=4, sort_keys=True))
        raise ValueError(f'invalid response result: {tx_result}')
    
    return response.result

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
WSS_RPC_URL = "wss://hooks-testnet-v3.xrpl-labs.com"
w3 = WebsocketClient(WSS_RPC_URL)

with w3 as client:

    currency_code: str = 'USD'
    network_id: int = 21338

    # response = client.request(ServerInfo())
    # print(json.dumps(response.result, sort_keys=True, indent=4))
    
    cold_wallet = Wallet(masterSecret, 0)
    invoke_on: List[str] = ['ttACCOUNT_SET']

    # print(BASE_DIR)
    CONTRACT_PATH = os.path.join(BASE_DIR, 'starter.c.wasm')
    with open(CONTRACT_PATH, 'rb') as f:
        content = f.read()
        
    # binary = binascii.hexlify(content).decode('utf-8').upper()
    binary = '0061736D01000000011C0460057F7F7F7F7F017E60037F7F7E017E60027F7F017F60017F017E02230303656E76057472616365000003656E7606616363657074000103656E76025F670002030201030503010002062B077F0141B088040B7F004180080B7F0041A6080B7F004180080B7F0041B088040B7F0041000B7F0041010B07080104686F6F6B00030AC4800001C0800001017F230041106B220124002001200036020C41920841134180084112410010001A410022002000420010011A41012200200010021A200141106A240042000B0B2C01004180080B254163636570742E633A2043616C6C65642E00224163636570742E633A2043616C6C65642E22'
    hook_on_values: List[str] = [v for v in invoke_on]
    # print(hook_on_value_map)
    hook_on: str = calculate_hook_on(hook_on_values)
    response = set_hook(client, network_id, cold_wallet, binary, hook_on)
    print(response)

    