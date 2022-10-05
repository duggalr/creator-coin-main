import secrets
import solcx
from web3 import Web3, HTTPProvider







def generate_nonce():
  return secrets.token_urlsafe()




# TODO:
  # The contract address will be saved with user that created/deployed it
    # "to-address" will be from the metamask-call
def mint_nft():
  blockchain_address = 'http://127.0.0.1:8545'
  web3 = Web3(HTTPProvider(blockchain_address))

  web3.eth.defaultAccount = web3.eth.accounts[0]

  # compiled_contract = solcx.compile_files(
  #   [
  #     "/Users/rahul/Documents/main/personal_learning_projects/fundamentals/nft_tutorial_two/contracts/ERC721Main.sol",
  #     "/Users/rahul/Documents/main/personal_learning_projects/fundamentals/node_modules/@openzeppelin/contracts/token/ERC721/ERC721.sol", 
  #     "/Users/rahul/Documents/main/personal_learning_projects/fundamentals/node_modules/@openzeppelin/contracts/access/Ownable.sol",
  #     "/Users/rahul/Documents/main/personal_learning_projects/fundamentals/node_modules/@openzeppelin/contracts/utils/Counters.sol"
  #   ],
  #   output_values=["abi", "bin"],
  #   solc_version="0.8.4"
  # )

  contract_id, contract_interface = compiled_contract.popitem()

  contract_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"
  cs_contract_address = web3.toChecksumAddress(contract_address)
  contract_abi = contract_interface['abi']
  NFTContract = web3.eth.contract(abi=contract_abi, address=cs_contract_address)

  print( "total-nft-supply:", NFTContract.functions.safeMint( web3.eth.accounts[3] ) )
  # print( "total-nft-supply:", NFTContract.functions.supportsInterface() )

  

 
# mint_nft()










