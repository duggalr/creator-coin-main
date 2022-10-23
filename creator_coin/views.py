from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
# from django.urls import reverse

from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# from rest_framework.authtoken.models import Token

from .models import UserNonce, Web3User, CreatorProfile, GithubProfile, UserNft, UserBetaEmails, UserNftTransactionHistory, CreatorProjectLog
# from .serializers import Web3UserSerializer

from requests_oauthlib import OAuth2Session

from eth_account.messages import encode_defunct
# import web3
from web3.auto import w3
import os
import magic

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv( os.path.join(BASE_DIR, 'creator_coin_new/.env') )

from . import main_utils




# TODO: 
  # add good logging for debugging later on...



# def home_two(request):
#   return render(request, 'home_three.html')


# def home_original(request):
#   return render(request, 'home_one.html')


def home(request):
  if request.method == "POST":
    user_email = request.POST['user_email']

    email_objects = UserBetaEmails.objects.filter(user_email=user_email)
    if len(email_objects) == 0:
      b = UserBetaEmails.objects.create(
        user_email=user_email
      )
      b.save()
      # return redirect('home')
      return JsonResponse({'success': True})
    else: 
      return JsonResponse({'duplicate': True})
      
  return render(request, 'home_two.html')


def about_page(request):
  return render(request, 'manifesto.html')


# TODO:
def explore_project(request):
  # all_projects = UserProject.objects.all()
  # # nft_images = ProjectNftImage.objects.all()

  # rv = []
  # for obj in all_projects:
  #   nft_image_obj = ProjectNftImage.objects.filter(project_obj=obj)
  #   rv.append({
  #     'nft_image_object': nft_image_obj
  #   })
  #   # rv.append({
  #   #   'nft_project_image:' nft_image_obj,
  #   #   'project_object': obj
  #   # })
  
  # return render(request, 'explore_project.html', {'all_projects': all_projects})

  # TODO: 
    # fetch all profiles with a NFT MINTED**
    # then, fetch all others
      # filter for both in the dropdown

  return render(request, 'explore_project.html')



def my_profile(request):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)

  creator_profile_obj = CreatorProfile.objects.get(user_obj=user_obj)
  return redirect('user_token_page', profile_id=creator_profile_obj.id)


# web3-user-id --> change to slug 
  # t

def user_token_page(request, profile_id):
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)

  user_nft_obj = None
  user_nft_objects = UserNft.objects.filter(creator_obj=creator_profile_obj)
  # print('user-nft-objs:', user_nft_objects)

  if len(user_nft_objects) == 1:  # TODO: enforce to only ensure it's one
    user_nft_obj = user_nft_objects[0]

  same_user = False
  if request.user.is_anonymous is False:
    current_user_pk_address = request.user.user_pk_address
    if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
      same_user = True

  # saved_user_objects = Web3User.objects.filter(current_user)
  # print(saved_user_objects)

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

  # nft_currently_deployed = True
  # if user_nft_obj is not None:
    

  if request.method == 'POST':

    print('post-data:', request.POST)

    creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  
    current_user_pk_address = request.user.user_pk_address
    if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
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
  
  project_log_list = CreatorProjectLog.objects.filter(creator_obj=creator_profile_obj).order_by('-log_created_date')

  return render(request, 'user_token_page_two.html', {
    'creator_profile': creator_profile_obj,
    'same_user': same_user,
    'profile_id': profile_id,
    'github_profile': github_profile,
    'user_nft_obj': user_nft_obj,
    'user_three_dim_upload': user_three_dim_upload,
    'nft_transaction_history': nft_transaction_history,
    'project_log_list': project_log_list
  })

 

def delete_project_log(request, project_log_id):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)

  project_log_obj = get_object_or_404(CreatorProjectLog, id=project_log_id)
  if user_obj == project_log_obj.creator_obj.user_obj:
    project_log_obj.delete()
    return redirect('user_token_page', profile_id=project_log_obj.creator_obj.id)

  # creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  
  # CreatorProjectLog.objects.filter(id=project_log_id).delete()
  # return redirect('user_token_page', profile_id=profile_id)


  
