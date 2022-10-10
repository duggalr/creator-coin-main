from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# from rest_framework.authtoken.models import Token

from .models import UserNonce, Web3User, CreatorProfile, GithubProfile, UserNft, UserBetaEmails
# from .serializers import Web3UserSerializer

from requests_oauthlib import OAuth2Session

from eth_account.messages import encode_defunct
import web3
from web3.auto import w3
import magic

import os
from dotenv import load_dotenv


# Get the path to the directory this file is in
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print('BASE-DIR:', os.path.join(BASE_DIR, '.env'))

# load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv("/Users/rahul/Documents/main/personal_learning_projects/creator_coin_new/creator_coin_new/.env")

from . import utils




# TODO: 
  # fix hardcoded env path above
  # add good logging for debugging later on...


def home(request):
  if request.method == "POST":
    user_email = request.POST['user_email']
    # print('user-email:', user_email)

    email_objects = UserBetaEmails.objects.filter(user_email=user_email)
    if len(email_objects) == 0:
      b = UserBetaEmails.objects.create(
        user_email=user_email
      )
      b.save()
      # return redirect('home')
      return JsonResponse({'success': True})

    else: # TODO: return success message or email already registered message
      return JsonResponse({'duplicate': True})
      

  return render(request, 'home_two.html')



def home_two(request):
  return render(request, 'home_three.html')


def home_original(request):
  return render(request, 'home_one.html')


def about_page(request):
  return render(request, 'manifesto.html')



def user_token_page(request, profile_id):
  # creator_profile_obj = CreatorProfile.objects.get(id=profile_id)
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)

  user_nft_objects = UserNft.objects.filter(creator_obj=creator_profile_obj)

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

  return render(request, 'user_token_page_two.html', {
    'creator_profile': creator_profile_obj,
    'same_user': same_user,
    'profile_id': profile_id,
    'github_profile': github_profile,
    'user_nft_obj': user_nft_objects

  })




def mint_new_nft_token():
  pass




# TODO: delete
def project_page(request, project_id):
  print('project-id:', project_id)
  return render(request, 'project_page_new.html')
  # # user_project_list = UserProject.objects.filter(id=project_id)
  # # if len(user_project_list) > 0:
  # #   user_project = user_project_list[0]
  # user_project_obj = get_object_or_404(UserProject, id=project_id)
  # # nft_image = ProjectNftImage.objects.get(project_obj=user_project_obj)

  # # profile_objects = CreatorProfile.objects.filter(user_obj=user_project_obj)
  # # if len(profile_objects) == 1:
  # #   user_profile_obj = profile_objects[0]

  # print(user_project_obj.creator_profile.user_obj.user_pk_address, request.user)
  # if user_project_obj.user_obj.user_pk_address == request.user:  # TODO: add option for User to Mint-NFT 
  #   print('True')

  # return render(request, 'project_page_new.html', {'user_project': user_project_obj})



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

  # TODO: 
    # add image and display project's; go from there
    # what happens when a user disconnects an account from CreatorCoin?
  # return render(request, 'explore_project.html', {'all_projects': all_projects})
  return render(request, 'explore_project.html')



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
  creator_profile_obj = get_object_or_404(CreatorProfile, id=profile_id)

  if request.method == "POST":
    print(request.POST)

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

    nonce = utils.generate_nonce()
    user_nonce_obj = UserNonce.objects.create(
      nonce=nonce,
      user=web_three_user_obj
    )
    user_nonce_obj.save()

    rv = {}
    rv['data'] = {'nonce': nonce}
    rv['message'] = 'user nonce created'

    return Response(rv, status = status.HTTP_200_OK)



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

            message = "\nBy signing this message, you will sign the randomly generated nonce. This will help complete your registration to the platform. \n\nNonce: " + saved_nonce + " \n\nWallet Address: " + user_pk_address
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



# TODO: protect-view with login/auth
def launch_token_form(request): # TODO: ensure proper file-validation is done on server-side
  
  max_file_size = 100
  accepted_content_types = [
    'model/gltf-binary', 'image/gif', 'image/jpeg', 'image/png',
    'image/svg+xml', 'image/webp', 'model/gltf-binary'
  ]

  if request.method == 'POST':
    print(request.POST, request.FILES)
    uploaded_file = request.FILES['nft_image_upload']
    upload_file_mb_size = uploaded_file.size / 1024 / 1024

    content_type = magic.from_buffer(uploaded_file.read(), mime=True) # verifies the uploaded file

    if content_type in accepted_content_types and upload_file_mb_size <= max_file_size:
      nft_name = request.POST['token_name']
      nft_price = request.POST['token_price_field']
      nft_total_supply = request.POST['nft_total_supply']


      # user_nft_obj = UserNft.objects.create(
      #   nft_name=nft_name,
      #   nft_price=nft_price,
      #   nft_total_supply=nft_total_supply,
      #   nft_media_file=uploaded_file
      # )
      # user_nft_obj.save()
      
      # print(nft_name, nft_price, nft_total_supply)
      
  return render(request, 'launch_token_form.html')

  

def deploy_new_nft(request):
  if request.method == "POST":
    pass








 