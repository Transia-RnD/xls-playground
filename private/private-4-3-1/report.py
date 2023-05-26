#!/usr/bin/env python
# coding: utf-8
import json
from typing import List

from xrpl import CryptoAlgorithm
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import ServerInfo

VL_LIST: List[str] = [
    "http://127.0.0.1:5005",
    "http://127.0.0.1:5006",
    "http://127.0.0.1:5007",
]
for i in range(len(VL_LIST)):
    vl_rpc_url = VL_LIST[i]
    vl_client = JsonRpcClient(vl_rpc_url)
    response = vl_client.request(ServerInfo())
    vl_state: int = response.result['info']['server_state']
    vl_complete_ledgers: int = response.result['info']['complete_ledgers']
    vl_peer_disconnects: int = response.result['info']['peer_disconnects']
    vl_peers: int = response.result['info']['peers']
    vl_uptime: int = response.result['info']['uptime']
    vl_quorum: int = response.result['info']['validation_quorum']
    vl_validated: bool = False
    vl_seq: int = 0
    if 'validated_ledger' in response.result['info']:
        vl_validated = True
        vl_seq = response.result['info']['validated_ledger']['seq']

    print('--------------------VALIDATORS------------------------------')
    print(f'NODE {i + 1}: STATE - {vl_state}')
    print(f'NODE {i + 1}: COMPLETED LEDGERS - {vl_complete_ledgers}')
    print(f'NODE {i + 1}: PEER DISCONECTS - {vl_peer_disconnects}')
    print(f'NODE {i + 1}: PEERS - {vl_peers}')
    print(f'NODE {i + 1}: UPTIME - {vl_uptime}')
    print(f'NODE {i + 1}: QUORUM - {vl_quorum}')
    print(f'NODE {i + 1}: VALIDATED - {vl_validated}')
    print(f'NODE {i + 1}: VL SEQUENCE - {vl_seq}')

PEER_LIST: List[str] = [
    "http://127.0.0.1:5008",
]
for i in range(len(PEER_LIST)):
    peer_rpc_url = PEER_LIST[i]
    peer_client = JsonRpcClient(peer_rpc_url)
    try:
        response = peer_client.request(ServerInfo())
        # print(json.dumps(response.result, sort_keys=True, indent=4))
        peer_state: int = response.result['info']['server_state']
        peer_complete_ledgers: int = response.result['info']['complete_ledgers']
        peer_peer_disconnects: int = response.result['info']['peer_disconnects']
        peer_peers: int = response.result['info']['peers']
        peer_uptime: int = response.result['info']['uptime']
        peer_quorum: int = response.result['info']['validation_quorum']
        peer_validated: bool = False
        peer_seq: int = 0
        if 'validated_ledger' in response.result['info']:
            peer_validated = True
            peer_seq = response.result['info']['validated_ledger']['seq']

        print('--------------------PEERS------------------------------')
        print(f'NODE {i + 1}: STATE - {peer_state}')
        print(f'NODE {i + 1}: COMPLETED LEDGERS - {peer_complete_ledgers}')
        print(f'NODE {i + 1}: PEER DISCONECTS - {peer_peer_disconnects}')
        print(f'NODE {i + 1}: PEERS - {peer_peers}')
        print(f'NODE {i + 1}: UPTIME - {peer_uptime}')
        print(f'NODE {i + 1}: QUORUM - {peer_quorum}')
        print(f'NODE {i + 1}: VALIDATED - {peer_validated}')
        print(f'NODE {i + 1}: VL SEQUENCE - {peer_seq}')
    except Exception as e:
        print(e)