# TODO: authenticate request (request user is same as owner of NFT and go from there) 
def mint_new_nft_token(request, profile_id):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  print('user-obj:', user_obj)

  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  if creator_profile_obj.user_obj.user_pk_address != user_pk_address:
    return redirect('user_token_page', profile_id=profile_id)

  # # creator_profile_obj = CreatorProfile.objects.get(id=profile_id)
  # creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)

  # user_nft_obj = None
  # user_nft_obj = UserNft.objects.get(creator_obj=creator_profile_obj)
  # # print('user-nft-objs:', user_nft_objects)
  # # if len(user_nft_objects) == 1:
  # #   user_nft_obj = user_nft_objects[0]

  # same_user = False
  # if request.user.is_anonymous is False:
  #   current_user_pk_address = request.user.user_pk_address
  #   if current_user_pk_address == creator_profile_obj.user_obj.user_pk_address:
  #     same_user = True

  # user_pk_address = request.user
  # user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  # print('user-obj:', user_obj)

  # creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  # if creator_profile_obj.user_obj.user_pk_address != user_pk_address:
  #   return redirect('user_token_page', profile_id=profile_id)




# # TODO: delete
# def project_page(request, project_id):
#   print('project-id:', project_id)
#   return render(request, 'project_page_new.html')
#   # # user_project_list = UserProject.objects.filter(id=project_id)
#   # # if len(user_project_list) > 0:
#   # #   user_project = user_project_list[0]
#   # user_project_obj = get_object_or_404(UserProject, id=project_id)
#   # # nft_image = ProjectNftImage.objects.get(project_obj=user_project_obj)

#   # # profile_objects = CreatorProfile.objects.filter(user_obj=user_project_obj)
#   # # if len(profile_objects) == 1:
#   # #   user_profile_obj = profile_objects[0]

#   # print(user_project_obj.creator_profile.user_obj.user_pk_address, request.user)
#   # if user_project_obj.user_obj.user_pk_address == request.user:  # TODO: add option for User to Mint-NFT 
#   #   print('True')

#   # return render(request, 'project_page_new.html', {'user_project': user_project_obj})




# TODO:
  # make this authenticated 
  # add the user-obj and redirect to project-page 
    # from here, have option for user to mint-NFT for project  (<-- make profile last)
      # on profile, user should see all the project's he has created along with NFT's 
@login_required(login_url='/')
def create_profile(request):
  user_obj = request.user

  if request.method == 'POST':

    current_user_pk_address = request.POST['user_obj']
    user_object = Web3User.objects.get(user_pk_address=current_user_pk_address)

    profile_objects = CreatorProfile.objects.filter(user_obj=user_object)
    if len(profile_objects) == 1:
      user_profile_obj = profile_objects[0]
      creator_name = request.POST['creator_name']
      creator_email = request.POST['creator_email']
      creator_personal_website = request.POST['creator_website']
      creator_github_website = request.POST['creator_github_website']
      creator_discord_website = request.POST['creator_discord_website']
      creator_description = request.POST['creator_description']

      user_profile_obj.creator_name = creator_name
      user_profile_obj.creator_email = creator_email
      user_profile_obj.creator_personal_website = creator_personal_website
      # TODO: github validation to ensure only github-website 
      user_profile_obj.creator_github_website = creator_github_website
      user_profile_obj.creator_discord_website = creator_discord_website
      user_profile_obj.creator_description = creator_description

      user_profile_obj.save()
      return redirect('user_profile')

      # project_title = request.POST['project_title']
      # project_website = request.POST['project_website']
      # project_github_website = request.POST['project_github_website']
      # project_discord_website = request.POST['project_discord_website']
      # project_description = request.POST['project_description']

      # user_project_obj = UserProject.objects.create(
      #   creator_profile=user_profile_obj,
      #   title=project_title,
      #   description=project_description,
      #   project_website=project_website,
      #   github_webite=project_github_website,
      #   discord_website=project_discord_website
      # )
      # user_project_obj.save()

      # ## TODO: link to creator/user here & *remove all previous images for project if update*
      # nft_image_list = request.FILES.getlist('nft_image')
      # nft_image_obj = ProjectNftImage.objects.create(
      #   project_obj = user_project_obj,
      #   nft_image = nft_image_list[0]
      # )
      # nft_image_obj.save()

      # return redirect('project_page', project_id=user_project_obj.id)

    else: # TODO: fill this
      pass


  return render(request, 'create_page_two.html', {'user_object': user_obj})



