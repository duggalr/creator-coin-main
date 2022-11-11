from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .models import UserNonce, Web3User, CreatorProfile, GithubProfile, UserNft, UserBetaEmails, UserNftTransactionHistory, CreatorProjectLog, UserNftCollection

from requests_oauthlib import OAuth2Session

from eth_account.messages import encode_defunct
from web3.auto import w3
import os
import magic

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv( os.path.join(BASE_DIR, 'creator_coin_new/.env') )

from . import utils




def home(request):

  if request.method == "POST":  # get the user email
    user_email = request.POST['user_email']
    if user_email != '':
      email_objects = UserBetaEmails.objects.filter(user_email=user_email)
      if len(email_objects) == 0:
        b = UserBetaEmails.objects.create(
          user_email=user_email
        )
        b.save()
        return JsonResponse({'success': True})
      else: 
        return JsonResponse({'duplicate': True})
  
  user_nft_obj = None
  if 'RDS_DB_NAME' in os.environ:
    creator_profile_obj = CreatorProfile.objects.get(id=11)
    user_nft_obj = UserNft.objects.get(creator_obj=creator_profile_obj)
  
  nft_total_token_supply = None
  nft_total_sold = None
  if user_nft_obj is not None and user_nft_obj.nft_deployed:
    current_token_id = utils.get_current_token_id(user_nft_obj.nft_deployed_contract_address)
    logging.warning(f'Current Creator Coin NFT Token-ID: {current_token_id}')

    if current_token_id is not None:
      nft_total_token_supply = user_nft_obj.nft_total_supply - current_token_id
      nft_total_sold = current_token_id

      if user_nft_obj.nft_deployed_transaction_status is None:  # if 0/1, it is updated
        transaction_dict = utils.get_transaction_status(user_nft_obj.nft_deployed_transaction_hash)
        logging.warning(f'transaction-dict: {transaction_dict}')

        if transaction_dict is not None:
          transaction_status = transaction_dict['result']['status']
          # print('transaction-dict:', transaction_dict)
          try:
            user_nft_obj.nft_deployed_transaction_status = transaction_status
            user_nft_obj.save()
          except:
            pass
    
        else:
          logging.warning(f'Current nft transaction status is None from user, {request.user}')
    
    else:
      logging.warning(f'Current token-id for deployed nft from user, {request.user} is None')
      

  return render(request, 'home.html', {
    'anon_user': request.user.is_anonymous,
    'creator_coin_nft_total_supply': nft_total_token_supply,
    'creator_coin_nft_total_sold': nft_total_sold,
    'creator_coin_nft_object': user_nft_obj
  })


def about_page(request):
  return render(request, 'manifesto.html')


def explore_project(request):
  # show all profiles which have a deployed NFT first, then all profiles with NFT, then all other profiles 
  
  three_dim_file_types = [
    '.glb', '.gltf', '.obj', '.ply', '.fbx' '.svg'
  ]

  deployed_creator_profile_objects = []
  deployed_nfts = UserNft.objects.filter(nft_deployed=True).order_by('-nft_updated_at')
  deployed_nft_list = []
  for obj in deployed_nfts:
    fn, file_extension = os.path.splitext(obj.nft_media_file.url)
    if file_extension in three_dim_file_types:
      user_three_dim_upload = True
    else:
      user_three_dim_upload = False

    deployed_nft_list.append({'nft_obj': obj, 'user_three_dim_upload': user_three_dim_upload})
    deployed_creator_profile_objects.append(obj.creator_obj)


  other_profiles_with_nfts = UserNft.objects.filter(nft_deployed=False).order_by('-nft_updated_at')
  non_deployed_nft_list = []
  for obj in other_profiles_with_nfts:
    fn, file_extension = os.path.splitext(obj.nft_media_file.url)
    if file_extension in three_dim_file_types:
      user_three_dim_upload = True
    else:
      user_three_dim_upload = False

    non_deployed_nft_list.append({'nft_obj': obj, 'user_three_dim_upload': user_three_dim_upload})
    deployed_creator_profile_objects.append(obj.creator_obj)


  final_profile_rv = []
  creator_profile_objects = CreatorProfile.objects.all()
  for obj in creator_profile_objects:
    if obj not in deployed_creator_profile_objects:
      final_profile_rv.append(obj)
  
  return render(request, 'explore_project.html', {
    'deployed_nft_objects': deployed_nft_list,
    'non_deployed_nft_objects': non_deployed_nft_list,
    'all_other_profiles': final_profile_rv
  })


