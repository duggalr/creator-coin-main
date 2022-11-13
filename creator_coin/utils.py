import os
import json
import secrets
import requests
from web3 import Web3

import io
from urllib.request import urlopen
import bleach

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

    # print('nft-url:', obj.nft_media_file.url, obj.nft_media_file)
    contents = io.BytesIO( urlopen(obj.nft_media_file.url).read() )

    # example passing only required values which don't have defaults set
    try:
      # Store a file
      api_response = api_instance.store(body=contents, _check_return_type=False)
      # print('api-res', api_response)
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
  transaction_url = f'https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={tx_hash}&apikey={os.getenv("etherscan_api_key")}'
  res = requests.get(transaction_url)
  if res.status_code == 200:
    return res.json()
  else:
    return None


def get_current_token_id(contract_address):
  f = open("nft_main_new_compiled_code.json")
  compiled_sol = json.load(f)
  
  abi = json.loads(compiled_sol["contracts"]["NFTMain.sol"]["NFTMain"]["metadata"])["output"]["abi"]

  w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{os.getenv('goerli_api_key')}"))

  CreatorContract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)
  try:
    current_token_id = CreatorContract.functions.getCurrentTokenID().call()
    return current_token_id
  except:
    return None
  

def bleach_text(text):
  return bleach.clean(text)


def get_user_recent_commits(username):
  github_personal_token = os.getenv("github_personal_token")
  num_per_page_limit = 10
  url = f'https://api.github.com/search/commits?q=author:{username}&sort=author-date&order=desc&page=1&per_page={num_per_page_limit}'
  headers = {"Authorization": "Bearer %s" % github_personal_token }
  res = requests.get(url, headers=headers)
  data = res.json()['items']
  
  rv = []
  for di in data:
    commit_dict = di['commit']
    author_dict = commit_dict['author']
    commit_message = commit_dict['message']
    author_name = author_dict['name']
    github_url = di['html_url']
    commit_date = author_dict['date']
    commit_date_clean = commit_date.split('T')[0]
    # print(github_url, commit_date_clean)
    rv.append({
      'commit_url': github_url,
      'commit_date': commit_date_clean,
      'commit_author': author_name,
      'commit_message': commit_message
    })
    
  return rv