# TODO: 
  # ensure only the user who created the profile has access to edit page
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
      return redirect('user_token_page', profile_id=profile_id)

    creator_profile_obj.creator_name = request.POST['person_name']
    creator_profile_obj.creator_email = request.POST['personal_email']
    creator_profile_obj.creator_personal_website = request.POST['project_website']
    creator_profile_obj.creator_discord_website = request.POST['project_discord_website']
    creator_profile_obj.creator_description = request.POST['project_description']
    creator_profile_obj.save()

    return redirect('user_token_page', profile_id=profile_id)

    # nft_image_file = request.FILES.getlist('nft_image')
    # if len(nft_image_file) > 0:  # update nft-image for project
    #   user_project_obj.title = request.POST['project_title']
    #   user_project_obj.description = request.POST['project_description']
    #   user_project_obj.project_website = request.POST['project_website']
    #   user_project_obj.github_webite = request.POST['project_github_website']
    #   user_project_obj.discord_website = request.POST['project_discord_website']
    #   user_project_obj.save()
      
  else:
    return render(request, 'create_project.html', {'creator_profile': creator_profile_obj})

  # # user_project_obj = UserProject.objects.get_object_or_404(id=project_id)
  # user_project_obj = get_object_or_404(UserProject, id=project_id)
  # nft_image = ProjectNftImage.objects.get(project_obj=user_project_obj)

  # if request.method == "POST":
  #   print(request.POST)
  #   nft_image_file = request.FILES.getlist('nft_image')
  #   if len(nft_image_file) > 0:  # update nft-image for project
  #     user_project_obj.title = request.POST['project_title']
  #     user_project_obj.description = request.POST['project_description']
  #     user_project_obj.project_website = request.POST['project_website']
  #     user_project_obj.github_webite = request.POST['project_github_website']
  #     user_project_obj.discord_website = request.POST['project_discord_website']
  #     user_project_obj.save()
      
  #     # ProjectNftImage.objects.

  # return render(request, 'create_project.html', {'user_project': user_project_obj, 'nft_image': nft_image})



# def nft_page_example(request):
#   return render(request, 'nft_page_example.html')


# TODO: ensure only the person who is 'owner' of the profile can see stuff; not everyone
@login_required(login_url='/')
def user_profile(request):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  print('user-obj:', user_obj)
  creator_profile = get_object_or_404(CreatorProfile, user_obj=user_obj)
  # TODO: 
    # show user's purchased and created <-- after this has been created (create basic UI for this already though)

  return render(request, 'user_profile.html', {'creator_profile': creator_profile})
 

@login_required(login_url='/')
def logout_view(request):
  logout(request)
  return redirect('home')






## API   

# Much of the web3 login is based from (credits go to author):
  # https://github.com/ManaanAnsari/MetaMask-Login-Python/blob/8f15caa1a374660629fe199ef55cb8458cde86d1/backend/user_management/views.py

# TODO: **review vulnb's here as super important** / mitm can help
# def metamask_login(request):
class UserNonceView(APIView):
  """
  Generate user nonce given pk_address
  Create Web3User with pk_address if doesn't exist
  """
  def get(self, request):
    pk_address = request.GET.get('web3_address')
    # print('pk-address:', pk_address)
  
    web_three_users = Web3User.objects.filter(user_pk_address=pk_address)
    web_three_user_obj = None
    if len(web_three_users) == 1:  # should never be >1 as pk_address is unique
      web_three_user_obj = web_three_users[0]
    else:
      web_three_user_obj = Web3User.objects.create(
        user_pk_address=pk_address
      )
      web_three_user_obj.save()

      creator_profile = CreatorProfile.objects.create(
        user_obj=web_three_user_obj
      )
      creator_profile.save()

    
    UserNonce.objects.filter(user=web_three_user_obj).delete()

    nonce = main_utils.generate_nonce()
    user_nonce_obj = UserNonce.objects.create(
      nonce=nonce,
      user=web_three_user_obj
    )
    user_nonce_obj.save()

    rv = {}
    rv['success'] = True
    rv['data'] = {'nonce': nonce}
    rv['message'] = 'user nonce created'

    return JsonResponse(rv)
    # return Response(rv, status = status.HTTP_200_OK)



class LoginView(APIView):
  """
  Web3 Login given user public-key and signature for generated nonce
  """
  def post(self, request):
    data = request.data
    # print('data:', data)

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
              login(request, user_obj)
              
              creator_profile_obj = CreatorProfile.objects.get(user_obj=user_obj)
              print('creator-profile:', creator_profile_obj)

              return Response({
                'success': True, 
                'message': 'user successfully logged in.', 
                'url': 'profile',
                'profile_id': creator_profile_obj.id
              })

    else:
      pass
 




@login_required(login_url='/')
def github_login(request):
  client_id = os.getenv("github_client_id")
  authorization_base_url = 'https://github.com/login/oauth/authorize'
  github = OAuth2Session(client_id)
  authorization_url, state = github.authorization_url(authorization_base_url)
  request.session['oauth_state'] = state
  return redirect(authorization_url)