@login_required(login_url='/')
def my_profile(request):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  creator_profile_obj = get_object_or_404(CreatorProfile, user_obj=user_obj)
  return redirect('user_token_page', profile_id=creator_profile_obj.id)



def user_token_page(request, profile_id):
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)

  user_nft_obj = None
  user_nft_objects = UserNft.objects.filter(creator_obj=creator_profile_obj)

  logging.warning(f'User NFT Objects: {user_nft_objects} / Length NFT Objects: {len(user_nft_objects)}')

  if len(user_nft_objects) == 1:  # TODO: enforce to only ensure it's one
    user_nft_obj = user_nft_objects[0]
  else:
    if len(user_nft_objects) > 1:
      logging.warning(f'USER WITH CREATOR PROFILE-ID: {profile_id} HAS MORE THAN ONE NFT?!?!')


  same_user = False
  if request.user.is_anonymous is False:
    current_user_pk_address = request.user.user_pk_address
    if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
      same_user = True

  github_profile = None
  if creator_profile_obj.user_obj.github_verified is True:
    # user_obj = Web3User.objects.get( user_pk_address=request.user )
    github_profile = GithubProfile.objects.get(user_obj=creator_profile_obj.user_obj)

  three_dim_file_types = [
    '.glb', '.gltf', '.obj', '.ply', '.fbx' '.svg'
  ]
  user_three_dim_upload = False
  if user_nft_obj is not None:
    # three_dim_model = False
    # main_utils.check_if_three_dim_model(user_nft_obj.nft_media_file)
  
    fn, file_extension = os.path.splitext(user_nft_obj.nft_media_file.url)
    if file_extension in three_dim_file_types:
      user_three_dim_upload = True


  # Join Beta Email Form
  if request.method == 'POST' and 'join_beta_email_form' in request.POST:

    creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
    current_user_pk_address = request.user.user_pk_address

    if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
      user_email = request.POST['user_email']
      logging.warning(f'saving email for user: {current_user_pk_address} / user-email: {user_email}')
      
      if user_email != '':
        email_objects = UserBetaEmails.objects.filter(user_email=user_email)
        if len(email_objects) == 0: # TODO: display success message or disable button on email submission in this page
          b = UserBetaEmails.objects.create(
            creator_obj=creator_profile_obj,
            user_email=user_email
          )
          b.save()

          creator_profile_obj.creator_email = user_email
          creator_profile_obj.save()

          return redirect('user_token_page', profile_id=creator_profile_obj.id)
        else: 
          return redirect('user_token_page', profile_id=creator_profile_obj.id)
  

  email_join_beta_form_display = False
  user_email_emails = UserBetaEmails.objects.filter(creator_obj=creator_profile_obj)  
  if len(user_email_emails) == 0:
    email_join_beta_form_display = True


  # Project Log Form
  if request.method == 'POST' and 'project-log-update' in request.POST:  # saving project-log inputs
    
    creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
    current_user_pk_address = request.user.user_pk_address

    if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
      
      logging.warning(f'saving project log for user: {current_user_pk_address}')

      log_title = request.POST['log-title']
      log_update = request.POST['log-update']
      cl = CreatorProjectLog.objects.create(
        creator_obj = creator_profile_obj,
        log_title = log_title,
        log_description = log_update
      )
      cl.save()

      return redirect('user_token_page', profile_id=profile_id)


  nft_transaction_history = UserNftTransactionHistory.objects.filter(nft_obj=user_nft_obj).order_by('-transaction_created_date')
  for nft_transaction_obj in nft_transaction_history:
    if nft_transaction_obj.transaction_status is None:
      transaction_dict = utils.get_transaction_status(nft_transaction_obj.transaction_hash)
      if transaction_dict is not None:
        transaction_status = transaction_dict['result']['status']
        try: 
          nft_transaction_obj.transaction_status = transaction_status
          nft_transaction_obj.save()
        except: # this is likely due to transaction not being executed and thus, transaction-status will be null
          pass
      else:
        logger.warning(f'NFT transaction status not received for trans-obj: {nft_transaction_obj}')

  project_log_list = CreatorProjectLog.objects.filter(creator_obj=creator_profile_obj).order_by('-log_created_date')
  user_nft_collection =  UserNftCollection.objects.filter(creator_obj=creator_profile_obj).order_by('-transaction_created_date')

  nft_total_token_supply = None
  nft_total_sold = None
  if user_nft_obj is not None and user_nft_obj.nft_deployed:
    # current_token_id = None
    # try:
    #   current_token_id = utils.get_current_token_id(user_nft_obj.nft_deployed_contract_address)
    # except:
    #   logging.warning(f'Current token-ID not available. Returned error when called.')
    #   pass
    
    current_token_id = utils.get_current_token_id(user_nft_obj.nft_deployed_contract_address)
    # logging.warning(f'Current token-ID: {current_token_id}')

    if current_token_id is not None:
      nft_total_token_supply = user_nft_obj.nft_total_supply - current_token_id
      nft_total_sold = current_token_id

      if user_nft_obj.nft_deployed_transaction_status is None:  # if 0/1, it is updated
        transaction_dict = utils.get_transaction_status(user_nft_obj.nft_deployed_transaction_hash)
        logging.warning(f'transaction-dict: {transaction_dict}')

        if transaction_dict is not None:
          transaction_status = transaction_dict['result']['status']
          # print('transaction-dict:', transaction_dict)
          try:
            user_nft_obj.nft_deployed_transaction_status = transaction_status
            user_nft_obj.save()
          except:
            pass
    
        else:
          logging.warning(f'Current nft transaction status is None from user, {request.user}')
    
    else:
      logging.warning(f'Current token-id for deployed nft from user, {request.user} is None')
      

  return render(request, 'user_profile_page_beta.html', {
    'anon_user': request.user.is_anonymous,
    'creator_profile': creator_profile_obj,
    'same_user': same_user,
    'profile_id': profile_id,
    'github_profile': github_profile,
    'user_nft_obj': user_nft_obj,
    'user_three_dim_upload': user_three_dim_upload,
    'nft_transaction_history': nft_transaction_history,
    'project_log_list': project_log_list,
    'user_nft_collection': user_nft_collection,
    'nft_total_token_supply': nft_total_token_supply,
    'nft_total_sold': nft_total_sold,
    'email_join_beta_form_display': email_join_beta_form_display
  })


