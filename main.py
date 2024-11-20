from pathlib import Path
from multiversx_sdk import (AccountNonceHolder, Address, QueryRunnerAdapter, SmartContractQueriesController, Transaction,
                            TransactionComputer, UserSigner, ProxyNetworkProvider) 
from multiversx_sdk.abi import Abi

from dotenv import load_dotenv
from flask import Flask, jsonify, request
import os
from card_props import CardProperties, Power, Rarity, Class
from esdt_token_data import EsdtTokenData, TradableCard
import time
import base64

provider = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
network_config = provider.get_network_config()

load_dotenv()
wallet = os.getenv("PEM_PATH")
signer = UserSigner.from_pem_file(Path(wallet))

abi_path = os.getenv("ABI_PATH")
abi = Abi.load(Path(abi_path))

sender_bech32 = "erd1lk8k33f3m4dcas4chj3a6hpf3w89rwdhr962sjglq87kn6uq3r5q0c5ay8"
sender_account = Address.from_bech32(sender_bech32)

contract_bech32 = "erd1qqqqqqqqqqqqqpgqrqz7r8yl5dav2z0fgnn302l2w7xynygruvaq76m26j"
contract_account = Address.from_bech32(contract_bech32)

metachain_bech32 = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls8a5w6u"

transaction_computer = TransactionComputer()

app = Flask(__name__)


@app.route("/nft/properties", methods=["GET"])
def get_assigned_properties():
    function_name = b"getYourNftCardProperties"

    transaction = Transaction(
        receiver=contract_bech32,
        sender=sender_bech32,
        value=0,
        gas_limit=10000000,
        chain_id=network_config.chain_id,
        data=function_name,
    )

    hash = sign_transaction(transaction)

    time.sleep(30)

    transaction_on_network = provider.get_transaction(hash)
    
    if not transaction_on_network.contract_results.items:
        res_data = transaction_on_network.raw_response['logs']['events'][0]['topics'][1]
        return jsonify(base64.b64decode(res_data).decode())
    else:
        res_data = transaction_on_network.contract_results.items[0].data

    hex_card_props = res_data.split('@')[2]
    properties = [int(hex_card_props[i:i+2], 16) for i in range(0, len(hex_card_props), 2)]
    card_properties = CardProperties.new_card_properties(properties)
    return jsonify(card_properties.to_dict())


@app.route("/nft/supply", methods=["POST"])
def get_equivalent_card():
    function_name = "nftSupply"
    try:
        class_type = request.json.get('class')
        rarity = request.json.get('rarity')
        power = request.json.get("power")
    except Exception as e:
        raise e
    
    query_runner = QueryRunnerAdapter(provider)
    query_controller = SmartContractQueriesController(query_runner, abi)

    query = query_controller.create_query(
        contract=contract_bech32,
        function=function_name,
        arguments=[],
    )

    res = query_controller.run_query(query)
    properties = query_controller.parse_query_response(res)
    cards_data_list = [EsdtTokenData.new_esdt_token_data(p).to_dict() for p in properties[0]]
    for nonce, card in enumerate(cards_data_list):
        card_attr = card['attributes']
        if card_attr['class'] == class_type and card_attr['rarity'] == rarity and card_attr['power'] == power:
            # nonce uses 1 based indexing
            return jsonify(TradableCard(card, nonce+1).to_dict())
    return jsonify("Not found")


@app.route("/nft/collection/create", methods=["POST"]) 
def create_NFT_collection():
    function_name = "issueNonFungible"
    try:
        collection_name = request.json.get('collection_name')
        ticker = request.json.get('ticker')
    except Exception as e:
        raise e
    
    hex_col_name = collection_name.encode("UTF-8").hex()
    hex_ticker = ticker.encode("UTF-8").hex()
    data = f"{function_name}@{hex_col_name}@{hex_ticker}"

    transaction = Transaction(
        sender=sender_bech32,
        receiver=metachain_bech32,
        value=50000000000000000,
        gas_limit=60000000,
        data=data.encode("UTF-8"),
        chain_id=network_config.chain_id,
    )

    transaction_hash = sign_transaction(transaction)

    time.sleep(20)

    transaction_on_network = provider.get_transaction(transaction_hash)

    res = "NFT collection could not be created"
    if transaction_on_network.contract_results.items:
        hex_res = transaction_on_network.contract_results.items[0].data.split("@")[1]
        res = {"nft_collection": bytearray.fromhex(hex_res).decode()}
    return jsonify(res)


