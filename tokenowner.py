import requests
import sys
import json

from solana.rpc.api import Client
from spl.token.client import Token
from solana.publickey import PublicKey

MAINNET_RPC = "https://api.mainnet-beta.solana.com/"

payload = {
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getTokenLargestAccounts",
  "params": [ ]
}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("provide mint address")
        sys.exit(0)
    payload["params"] = [sys.argv[1]]
    resp = json.loads(requests.post(MAINNET_RPC, json = payload).text)
    owner_raw = list(filter(lambda x: x["amount"] == "1", resp["result"]["value"]))[0]
    print("token account address:  %s"%(owner_raw["address"]))


    solana_client = Client(MAINNET_RPC)
    spl_client = Token(solana_client, PublicKey(sys.argv[1]), PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),None)
    ainfo = spl_client.get_account_info(owner_raw["address"])
    print("actual owner address:  %s"%ainfo.owner)