@login_required(login_url='/')
def delete_project_log(request, project_log_id):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)

  project_log_obj = get_object_or_404(CreatorProjectLog, id=project_log_id)
  if user_obj == project_log_obj.creator_obj.user_obj:
    project_log_obj.delete()
    return redirect('user_token_page', profile_id=project_log_obj.creator_obj.id)


@login_required(login_url='/')
def edit_user_profile(request, profile_id):
  user_pk_address = request.user
  # user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)

  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  creator_profile_user_pk = creator_profile_obj.user_obj.user_pk_address

  # print('ue:', type(creator_profile_user_pk), type(user_pk_address) )
  if creator_profile_user_pk != str(user_pk_address):
    return redirect('user_token_page', profile_id=profile_id)

  if request.method == "POST":

    user_pk_address = request.user
    # user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)

    creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
    creator_profile_user_pk = creator_profile_obj.user_obj.user_pk_address

    if creator_profile_user_pk != str(user_pk_address):
      logger.warning(f'user tried to edit profile but request.user pk-address not same as profile-id one. user: {request.user}')
      return redirect('user_token_page', profile_id=profile_id)

    logger.warning(f'User has edited their creator profile. User: {request.user}')
    creator_profile_obj.creator_name = request.POST['person_name']
    creator_profile_obj.creator_email = request.POST['personal_email']
    creator_profile_obj.creator_personal_website = request.POST['project_website']
    creator_profile_obj.creator_discord_website = request.POST['project_discord_website']
    creator_profile_obj.creator_description = request.POST['project_description']
    creator_profile_obj.save()

    return redirect('user_token_page', profile_id=profile_id)
      
  else:
    return render(request, 'create_user_profile.html', {'creator_profile': creator_profile_obj})




