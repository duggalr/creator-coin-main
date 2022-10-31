import os
import json
import secrets
import requests
from web3 import Web3

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


def store_file_in_ipfs(obj):
  """
  Store user uploaded NFT Metadata in nft.storage
  """

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



def get_transaction_status(tx_hash):
  
  transaction_url = f'https://api-goerli.etherscan.io/api?module=account&action=balance&address={tx_hash}&tag=latest&apikey={os.getenv("etherscan_api_key")}'
  res = requests.get(transaction_url)
  print(res.status_code)
  if res.status_code == 200:
    print(res.json())



# get_transaction_status('0xf9f72f5289c622e9e87308c9258ab98df1575bcc9ebd798f53ab6762748fe699')


# https://api-goerli.etherscan.io/api?module=stats&action=tokensupply&contractaddress=0xf06CEEEb31a39EA5B22a0d0AdffD2a2CD80CEc0F&apikey=FPBBQN6698WE8EXS86BA7D72XN3CZWJPGB
# https://api-goerli.etherscan.io/api?module=stats&action=tokensupply&contractaddress=0x1f9840a85d5af5bf1d1762f925bdaddc4201f984&apikey=FPBBQN6698WE8EXS86BA7D72XN3CZWJPGB


def get_current_token_id(contract_address):
  f = open("/Users/rahul/Documents/main/personal_learning_projects/creator_coin_new/creator_coin/deployed_contracts/nft_main_new_compiled_code.json")
  compiled_sol = json.load(f)

  bytecode = compiled_sol["contracts"]["NFTMainNew.sol"]["NFTMainNew"]["evm"]["bytecode"]["object"]
  abi = json.loads(compiled_sol["contracts"]["NFTMainNew.sol"]["NFTMainNew"]["metadata"])["output"]["abi"]

  w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/2101c205c1c447daa8ad7d7d9cb9bb5b"))

  CreatorContract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)
  current_token_id = CreatorContract.functions.getCurrentTokenID().call()
  return current_token_id



# # https://goerli.etherscan.io/address/0xf06ceeeb31a39ea5b22a0d0adffd2a2cd80cec0f
# get_token_supply("0xf06ceeeb31a39ea5b22a0d0adffd2a2cd80cec0f")