@app.route("/nft/collection/role", methods=["POST"])
def add_NFT_roles():
    function_name = "setSpecialRole"
    try:
        nft_collection = request.json.get('nft_collection')
        role = request.json.get('role')
    except Exception as e:
        raise e

    hex_collection = nft_collection.encode("UTF-8").hex()
    hex_role = role.encode("UTF-8").hex()
    data = f"{function_name}@{hex_collection}@{sender_account.hex()}@{hex_role}"

    transaction = Transaction(
        sender=sender_bech32,
        receiver=metachain_bech32,
        value=0,
        gas_limit=60000000,
        data=data.encode("UTF-8"),
        chain_id=network_config.chain_id,
    )

    transaction_hash = sign_transaction(transaction)

    time.sleep(30)

    transaction_on_network = provider.get_transaction(transaction_hash)

    res = "Roles could not be added"
    if transaction_on_network.contract_results.items:
        hex_res = transaction_on_network.contract_results.items[1].data.split("@")[1]
        res = {"transaction": bytearray.fromhex(hex_res).decode()}
    return jsonify(res)


@app.route("/nft/create", methods=["POST"])
def create_NFT_with_properties():
    function_name = "ESDTNFTCreate"
    try:
        nft_collection = request.json.get('nft_collection')
        name = request.json.get('name')
        class_type = Class.from_string(request.json.get('class'))
        rarity = Rarity.from_string(request.json.get('rarity'))
        power = Power.from_string(request.json.get("power"))
    except Exception as e:
        raise e
    

    hex_collection = nft_collection.encode("UTF-8").hex()
    hex_name = name.encode("UTF-8").hex()

    # quantity = 1, but it's formatted as 01
    quantity = f"{1:02x}"
    royalties = 2000
    hash_field = ""
    attributes = f"{class_type:02x}{rarity:02x}{power:02x}"
    img = "https://i.natgeofe.com/n/4f5aaece-3300-41a4-b2a8-ed2708a0a27c/domestic-dog_thumb_square.jpg"

    data = (
        f"{function_name}@{hex_collection}"
        f"@{quantity}"
        f"@{hex_name}"
        f"@{royalties}"
        f"@{hash_field}"
        f"@{attributes}"
        f"@{img.encode('utf-8').hex()}"
    )
    transaction = Transaction(
        sender=sender_bech32,
        receiver=sender_bech32,
        value=0,
        gas_limit=3000000 + len(data) * 1500,
        data=data.encode("UTF-8"),
        chain_id=network_config.chain_id
    )

    transaction_hash = sign_transaction(transaction)

    time.sleep(15)

    transaction_on_network = provider.get_transaction(transaction_hash)

    res = "NFT could not be created"
    if transaction_on_network.contract_results.items:
        hex_res = transaction_on_network.contract_results.items[0].data.split("@")[2]
        res = {"nft_nonce": int(hex_res, 16)}
    return jsonify(res)


@app.route("/nft/exchange", methods=["POST"])
def exchange_cards():
    hex_contract_endpoint = "exchangeNft".encode("utf-8").hex()
    function_name = "ESDTNFTTransfer"
    data = f"{function_name}"
    try:
        supply_nonce = int(request.json.get("supply_nonce"))
        collection = request.json.get("collection")
        nft_nonce = request.json.get("nft_nonce")
    except Exception as e:
        raise e
    
    hex_collection = collection.encode("UTF-8").hex()
    token_amount = 1
    token_data = f"{hex_collection}@{nft_nonce:02x}@{token_amount:02x}"
    contract_data = f"{contract_account.hex()}@{hex_contract_endpoint}@{supply_nonce:02x}"

    data = f"{function_name}@{token_data}@{contract_data}"

    transaction = Transaction(
        sender=sender_bech32,
        receiver=sender_bech32,
        value=0,
        gas_limit=50000000 + len(data) * 1500,
        data=data.encode("UTF-8"),
        chain_id=network_config.chain_id
    )
    transaction_hash = sign_transaction(transaction)

    time.sleep(30)

    transaction_on_network = provider.get_transaction(transaction_hash)
    hex_res = transaction_on_network.status.status

    return jsonify({"status": hex_res})



# Signs transaction and increments the sender's nonce
def sign_transaction(transaction: Transaction):

    sender_nonce = provider.get_account(sender_account).nonce
    nonce_holder = AccountNonceHolder(sender_nonce)

    transaction.nonce = nonce_holder.get_nonce_then_increment()
    transaction.signature = signer.sign(transaction_computer.compute_bytes_for_signing(transaction))
    transaction_hash = provider.send_transaction(transaction)

    return transaction_hash


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