@login_required(login_url='/')
def logout_view(request):
  logout(request)
  return redirect('home')



## API   
# Much of the web3 login is based from (credits go to author):
  # https://github.com/ManaanAnsari/MetaMask-Login-Python/blob/8f15caa1a374660629fe199ef55cb8458cde86d1/backend/user_management/views.py

class UserNonceView(APIView):
  """
  Generate user nonce given pk_address
  Create Web3User with pk_address if doesn't exist
  """
  def get(self, request):
    pk_address = request.GET.get('web3_address')

    if pk_address is not None:
      web_three_users = Web3User.objects.filter(user_pk_address=pk_address)
      web_three_user_obj = None
    
      return_nonce = False
      if len(web_three_users) == 1:  # should never be >1 as pk_address is unique
        return_nonce = True
        web_three_user_obj = web_three_users[0]
        
      elif len(web_three_users) == 0:
        return_nonce = True
        web_three_user_obj = Web3User.objects.create(  # create the user, but set active=False
          user_pk_address=pk_address,
          is_active=False
        )
        web_three_user_obj.save()

      else:  # should never be the case, but putting here for safety measures
        return_nonce = False

      if return_nonce is True and web_three_user_obj is not None:

        UserNonce.objects.filter(user=web_three_user_obj).delete()

        nonce = utils.generate_nonce()
        user_nonce_obj = UserNonce.objects.create(
          nonce=nonce,
          user=web_three_user_obj
        )
        user_nonce_obj.save()

        rv = {}
        rv['success'] = True
        rv['data'] = {'nonce': nonce}
        rv['message'] = 'user nonce created'

      else:
        rv = {}
        rv['success'] = False

    else:
      rv = {}
      rv['success'] = False

    return JsonResponse(rv)



class LoginView(APIView):
  """
  Web3 Login given user public-key and signature for generated nonce
  """
  def post(self, request):
    data = request.data

    if 'nonce_signature' in data and 'pk_address' in data:
      user_pk_address = data["pk_address"]
      user_nonce_signature = data["nonce_signature"]

      if Web3User.objects.filter(user_pk_address=user_pk_address).exists():
        user_obj = Web3User.objects.get(user_pk_address=user_pk_address)

        if UserNonce.objects.filter(user=user_obj).exists():
          saved_nonce_obj = UserNonce.objects.get(user=user_obj)
          saved_nonce = saved_nonce_obj.nonce

          message = "\nBy signing this message, you will sign the randomly generated nonce.  \n\nNonce: " + saved_nonce + " \n\nWallet Address: " + user_pk_address
          encode_msg = encode_defunct(text=message)

          recovered_signed_address = ( w3.eth.account.recover_message(encode_msg, signature=user_nonce_signature) )

          # print(f"original-addr: {user_pk_address} / signed-addr: {signed_address}")

          # # hash_msg = web3.Web3.sha3(text=saved_nonce)
          # hash_msg = web3.Web3.sha3(text=message)
          # # pk2 = w3.eth.account.recover_message(hash_msg, signature=user_nonce_signature)
          # recovered_public_key = w3.eth.account.recoverHash(hash_msg, signature=user_nonce_signature) 
          # print(f"recovered-has: {recovered_public_key} / user-sig: {user_nonce_signature} / user-pk-add: {user_pk_address}")

          if recovered_signed_address == user_obj.user_pk_address:
            UserNonce.objects.filter(user=user_obj).delete()            

            # Nonce is verified; ensure web3user_obj is True
            if user_obj.is_active is False:
              user_obj.is_active = True
              user_obj.save()

            login(request, user_obj)

            creator_profile_objects = CreatorProfile.objects.filter(user_obj=user_obj)

            if len(creator_profile_objects) == 1:  # existing profile login; since OnetoOneField, will always be 1
              return Response({
                'success': True, 
                'message': 'user successfully logged in.', 
                'url': 'profile',
                'profile_id': creator_profile_objects[0].id
              })

            else:
              # New User; Create the Creator Profile and redirect to this page
              creator_profile_obj = CreatorProfile.objects.create( 
                user_obj=user_obj
              )
              creator_profile_obj.save()

              return Response({
                'success': True, 
                'message': 'user successfully logged in.', 
                'url': 'profile',
                'profile_id': creator_profile_obj.id
              })

          else:
            Web3User.objects.get(user_pk_address=user_pk_address).delete()
            return Response({
              'success': False
            })

        else:
          Web3User.objects.get(user_pk_address=user_pk_address).delete()
          return Response({
            'success': False
          })

      else:
        return Response({
          'success': False
        })

    else:
      return Response({
        'success': False
      })
 

 

