
from typing import Dict, Any, List
from symtable import Symbol
import binascii
import json

from xrpl.models.transactions import Memo
from xrpl.models.transactions.metadata import TransactionMetadata
from xrpl.utils.txn_parser.utils.nodes import NormalizedNode, normalize_nodes

def symbol_to_hex(symbol):
    """symbol_to_hex."""
    if len(symbol) > 3:
        bytes_string = bytes(str(symbol).encode('utf-8'))
        return bytes_string.hex().upper().ljust(40, '0')
    return symbol


def hex_to_symbol(hex):
    """hex_to_symbol."""
    if len(hex) > 3:
        return bytes.fromhex(str(hex)).decode('utf-8')
    return hex

def create_memo(data: str, format: str, type: str):
    memo = Memo(
        memo_data=binascii.hexlify(data.encode('utf8')).decode('utf-8').upper(),
        memo_format=binascii.hexlify(format.encode('utf8')).decode('utf-8').upper(),
        memo_type=binascii.hexlify(type.encode('utf8')).decode('utf-8').upper(),
    )
    return memo

def read_memo(memo: Memo):
    _memo = {
        'memo_data': binascii.unhexlify(memo.memo_data).decode('utf-8'),
        'memo_format': binascii.unhexlify(memo.memo_format).decode('utf-8'),
        'memo_type': binascii.unhexlify(memo.memo_type).decode('utf-8'),
    }
    return _memo

# memos: [{'data': object, 'format': xls43-/message, 'type': xls-42/signature}]
def create_memos(memos: List[Dict[str, Any]]):
    hex_memos = []
    for memo in memos:
        hex_memos.append(create_memo(json.dumps(memo['data']), memo['format'], memo['type']))
    return hex_memos

# memos: [{'data': object, 'format': xls43-/message, 'type': xls-42/signature}]
def read_memos(memos: List[Memo]):
    hex_memos = []
    for memo in memos:
        hex_memos.append(read_memo(memo))
    return hex_memos

# types: List[str] = ['Escrow', 'PaymentChannel', 'URIToken']
def get_object_id(meta: Dict[str, Any], type: str) -> str:
    created_list = [node for node in meta['AffectedNodes'] if 'CreatedNode' in node and node['CreatedNode']['LedgerEntryType'] == type]
    if len(created_list) > 0:
        return created_list[0]['CreatedNode']['LedgerIndex']
    return None