@login_required(login_url='/')
def github_callback(request):
  client_id = os.getenv("github_client_id")
  client_secret = os.getenv("github_client_secret")
  token_url = 'https://github.com/login/oauth/access_token'

  github_request_url = request.build_absolute_uri()
  github_request_url = github_request_url.replace('http', 'https')
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

  return redirect('user_token_page', profile_id=web3_user.id)



@login_required(login_url='/')
def create_token_form(request): # TODO: ensure proper file-validation is done on server-side
  
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  #  Web3User.objects.get(user_pk_address=current_user_pk_address)

  creator_obj = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_objects = UserNft.objects.filter(creator_obj=creator_obj)
  if len(user_nft_objects) != 0:
    return redirect('user_token_page', profile_id=user_object.id)


  max_file_size = 100
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'model/gltf-binary'
  ]

  if request.method == 'POST':
    # print(request.POST, request.FILES)

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

        if form_validation_error is False:
          # print('uploaded-file:', uploaded_file)
          
          user_pk_address = request.POST['user_obj']
          print('user-obj:', user_pk_address)
          
          # TODO: can this user_pk_address return not found or invalid value?
          user_object = Web3User.objects.get(user_pk_address=user_pk_address)
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
    'user_object': user_object
  })



@login_required(login_url='/')
def update_token_form(request):
  current_user_pk_address = request.user.user_pk_address
  # user_object = Web3User.objects.get(user_pk_address=current_user_pk_address)
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)
  
  # TODO:          
    # NFT-View for Owner and Public** 

    # **if user has already created NFT, at the moment, they cannot create and launch another one <-- prevent this**
      # think about other, similar cases to this
 
    # once launched, NFT-metadata can not be updated
      # can the total-supply change? <-- not initially (after, yes)
 
    # **finalize all auth/user-settings in profile-page, etc.
    # actually use it to launch an NFT 
      # **(Optional): do project-log, desc-markdown, share before NFT launch & etherscan
  
    # **ensure the placeholder and coin object look really good <-- first thing the user will see
 

  max_file_size = 100
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'model/gltf-binary'
  ]
 
  if request.method == 'POST': # TODO: do we need to do any user-auth-verification here?
    user_nft = request.POST['user_nft_obj']
    nft_name = request.POST['token_name']
    nft_price = request.POST['token_price_field']
    nft_total_supply = request.POST['nft_total_supply']
    
    nft_name = request.POST['token_name']
    nft_price = request.POST['token_price_field']
    nft_total_supply = request.POST['nft_total_supply']

    form_validation_error = False
    try:
      nft_float_price = float(nft_price)
      if nft_float_price <= 0 :
        form_validation_error = True
    except:
      form_validation_error = True
    
    if nft_name == '':
      form_validation_error = True


    # print('POST-method:', request.POST, request.FILES)
    uploaded_file = None
    upload_file_mb_size = 0
    if 'nft_image_upload' in request.FILES:
    # nft_image_upload = request.POST['nft_image_upload']
    # uploaded_file = None
    # upload_file_mb_size = 0
    # if nft_image_upload != '' and form_validation_error is False:
      uploaded_file = request.FILES['nft_image_upload']   
      
      content_type = magic.from_buffer(uploaded_file.read(), mime=True) # verifies the uploaded file
      upload_file_mb_size = uploaded_file.size / 1024 / 1024

      if content_type in accepted_content_types and upload_file_mb_size <= max_file_size:
        # user_nft_object.nft_media_file = uploaded_file
        pass
      
      else:
        form_validation_error = True


    if form_validation_error is False:
      user_nft_object = get_object_or_404(UserNft, id=user_nft)
      user_nft_object.nft_name = nft_name
      user_nft_object.nft_price = nft_price
      user_nft_object.nft_total_supply = nft_total_supply
      if uploaded_file is not None:
        user_nft_object.nft_media_file = uploaded_file
      user_nft_object.save()

      return redirect('user_token_page', profile_id=user_object.id)

    else:
      return render(request, 'launch_token_form.html', {
        'form_validation_error': form_validation_error,
        'nft_name': request.POST['token_name'],
        'nft_price': request.POST['token_price_field'],
        'nft_total_supply': request.POST['nft_total_supply']
      })


  three_dim_file_types = [
    '.glb', '.gltf', '.obj', '.ply', '.fbx' '.svg'
  ]
  fn, file_extension = os.path.splitext(user_nft_obj.nft_media_file.url)

  user_three_dim_upload = False
  if file_extension in three_dim_file_types:
    user_three_dim_upload = True

  return render(request, 'launch_token_form.html', {
    'user_nft_obj': user_nft_obj,
    'nft_name': user_nft_obj.nft_name,
    'nft_symbol': user_nft_obj.nft_symbol,
    'nft_price': user_nft_obj.nft_price,
    'nft_total_supply': user_nft_obj.nft_total_supply,
    'nft_uploaded_image_url': user_nft_obj.nft_media_file.url,
    'user_editing': True,
    'user_upload_3d_model': user_three_dim_upload
  })