@login_required(login_url='/')
def github_login(request):
  client_id = os.getenv("github_client_id")
  authorization_base_url = 'https://github.com/login/oauth/authorize'
  github = OAuth2Session(client_id)
  authorization_url, state = github.authorization_url(authorization_base_url)
  
  logging.warning(f'auth-url: {authorization_url}')

  request.session['oauth_state'] = state
  return redirect(authorization_url)
 
 

@login_required(login_url='/')
def github_callback(request):
  client_id = os.getenv("github_client_id")
  client_secret = os.getenv("github_client_secret")
  token_url = 'https://github.com/login/oauth/access_token'

  github_request_url = request.build_absolute_uri()
  # TODO: need to make exception for local-dev
  # github_request_url = github_request_url.replace('http', 'https')
  # logging.warning(f'github-request-url: {github_request_url}')

  github = OAuth2Session(client_id, state=request.session['oauth_state'])
  token = github.fetch_token(
    token_url, 
    client_secret=client_secret, 
    authorization_response=github_request_url
  )
  
  user_data = github.get('https://api.github.com/user').json()
  # print(f'user-data: {user_data} / token: {token}')  

  web3_user = Web3User.objects.get(user_pk_address=request.user)
  web3_user.github_verified = True
  web3_user.save()

  if len(GithubProfile.objects.filter(user_obj=web3_user)) > 0:
    GithubProfile.objects.filter(user_obj=web3_user).delete()
  
  gp = GithubProfile.objects.create(
    user_obj=web3_user,
    github_username=user_data['login'],
    github_profile_url=user_data['html_url'],
    github_avatar_url=user_data['avatar_url']
  )
  gp.save()

  creator_profile = CreatorProfile.objects.get(user_obj=web3_user)
  
  return redirect('user_token_page', profile_id=creator_profile.id)



