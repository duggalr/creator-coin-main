import json #to save the output in a JSON file
import solcx
from web3 import Web3



def deploy_contract():
  with open("NFTExample.sol", "r") as file:
    nft_example_file = file.read()


  compiled_sol = solcx.compile_standard(
      {
          "language": "Solidity",
          "sources": {"NFTExample.sol": {"content": nft_example_file}},
          "settings": {
              "outputSelection": {
                  "*": {
                      "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                  }
              }
          },
      },
      allow_paths="/Users/rahul/Documents/main/personal_learning_projects/creator_coin_new/creator_coin",
      solc_version="0.8.4",
  )

  # print(compiled_sol)


  with open("nft_example_compiled_code.json", "w") as file:
      json.dump(compiled_sol, file)

  # get bytecode
  bytecode = compiled_sol["contracts"]["NFTExample.sol"]["NFTExample"]["evm"]["bytecode"]["object"]
  # get abi
  abi = json.loads(compiled_sol["contracts"]["NFTExample.sol"]["NFTExample"]["metadata"])["output"]["abi"]

  # For connecting to ganache
  w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
  chain_id = 1337
  address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
  private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d" # leaving the private key like this is very insecure if you are working on real world project
  # Create the contract in Python
  NFTExample = w3.eth.contract(abi=abi, bytecode=bytecode)
  # Get the number of latest transaction
  nonce = w3.eth.getTransactionCount(address)

  # build transaction
  tok_name = 'RahulPersonal'
  tok_symbol = 'RP'
  total_supply = 1000
  max_num_per_sale = 25
  user_token_price = 1000  # TODO: look at eth-brownie for the token-price
  user_token_uri = 'https://github.com/OpenZeppelin/openzeppelin-contracts/tree/v4.7.3'

  transaction = NFTExample.constructor(tok_name, tok_symbol, total_supply, max_num_per_sale, user_token_price, user_token_uri).buildTransaction(
      {
          "chainId": chain_id,
          "gasPrice": w3.eth.gas_price,
          "from": address,
          "nonce": nonce,
      }
  )

  # Sign the transaction
  sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
  print("Deploying Contract!")
  transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
  # Wait for the transaction to be mined, and get the transaction receipt
  print("Waiting for transaction to finish...")
  transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
  print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

  # contract_address = transaction_receipt.contractAddress


 

# TODO: 
  # deploy NFT on Ropsten
  # add purchase functionality (safeMint)
  # enusre all transactions are logged on Ropsten 
  # import to CreatorCoin with etherscan api
  # **start from scratch and fix all final-bugs, etc. <-- record demo** 

 
