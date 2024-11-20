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

* Run the `main.py` file with `python3 main.py`.


## Steps for exchanging a card/ NFT 
1. Fetch player assigned properties
2. Fetch the card with these properties from the smart contract
3. Create a new card with these properties:

        3.1 Create NFT collection

        3.2 Add ESDTRoleNFTCreate to the collection

        3.3 Create NFT inside collection (as we now have the role for that)

        3.4 Mint NFT
4. Exchange the minted NFT with the one fetched at step 2

        Step 4 is basically about calling the `exchangeNft` payable endpoint in the contract. This can be done by executing a simple NFT transfer transaction (ESDTNFTTransfer) and adding the contract address, endpoint and its required parameters to the transfer data, with proper encoding. 
        
        Since the contract will return our exchanged card, the receiver will be equal to the sender.

5. In the end, validate by executing step 1 again. The transaction should fail on the blochckain, but the API will return the following message:

    `"Congratulations! You already finished the homework!"`