@login_required(login_url='/')
def create_token_form(request): # TODO: ensure proper file-validation is done on server-side
  
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  # print('user-object:', user_object)
  #  Web3User.objects.get(user_pk_address=current_user_pk_address)

  creator_obj = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_objects = UserNft.objects.filter(creator_obj=creator_obj)
  if len(user_nft_objects) != 0:
    return redirect('user_token_page', profile_id=creator_obj.id)


  max_file_size = 25
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'application/octet-stream'
  ]

  if request.method == 'POST':
    # print('post-data:', request.POST, request.FILES)

    form_validation_error = False

    if 'nft_image_upload' in request.FILES:
      uploaded_file = request.FILES['nft_image_upload']
      upload_file_mb_size = uploaded_file.size / 1024 / 1024
      content_type = magic.from_buffer(uploaded_file.read(), mime=True) # verifies the uploaded file

      if content_type in accepted_content_types and upload_file_mb_size <= max_file_size and form_validation_error is False:
        nft_name = request.POST['token_name']
        nft_symbol = request.POST['token_symbol']
        nft_price = request.POST['token_price_field']
        nft_total_supply = request.POST['nft_total_supply']

        try:
          nft_float_price = float(nft_price)
          if nft_float_price <= 0 :
            form_validation_error = True
            form_validation_error_message = "Really? NFT Price obviously must be greater than 0!"
        except:
          form_validation_error = True
          form_validation_error_message = "Nice Try... NFT Price must be a number."
        
        # reinforce token-symbol is 3 letters or less
        if len(nft_symbol) > 3:
          form_validation_error = True
          form_validation_error_message = "Your NFT symbol must be less than or equal to 3 characters."

        try: # sanity checks as you never know the data that can come from JS...
          nft_total_supply = int(nft_total_supply)
        except:
          form_validation_error = True
          form_validation_error_message = "Total NFT supply must be an integer"

        if nft_total_supply > 1000:
          form_validation_error = True
          form_validation_error_message = "Total NFT supply must be <= 1000."


        if form_validation_error is False:
          
          user_pk_address = request.POST['user_obj']
          
          user_object = None
          try: # sanity-checking...
            user_object = Web3User.objects.get(user_pk_address=user_pk_address)
          except:
            logger.warning(f'user tried creating nft but there object could not be found. User-PK: {user_pk_address}')
          
          if user_object is not None:
            logger.warning(f'user has created nft. user: {request.user}')
            user_profile_obj = CreatorProfile.objects.get(user_obj=user_object)

            user_nft_obj = UserNft.objects.create(
              creator_obj=user_profile_obj,
              nft_name=nft_name,
              nft_symbol=nft_symbol,
              nft_price=nft_price,
              nft_total_supply=nft_total_supply,
              nft_media_file=uploaded_file
            )
            user_nft_obj.save()
            
            return redirect('user_token_page', profile_id=user_profile_obj.id)

          else:
            return render(request, 'launch_token_form.html', {
              'nft_name': request.POST['token_name'],
              'nft_symbol': request.POST['token_symbol'],
              'nft_price': request.POST['token_price_field'],
              'nft_total_supply': request.POST['nft_total_supply']
            })

      else:
        form_validation_error = True
        form_validation_error_message = "Ugh.. seems like you submitted a file that clearly isn't accepted by me. Look at the file types and try again!"
            
    else:
      form_validation_error = True
      form_validation_error_message = "Really? You must submit an image for your NFT."

    if form_validation_error:
      return render(request, 'launch_token_form.html', {
        'form_validation_error': form_validation_error,
        'form_validation_error_message': form_validation_error_message,

        'nft_name': request.POST['token_name'],
        'nft_symbol': request.POST['token_symbol'],
        'nft_price': request.POST['token_price_field'],
        'nft_total_supply': request.POST['nft_total_supply']
      })


  return render(request, 'launch_token_form.html', {
    'user_object': user_object,
  })


