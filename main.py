from pathlib import Path
from multiversx_sdk import (Address, QueryRunnerAdapter, RelayedTransactionsFactory, SmartContractQueriesController, SmartContractTransactionsFactory, Transaction,
                            TransactionComputer, TransactionsFactoryConfig,
                            UserSigner, ProxyNetworkProvider) 
from multiversx_sdk.abi import Abi, EnumValue
from dotenv import load_dotenv
from flask import Flask, jsonify
import os
from card_props import CardProperties
from esdt_token_data import EsdtTokenData

provider = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
network_config = provider.get_network_config()

load_dotenv()
wallet = os.getenv("PEM_PATH")
abi_path = os.getenv("ABI_PATH")
abi = Abi.load(Path(abi_path))
sender_bech32 = "erd1lk8k33f3m4dcas4chj3a6hpf3w89rwdhr962sjglq87kn6uq3r5q0c5ay8"
contract_bech32 = "erd1qqqqqqqqqqqqqpgqtpxhlcckhltvs3pf3dj6ullt4nt6e7ahuvaqcetetf"


app = Flask(__name__)


@app.route("/nft/properties", methods=["GET"])
def getAssignedProperties():
    function_name = "getYourNftCardProperties"
    # factory = SmartContractTransactionsFactory(network_config, abi)
    query_runner = QueryRunnerAdapter(provider)
    query_controller = SmartContractQueriesController(query_runner, abi)
    query = query_controller.create_query(
        contract=contract_bech32,
        function=function_name,
        arguments=[],
    )
    res = query_controller.run_query(query)
    properties = query_controller.parse_query_response(res)
    card_properties = CardProperties.new_card_properties(properties)
    return jsonify(card_properties.to_dict())


@app.route("/nft/supply", methods=["GET"])
def getEquivalentCards():
    function_name = "nftSupply"
    query_runner = QueryRunnerAdapter(provider)
    query_controller = SmartContractQueriesController(query_runner, abi)

    query = query_controller.create_query(
        contract=contract_bech32,
        function=function_name,
        arguments=[],
    )

    res = query_controller.run_query(query)
    properties = query_controller.parse_query_response(res)
    token_data_list = [EsdtTokenData.new_esdt_token_data(p).to_dict() for p in properties[0]]
    return jsonify(token_data_list)

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