def deploy_new_nft(request):
  if request.method == "POST":
    pass


@login_required(login_url='/')
def verify_user_profile(request):
  user_pk_address = request.user
  user_obj = get_object_or_404(Web3User, user_pk_address=user_pk_address)
  creator_profile = get_object_or_404(CreatorProfile, user_obj=user_obj)
  
  user_github_profile = GithubProfile.objects.filter(user_obj=user_obj)
  if len(user_github_profile) > 0 and creator_profile.creator_name is not None and creator_profile.creator_name != '':
    return JsonResponse({'success': True})
  
  return JsonResponse({'success': False})



def delete_non_minted_nft(request):
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  # user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)
  UserNft.objects.filter(creator_obj=creator_profile).delete()
  
  return redirect('user_token_page', profile_id=creator_profile.id)



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



def save_nft_metadata(request):
  current_user_pk_address = request.user.user_pk_address
  user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)

  ipfs_uploaded, ipfs_cid = main_utils.store_file_in_ipfs(user_nft_obj)
  print('ipfs-res:', ipfs_uploaded, ipfs_cid)

  if ipfs_uploaded:
    user_nft_obj.nft_ipfs_url = "ipfs://" + ipfs_cid
    user_nft_obj.save()

    return JsonResponse({'success': True})

  else:
    return JsonResponse({'success': False, 'error_message': 'Could not upload file to IPFS.'})


# handle-eth-account-change
def handle_account_change(request):
  # print(request)
  # print(request.user)
  if request.user.is_anonymous is False:  # TODO: user was logged in; let's log out the previous user and redirect to home?
    return JsonResponse({'redirect': True})
  else:
    return JsonResponse({'redirect': False})
  




@require_http_methods(["POST"])
def nft_launch_final(request):
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

  # print('nft-launch-post:', request.POST)

  user_nft_obj.nft_deployed = True
  user_nft_obj.nft_deployed_transaction_hash = nft_transaction_hash
  user_nft_obj.nft_deployed_contract_data = nft_deployed_data
  user_nft_obj.nft_deployed_nonce = nft_deployed_nonce
  user_nft_obj.nft_deployed_chain_id = nft_deployed_chain_id
  user_nft_obj.nft_deployed_contract_address = nft_contract_address
  user_nft_obj.save()

  return JsonResponse({'success': True})


 
# TODO: add profile-id to params for this url; fetch that object and go from them to implement buy (ensure handled well)
def fetch_nft_main_data(request, profile_id):
  # print('pid:', profile_id)
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  # UserNft.objects.get()
  user_nft_obj = get_object_or_404(UserNft, creator_obj=creator_profile_obj)


  # print( 'url:', request.build_absolute_uri() )
  # current_user_pk_address = request.user.user_pk_address
  # user_object = get_object_or_404(Web3User, user_pk_address=current_user_pk_address)
  # creator_profile = CreatorProfile.objects.get(user_obj=user_object)
  # user_nft_obj = UserNft.objects.get(creator_obj=creator_profile)

  # nft_contract_address = user_nft_obj.nft_deployed_contract_address
  return JsonResponse({
    'nft_contract_address': user_nft_obj.nft_deployed_contract_address,
    'nft_token_price': user_nft_obj.nft_price
  })

  # fetch("http://127.0.0.1:7500/static/json_files/nft_main_compiled_code.json")
  # f = open()



# TODO: 
  # is this not a secure way to 'save' an executed buy-transaction 
  # rather, use etherscan api to fetch token-transactions
    # use contract-function-call to fetch total-supply  
@require_http_methods(["POST"])
def save_nft_transaction_data(request):
  """
  Save a buy transaction that just occured for a specific NFT
  """
  print('save-nft-post:', request.POST)
  
  profile_id = request.POST['profile_id']
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)
  # UserNft.objects.get()
  user_nft_obj = get_object_or_404(UserNft, creator_obj=creator_profile_obj)

  # Save the bought transaction 
    # keep a running count of the supply in new model? 
  print('post-data:', request.POST)

  nft_history_obj = UserNftTransactionHistory.objects.create(
    nft_obj = user_nft_obj, 
    transaction_hash = request.POST['nft_transaction_hash']
  )
  nft_history_obj.save()

  return JsonResponse({'success': True})