@login_required(login_url='/')
def update_token_form(request):
  current_user_pk_address = request.user.user_pk_address
  # user_object = Web3User.objects.get(user_pk_address=current_user_pk_address)
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)
  logging.warning(f'update-token-form-creator-obj: {user_nft_obj}')
  
  max_file_size = 25
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'model/gltf-binary', 'application/octet-stream'
  ]
 
  if request.method == 'POST': 
    user_nft = request.POST['user_nft_obj']
    nft_name = request.POST['token_name']
    nft_price = request.POST['token_price_field']
    nft_total_supply = request.POST['nft_total_supply']
    
    nft_name = request.POST['token_name']
    nft_symbol = request.POST['token_symbol']
    nft_price = request.POST['token_price_field']
    nft_total_supply = request.POST['nft_total_supply']

    form_validation_error = False
    uploaded_file = None
    upload_file_mb_size = 0
    if 'nft_image_upload' in request.FILES:
      uploaded_file = request.FILES['nft_image_upload']

      content_type = magic.from_buffer(uploaded_file.read(), mime=True) # verifies the uploaded file
      upload_file_mb_size = uploaded_file.size / 1024 / 1024

      logger.warning(f'Upload-file: {uploaded_file} / Update-File Content Type: {content_type} / Upload File MB Size: {upload_file_mb_size}')

      if content_type in accepted_content_types and upload_file_mb_size <= max_file_size:
        
        if nft_name == '':
          form_validation_error = True
          form_validation_error_message = "You must name your NFT..."

        try:
          nft_float_price = float(nft_price)
          if nft_float_price <= 0 :
            form_validation_error = True
            form_validation_error_message = "Really? NFT Price obviously must be greater than 0!"
        except:
          form_validation_error = True
          form_validation_error_message = "Nice Try... NFT Price must be a number."
        
        # reinforce token-symbol is 3 letters or less
        if len(nft_symbol) > 3:
          form_validation_error = True
          form_validation_error_message = "Your NFT symbol must be less than or equal to 3 characters."

        try: # sanity checks as you never know the data that can come from JS...
          nft_total_supply = int(nft_total_supply)
        except:
          form_validation_error = True
          form_validation_error_message = "Total NFT supply must be an integer."

        if nft_total_supply > 1000:
          form_validation_error = True
          form_validation_error_message = "Total NFT supply must be <= 1000."
      
      else:
        form_validation_error = True
        form_validation_error_message = "Invalid file submitted for NFT."
      
    else: # file saved from before
      pass


    if form_validation_error:
      return render(request, 'launch_token_form.html', {
        'form_validation_error': form_validation_error,
        'form_validation_error_message': form_validation_error_message,
        'nft_name': request.POST['token_name'],
        'nft_symbol': request.POST['token_symbol'],
        'nft_price': request.POST['token_price_field'],
        'nft_total_supply': request.POST['nft_total_supply']
      })
    else:
      logging.warning(f"user: {request.user} has updated there nft")
      logging.warning(f"request-post: {request.POST}")

      user_nft_object = get_object_or_404(UserNft, id=user_nft)
      user_nft_object.nft_name = nft_name
      user_nft_object.nft_price = nft_price
      user_nft_object.nft_total_supply = nft_total_supply
      if uploaded_file is not None:
        user_nft_object.nft_media_file = uploaded_file
      user_nft_object.save()

      return redirect('user_token_page', profile_id=creator_profile.id)

  three_dim_file_types = [
    '.glb', '.gltf', '.obj', '.ply', '.fbx' '.svg'
  ]
  fn, file_extension = os.path.splitext(user_nft_obj.nft_media_file.url)

  user_three_dim_upload = False
  if file_extension in three_dim_file_types:
    user_three_dim_upload = True

  return render(request, 'launch_token_form.html', {
    'user_object': user_object,
    'user_nft_obj': user_nft_obj,
    'nft_name': user_nft_obj.nft_name,
    'nft_symbol': user_nft_obj.nft_symbol,
    'nft_price': user_nft_obj.nft_price,
    'nft_total_supply': user_nft_obj.nft_total_supply,
    'nft_uploaded_image_url': user_nft_obj.nft_media_file.url,
    'user_editing': True,
    'user_upload_3d_model': user_three_dim_upload
  })



# def deploy_new_nft(request):
#   if request.method == "POST":
#     pass


@login_required(login_url='/')
def verify_user_profile(request):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  creator_profile = get_object_or_404(CreatorProfile, user_obj=user_obj)
  
  user_github_profile = GithubProfile.objects.filter(user_obj=user_obj)
  if len(user_github_profile) > 0 and creator_profile.creator_name is not None and creator_profile.creator_name != '':
    return JsonResponse({'success': True})
  
  return JsonResponse({'success': False})


@login_required(login_url='/')
def delete_non_minted_nft(request):
  logging.warning(f"user: {request.user} is deleting their non-minted-nft")
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  # user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)
  # UserNft.objects.filter(creator_obj=creator_profile).delete()
  user_nft_obj = get_object_or_404(UserNft, creator_obj=creator_profile)
  if user_nft_obj.nft_deployed is False:
    UserNft.objects.filter(creator_obj=creator_profile).delete()

  return redirect('user_token_page', profile_id=creator_profile.id)


@login_required(login_url='/')
def get_minted_nft_metadata(request):
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)
  return JsonResponse({
    'nft_name': user_nft_obj.nft_name,
    'nft_symbol': user_nft_obj.nft_symbol,
    'nft_price': str(user_nft_obj.nft_price),
    'nft_total_supply': user_nft_obj.nft_total_supply,
    'nft_media_file': user_nft_obj.nft_media_file.url,
    'nft_ipfs_url': user_nft_obj.nft_ipfs_url
  })


