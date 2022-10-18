import json #to save the output in a JSON file
import secrets
import solcx
from web3 import Web3
import magic
import os

import nft_storage
from nft_storage.api import nft_storage_api
from nft_storage.model.error_response import ErrorResponse
from nft_storage.model.upload_response import UploadResponse
from nft_storage.model.unauthorized_error_response import UnauthorizedErrorResponse
from nft_storage.model.forbidden_error_response import ForbiddenErrorResponse


from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv( os.path.join(BASE_DIR, 'creator_coin_new/.env') )





def generate_nonce():
  return secrets.token_urlsafe()


def deploy_contract():
    
  with open("./main_contracts/NFTExample.sol", "r") as file:
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

#   # For connecting to ganache
#   w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
#   chain_id = 1337

  w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/"))
  chain_id = 5
  address = "0x9d225E305758483AdD2A372B444acda6c0c21Fb1"
  private_key = "82fce336756c0134b9144e4cb360a299369372f8248722fda0b37b5573a08128" # leaving the private key like this is very insecure if you are working on real world project
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
  print(sign_transaction)
#   print("Deploying Contract!")
#   transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
#   # Wait for the transaction to be mined, and get the transaction receipt
#   print("Waiting for transaction to finish...")
#   transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
#   print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

  # contract_address = transaction_receipt.contractAddress


 
# deploy_contract()

# TODO: 
  # deploy NFT on Ropsten
  # add purchase functionality (safeMint)
  # enusre all transactions are logged on Ropsten 
  # import to CreatorCoin with etherscan api
  # **start from scratch and fix all final-bugs, etc. <-- record demo** 


def deploy_contract_main():
	with open("./deployed_contracts/NFTMain.sol", "r") as file:
		nft_main_file = file.read()

	compiled_sol = solcx.compile_standard(
			{
					"language": "Solidity",
					"sources": {"NFTMain.sol": {"content": nft_main_file}},
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

	with open("nft_main_compiled_code.json", "w") as file:
		json.dump(compiled_sol, file)


# deploy_contract_main()



def check_if_three_dim_model(f):
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'model/gltf-binary'
  ]

  content_type = magic.from_buffer(f.read(), mime=True) # verifies the uploaded file
  print('ct:', content_type)

    # if 'nft_image_upload' in request.FILES:
    #   uploaded_file = request.FILES['nft_image_upload']
    #   upload_file_mb_size = uploaded_file.size / 1024 / 1024
      
    #   if content_type in accepted_content_types and upload_file_mb_size <= max_file_size and form_validation_error is False:
    #     nft_name = request.POST['token_name']
    #     nft_symbol = request.POST['token_symbol']
    #     nft_price = request.POST['token_price_field']
    #     nft_total_supply = request.POST['nft_total_supply']


# check_if_three_dim_model()



def store_file_in_ipfs(obj):
  configuration = nft_storage.Configuration(
    host = "https://api.nft.storage"
  )

  configuration = nft_storage.Configuration(
    access_token = os.getenv("nft_storage_accesss_token")
  )

  with nft_storage.ApiClient(configuration) as api_client:
    api_instance = nft_storage_api.NFTStorageAPI(api_client)

    obj_fp = BASE_DIR + obj.nft_media_file.url
    contents = open(obj_fp, 'rb')

    # body = open('/Users/rahul/Desktop/Screen Shot 2022-10-16 at 11.47.51 AM.png', 'rb') # file_type | 

    # example passing only required values which don't have defaults set
    try:
      # Store a file
      api_response = api_instance.store(body=contents, _check_return_type=False)
      print('api-res', api_response)
      if api_response['ok'] is True:
        uploaded_data = api_response['value']
        ipfs_cid = uploaded_data['cid']
        return True, ipfs_cid
      else:
        return False, None

    except nft_storage.ApiException as e:
      print("Exception when calling NFTStorageAPI->store: %s\n" % e)
      return False, None


# import os

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "creator_coin_new.settings")

# from models import UserNft

# obj = UserNft.objects.all()[1]
# store_file_in_ipfs(obj)




