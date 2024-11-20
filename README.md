# Trading-Card-Blockchain

##  Short description
This is a Python client for a trading card game on the MultiversX blockchain.

* The smart contract the client is interacting with can be found [here](https://github.com/cs-pub-ro/blockchain-protocols-and-distributed-applications/tree/main/assignments/tema-1).
* For interacting with the contract, the [MX Python SDK](https://github.com/multiversx/mx-sdk-py) was used.
* The client consists of a few Flask endpoints that are calling the smart contract and other blockchain specific functions, like creating and mining NFTs.

There are some cards, each containing properties like class, rarity and power. Each player has to get their assigned properties,for example:

```
{
    "class": "Paladin", 
    "power": "Low",
    "rarity": "Legendary"
}
```
 The user has to create a card with these properties and exchange the created card with an existing one with the same properties.

## Running locally

Make sure you have Pyhton 3 installed on your system.

* Create and activate a virtual environment to install the dependencies into:
```
    python3 -m venv .venv
    source .venv/bin/activate (works on Unix)
```
* Install all necessary dependecies using the `requirements.txt` file: 
```   
    pip install -r requirements.txt
```

* Create an `.env` file and place the path to your wallet's PEM file. This makes it possible to sign transactions securely, without exposing the private key.

* Build the smart contract and generate the ABI files. Save the ABI file that contains the contract's endpoints' input and output structure.

    Place the path to this file in the `.env` file as well. The ABI is necessary for using the encoders and decoders provided by the MX SDK.


* Start the server with `python3 main.py`.


## Steps for exchanging a card/ NFT 
1. Fetch player assigned properties
2. Fetch the card with these properties from the smart contract
3. Create a new card with these properties:

        3.1 Create NFT collection

        3.2 Add ESDTRoleNFTCreate to the collection

        3.3 Create NFT inside collection (as we now have the role for that)

        3.4 Mint NFT

4. Exchange the minted NFT with the one fetched at step 2

        Step 4 is basically about calling the `exchangeNft` payable endpoint in the contract.
        This can be done by executing a simple NFT transfer transaction (ESDTNFTTransfer) and
        adding the contract address, endpoint and its required parameters to the transfer data,
        with proper encoding. 
        
        Since the contract will return our exchanged card, the receiver will be equal to the sender.

5. In the end, validate by executing step 1 again. The transaction should fail on the blochckain, but the API will return the following message:

    `"Congratulations! You already finished the homework!"`


## Endpoints

`GET /nft/properties`
        
        Executes a transaction and signs it with the provided PEM. 
        
        Fetches the card properties assigned to the user associated with the provided PEM.

        If a card has already been exchanged for this user via the smart contract, a message will be returned.

Response:
```
{
    "class": "Warlock",
    "power": "Low",
    "rarity": "Common"
}
```

`POST /nft/supply`

        Takes 3 parameters:
            - class : stirng, class property of the card
            - rarity : string, rarity property of the card
            - power : string, power property of the card

        Queries the contract for the available cards, and returns the card from the list that has exactly the requested properties.

        Returns the card with all its data, along with its nonce. The nonce is the position in the queried list + 1, since the list has 0 based indexing, but nonces start at 1.

Response:

```
{
    "nonce": 61,
    "tradable_card": {
        "amount": 1,
        "attributes": {
            "class": "Warlock",
            "power": "Low",
            "rarity": "Common"
        },
        "creator": "erd1mqa9wttlzwwdvwgk9dzsfdn79lv5raw0tfe9ynvn0dg92hpruvaqhhd2gx",
        "frozen": false,
        "hash": "69c492e24afa52c556de5ea70e1b5d7da3f0bc7a5a7fd1d413444c1a42a7e9b3",
        "name": "BPDA-TRADING-CARD",
        "royalties": 10000,
        "token_type": "NonFungible",
        "uris": []
    }
}
```

`POST /nft/collection/create`
        
        Takes 2 parameters:
            - collection_name : string, the name of the collection
            - ticker : string, the ticker of the collection

        Creates an empty NFT collection.
        
Returns the new collection's id:

```
{
    "nft_collection": "DAWG-a5b788"
}
```

`POST /nft/collection/role`

        Takes 2 parameters:
            - nft_collection : string, the collection's ID
            - role : string, the name of the role to add to the collection 

        Adds the requested role to the given collection ID.

Returns the status of the operation:

```
{
    "transaction": "ok"
}
```

`POST /nft/create`

        Takes 5 parameters:
            - nft_collection : string, NFT collection ID
            - NFT name : string, the NFT's name
            - class : string
            - rarity : string
            - power : string
        Creates an NFT with the given name, in the provided NFT collection.

Returns the NFT's nonce if successful:

```
{
    "nft_nonce": 1
}
```

`POST /nft/exchange`

        Takes 3 parameters: 
            - collection : string, the NFT collection ID
            - nft_nonce : number, the nonce of the NFT sent as payment
            - supply_nonce : number, the nonce of the NTF we are trading with


