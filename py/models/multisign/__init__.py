from typing import Dict, Any
from xrpl.wallet import Wallet

from xrpl.core.binarycodec import encode_for_multisigning
from xrpl.core.keypairs import sign
from xrpl.models import Signer

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