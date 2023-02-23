

from xrpl.clients import Client
from xrpl.wallet import Wallet
from xrpl.models.requests import (
    AccountInfo,
    AccountNFTs,
    AccountOffers,
    AccountLines,
    AccountObjects,
    AccountObjectType
)
from xrpl.models.transactions import AccountSet, AccountSetFlag, TicketCreate, SetRegularKey
from xrpl.utils import str_to_hex
from models.nftoken.burn import nftoken_burn
from xrpl.transaction import (
    send_reliable_submission,
    safe_sign_and_autofill_transaction,
)

def account_set(
    client: Client, 
    wallet: Wallet,
    domain: str = None,
    email: str = None,
    transfer_rate: int = 0,
    tick_size: int = 0
):
    tx = AccountSet(
        account=wallet.classic_address,
        domain=bytes.hex(domain.encode("ASCII")),
        # set_flag=[AccountSetFlag.ASF_DEFAULT_RIPPLE, AccountSetFlag.ASF_REQUIRE_AUTH],
        set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
    )
    
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response

def disable_master(
    client: Client, 
    wallet: Wallet
):
    tx = AccountSet(
        account=wallet.classic_address,
        set_flag=AccountSetFlag.ASF_DISABLE_MASTER,
    )
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response


# Ticket Create
# [START] Ticket Create
def ticket_create(
    client: Client, 
    wallet: Wallet,
    count: int,
):
    tx = TicketCreate(
        account=wallet.classic_address,
        ticket_count=count,
    )
    
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response
# [END] Ticket Create


# Set Regular Key
# [START] Set Regular Key
def set_regular_key(
    client: Client, 
    wallet: Wallet,
    regular_key: str,
):
    tx = SetRegularKey(
        account=wallet.classic_address,
        regular_key=regular_key,
    )
    
    prepared = safe_sign_and_autofill_transaction(
        transaction=tx,
        wallet=wallet,
        client=client,
    )
    response = send_reliable_submission(prepared, client)
    return response
# [END] Set Regular Key

def get_native_balance(client, account: str):
    """get_balance."""
    response = client.request(AccountInfo(account=account))
    if 'error' in response.result:
        return []
    return int(response.result['account_data']['Balance'])

# Get Balances
# [START] Get Balances
def get_balances(client, account):
    """get_balance."""
    response = client.request(AccountLines(account=account))
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    if 'lines' not in response.result:
        raise ValueError('Unknown Error')
    return response.result['lines']
# [END] Get Balances

# Get IC Balance
# [START] Get Balance
def get_ic_balance(client: Client, account: str, issuer: str, currency: str):
    """get_ic_balance."""
    holders = []
    marker = None
    has_marker = True
    page = 1
    # print('SNAPSHOT {} FOR {}'.format(currency, issuer))
    while has_marker:
        # print('PAGINATION: PAGE: {}'.format(page))
        acct_lines = AccountLines(
            account=account,
            ledger_index="validated",
            limit=200,
            marker=marker,
        )
        response = client.request(acct_lines)

        # if 'status' in response.result and response.result['status'] == 'error':  # noqa
        #     raise ValueError(response.result['error_message'])

        if 'lines' in response.result:
            for line in response.result['lines']:
                if line['account'] == issuer and line['currency'] == currency:
                    return {
                        'address': line['account'],
                        'balance': int(abs(float(line['balance']))),
                    }

        if 'marker' in response.result:
            marker = response.result['marker']
            page += 1
            continue

        has_marker = False

    # print('FINISHED PAGINATION')
    return holders
# [END] Get Balance

# Offers
# [START] Offers
def get_offers(w3, account):
    """get_offers."""
    response = w3.request(AccountOffers(account=account))
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    if 'account_nfts' not in response.result:
        raise ValueError('Unknown Error')
    return response.result['offers']
# [END] Offers

# NFTs
# [START] NFTs
def get_nfts(w3, account):
    """get_nfts."""
    response = w3.request(
        AccountNFTs(
            account=account,
        ),
    )
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    if 'account_nfts' not in response.result:
        raise ValueError('Unknown Error')
    return response.result['account_nfts']
# [END] NFTs


# Escrows
# [START] Escrows
def get_escrows(w3, account):
    """get_escrows."""
    response = w3.request(
        AccountObjects(
            account=account,
            type=AccountObjectType.ESCROW
        ),
    )
    if 'error' in response.result:
        print(response.result['error_message'])
        return []
    if 'account_objects' not in response.result:
        raise ValueError('Unknown Error')
    return response.result['account_objects']
# [END] Escrows


def nuke_account(client: Client, account: str, wallet: Wallet, count: int):
    print(account)
    account_nfts = get_nfts(client, account)
    if len(account_nfts) == 0:
        print('NO NFTS...')
        return
    if count and count != 0:
        for i in range(count):
            print(i)
            print(account_nfts)
            nft = account_nfts[i]
            nftoken_burn(client, wallet, nft['NFTokenID'])
            return
    for i in range(len(account_nfts)):
        nft = account_nfts[i]
        nftoken_burn(client, wallet, nft['NFTokenID'])
        return