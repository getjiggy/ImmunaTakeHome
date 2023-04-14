from web3 import providers, Web3
from web3.logs import DISCARD
import os
import abis
import json
import pprint

printer = pprint.PrettyPrinter()



# {asset_holder: {token_address: amount gained/lost}}
AssetDeltas = {str: {str: int}}


# this function will detect balance changes in ERC20 tokens and return an AssetDelta Obj summarizing
# all changes in a given transaction
def detect_gainers_and_losers(txn_hash: str) -> AssetDeltas:
    with open("abis/ERC20.json") as erc20:
        erc20_abi = json.load(erc20)
    url = os.getenv("INFURA_URL")
    w3 = Web3(providers.HTTPProvider(endpoint_uri=url))
    asset_deltas: AssetDeltas = {}
    #grab transaction receipt
    txn_receipt = w3.eth.get_transaction_receipt(txn_hash)
    # create erc20 interface to parse events
    erc20_interface = w3.eth.contract(abi=erc20_abi)

    #filter transfer events
    transfer_events = erc20_interface.events.Transfer().process_receipt(txn_receipt, errors=DISCARD)

    #find deltas for each asset holder

    for i in transfer_events:
        sender = i.args.src
        recipient = i.args.dst
        asset = i.address
        if asset_deltas.get(sender) == None:
            asset_deltas[sender] = {asset: -i.args.wad}

        elif asset_deltas[sender].get(asset) == None:
            asset_deltas[sender][asset] = -i.args.wad
        else:
            asset_deltas[sender][asset] -= i.args.wad

        if asset_deltas.get(recipient) == None:
            asset_deltas[recipient] = {asset: i.args.wad}
        elif asset_deltas[recipient].get(asset) == None:
            asset_deltas[recipient][asset] = i.args.wad
        else:
            asset_deltas[recipient][asset] += i.args.wad

    return asset_deltas

printer.pprint(detect_gainers_and_losers('0x6200bf5c43c214caa1177c3676293442059b4f39eb5dbae6cfd4e6ad16305668'))
