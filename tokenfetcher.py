import requests
import json
import base64
import base58
import struct

from optparse import OptionParser

payload = {
    "method": "getProgramAccounts",
    "jsonrpc": "2.0",
    "params": [
        "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
        {
            "encoding": "base64",
            "filters": [
                {
                    "memcmp": {
                        "offset": 326,
                        "bytes": "",
                    }
                }
            ],
        },
    ],
    "id": "f0e26f8e-7c9b-40f6-a712-af65978b67da",
}

def unpack_metadata_account(data):
    assert(data[0] == 4)
    i = 1
    source_account = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
    i += 32
    mint_account = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
    i += 32
    name_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4
    name = struct.unpack('<' + "B"*name_len, data[i:i+name_len])
    i += name_len
    symbol_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4 
    symbol = struct.unpack('<' + "B"*symbol_len, data[i:i+symbol_len])
    i += symbol_len
    uri_len = struct.unpack('<I', data[i:i+4])[0]
    i += 4 
    uri = struct.unpack('<' + "B"*uri_len, data[i:i+uri_len])
    i += uri_len
    fee = struct.unpack('<h', data[i:i+2])[0]
    i += 2
    has_creator = data[i] 
    i += 1
    creators = []
    verified = []
    share = []
    if has_creator:
        creator_len = struct.unpack('<I', data[i:i+4])[0]
        i += 4
        for _ in range(creator_len):
            creator = base58.b58encode(bytes(struct.unpack('<' + "B"*32, data[i:i+32])))
            creators.append(creator)
            i += 32
            verified.append(data[i])
            i += 1
            share.append(data[i])
            i += 1
    primary_sale_happened = bool(data[i])
    i += 1
    is_mutable = bool(data[i])
    metadata = {
        "update_authority": source_account,
        "mint": mint_account,
        "data": {
            "name": bytes(name).decode("utf-8").strip("\x00"),
            "symbol": bytes(symbol).decode("utf-8").strip("\x00"),
            "uri": bytes(uri).decode("utf-8").strip("\x00"),
            "seller_fee_basis_points": fee,
            "creators": creators,
            "verified": verified,
            "share": share,
        },
        "primary_sale_happened": primary_sale_happened,
        "is_mutable": is_mutable,
    }
    return metadata

if __name__ == "__main__":

    parser = OptionParser()
    creator_address = "DVemJ8n9ZiSmSf8a18VYgpBgTUoHEA8x6ZZBsTL2bxk9"
    parser.add_option("-c", "--c", dest="creator_address",
                  help="candy machine creator address")

    (options, args) = parser.parse_args()
    if options.creator_address:
        creator_address = options.creator_address
    payload["params"][1]["filters"][0]["memcmp"]["bytes"] = creator_address
    resp = json.loads(requests.post("https://api.mainnet-beta.solana.com/", json = payload).text)

    for r in resp["result"]:
        print(unpack_metadata_account(base64.b64decode(r["account"]["data"][0])))

