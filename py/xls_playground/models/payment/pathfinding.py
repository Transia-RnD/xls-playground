
from xrpl.clients import Client
from xrpl.wallet import Wallet
from xrpl.models import PathFind, PathFindSubcommand
from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from models.utils import symbol_to_hex

# Pathfinding
# [START] Pathfinding
def pathfinding(
    client: Client,
    account: str,
    destination: str,
    issuer: str,
    currency: str,
    amount: float,
):
    """pathfinding."""
    try:
        curr_value = IssuedCurrencyAmount(
            currency=symbol_to_hex(currency),
            issuer=issuer,
            value=str(round(amount, 2))
        )
        return client.request(
            PathFind(
              source_account=account,
              subcommand=PathFindSubcommand.CREATE,
              destination_account=destination,
              destination_amount=curr_value,
            ),
        )
    except Exception as e:
        print(e)
        raise e
# [END] Pathfinding