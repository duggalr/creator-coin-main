import secrets
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