@login_required(login_url='/')
def save_nft_metadata(request):
  logging.warning(f"user: {request.user} is saving nft metadata")

  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)

  ipfs_uploaded, ipfs_cid = utils.store_file_in_ipfs(user_nft_obj)
  # print('ipfs-res:', ipfs_uploaded, ipfs_cid)

  if ipfs_uploaded:
    user_nft_obj.nft_ipfs_url = "ipfs://" + ipfs_cid
    user_nft_obj.save()

    return JsonResponse({'success': True})

  else:
    return JsonResponse({'success': False, 'error_message': 'Could not upload file to IPFS.'})


# handle-eth-account-change
def handle_account_change(request):
  if request.user.is_anonymous is False:  # user was logged in; let's log out the previous user and redirect to home?
    return JsonResponse({'redirect': True})
  else:
    return JsonResponse({'redirect': False})
  


@login_required(login_url='/')
@require_http_methods(["POST"])
def nft_launch_final(request):
  logging.warning(f"user: {request.user} has executed nft-launch-final")

  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)

  # ipfs_uploaded, ipfs_cid = main_utils.store_file_in_ipfs(user_nft_obj)
  # print('ipfs-res:', ipfs_uploaded, ipfs_cid)

  nft_transaction_hash = request.POST['nft_transaction_hash']
  nft_deployed_data = request.POST['nft_deployed_data']
  nft_deployed_nonce = request.POST['nft_deployed_nonce']
  nft_deployed_chain_id = request.POST['nft_deployed_chain_id']
  nft_contract_address = request.POST['nft_contract_address']

  user_nft_obj.nft_deployed = True
  user_nft_obj.nft_deployed_transaction_hash = nft_transaction_hash
  user_nft_obj.nft_deployed_contract_data = nft_deployed_data
  user_nft_obj.nft_deployed_nonce = nft_deployed_nonce
  user_nft_obj.nft_deployed_chain_id = nft_deployed_chain_id
  user_nft_obj.nft_deployed_contract_address = nft_contract_address
  user_nft_obj.save()

  return JsonResponse({'success': True})


@login_required(login_url='/')
def fetch_nft_main_data(request, profile_id):
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  user_nft_obj = get_object_or_404(UserNft, creator_obj=creator_profile_obj)
  return JsonResponse({
    'nft_contract_address': user_nft_obj.nft_deployed_contract_address,
    'nft_token_price': user_nft_obj.nft_price
  })



@login_required(login_url='/')
@require_http_methods(["POST"])
def save_nft_transaction_data(request):
  """
  Save a buy transaction that just occured for a specific NFT
  """
  # print('save-nft-post:', request.POST)
  
  if request.user.is_anonymous is False:
    
    # print('post-data:', request.POST)

    logging.warning(f"user: {request.user} has executed a buy transaction")

    profile_id = request.POST['profile_id']
    creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
    user_nft_obj = get_object_or_404(UserNft, creator_obj=creator_profile_obj)
  
    number_of_tokens_bought = request.POST['number_of_tokens_bought']
    transaction_hash = request.POST['nft_transaction_hash']

    # web_three_obj = get_object_or_404(Web3User, user_pk_address=buyer_pk_address)
    # purchaser_profile_obj = CreatorProfile.objects.get(user_obj=web_three_obj)
    web_three_user_obj = Web3User.objects.get(user_pk_address=request.user)
    buyer_cp_obj = CreatorProfile.objects.get(user_obj=web_three_user_obj)

    nft_history_obj = UserNftTransactionHistory.objects.create(
      nft_obj = user_nft_obj,
      purchaser_user_obj=buyer_cp_obj,
      purchase_amount=number_of_tokens_bought,
      transaction_hash = transaction_hash
    )
    nft_history_obj.save()

    buyer_nft_collect_obj = UserNftCollection.objects.create(
      creator_obj = buyer_cp_obj,
      nft_transaction_history_obj = nft_history_obj
      # nft_obj = user_nft_obj      
    )
    buyer_nft_collect_obj.save()

    return JsonResponse({'success': True, 'redirect_profile_id': buyer_cp_obj.id})

  else:
    return JsonResponse({'success': False})



