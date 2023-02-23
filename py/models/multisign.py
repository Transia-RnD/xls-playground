
from typing import Dict, Any, List

from xrpl.clients import Client
from xrpl.wallet import Wallet

from xrpl.core.binarycodec import encode_for_multisigning
from xrpl.core.keypairs import sign
from xrpl.models import Signer, SignerEntry
from xrpl.models.transactions import SignerListSet
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)

# Signer List Set
# [START] Signer List Set
def signer_list_set(
    client: Client, 
    wallet: Wallet,
    quorum: int,
    signers: Dict[str, Any] = {},
):
    entries: List[SignerEntry] = [SignerEntry(account=k, signer_weight=v) for k, v in signers.items()]
    tx = SignerListSet(
        account=wallet.classic_address,
        signer_quorum=quorum,
        signer_entries=entries
    )
    
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response

# [END] Signer List Set

# Multi Sign
# [START] Multi Sign
def multi_sign(
    tx_json: Dict[str, Any],
    wallet: Wallet,
):
    """multi_sign."""
    signature: str =  sign(
        bytes.fromhex(
            encode_for_multisigning(
                tx_json,
                wallet.classic_address,
            )
        ),
        wallet.private_key,
    )
    return Signer(
        account=wallet.classic_address,
        txn_signature=signature,
        signing_pub_key=wallet.public_key,
    )

# [END] Multi Sign