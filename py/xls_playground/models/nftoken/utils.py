#!/usr/bin/env python
# coding: utf-8

import json
from typing import Dict, Any


def get_token_id_from_meta(meta: Dict[str, Any]):
    created_list = [node['CreatedNode'] for node in meta['AffectedNodes'] if 'CreatedNode' in node and node['CreatedNode']['LedgerEntryType'] == 'NFTokenPage']
    modified_list = [node['ModifiedNode'] for node in meta['AffectedNodes'] if 'ModifiedNode' in node and node['ModifiedNode']['LedgerEntryType'] == 'NFTokenPage']
    if len(created_list) > 0:
        return created_list[0]['NewFields']['NFTokens'][-1]['NFToken']['NFTokenID']
    return modified_list[-1]['FinalFields']['NFTokens'][-1]['NFToken']['NFTokenID']

def get_buy_index_hash(meta: Dict[str, Any]):
    created_list = [node for node in meta['AffectedNodes'] if 'CreatedNode' in node and node['CreatedNode']['LedgerEntryType'] == 'NFTokenOffer']
    if len(created_list) > 0:
        return created_list[0]['CreatedNode']['LedgerIndex']
    return None