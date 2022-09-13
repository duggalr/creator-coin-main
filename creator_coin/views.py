from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
# from rest_framework.authtoken.models import Token

from .models import UserNonce, Web3User, CreatorProfile
from .serializers import Web3UserSerializer

import web3

from web3.auto import w3

from . import utils




# TODO: 
  # add good logging for debugging later on...



def home(request):
  return render(request, 'home_one.html')


# TODO: add slug for project-page-name
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
  all_projects = UserProject.objects.all()
  # nft_images = ProjectNftImage.objects.all()

  rv = []
  for obj in all_projects:
    nft_image_obj = ProjectNftImage.objects.filter(project_obj=obj)
    rv.append({
      'nft_image_object': nft_image_obj
    })
    # rv.append({
    #   'nft_project_image:' nft_image_obj,
    #   'project_object': obj
    # })

  # TODO: 
    # add image and display project's; go from there
    # what happens when a user disconnects an account from CreatorCoin?
  return render(request, 'explore_project.html', {'all_projects': all_projects})



# TODO:
  # make this authenticated 
  # add the user-obj and redirect to project-page 
    # from here, have option for user to mint-NFT for project  (<-- make profile last)
      # on profile, user should see all the project's he has created along with NFT's 




@login_required(login_url='/')
def create_project(request):
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



# TODO: add auth to verify user has access to 
def edit_project(request, project_id):
  # user_project_obj = UserProject.objects.get_object_or_404(id=project_id)  
  user_project_obj = get_object_or_404(UserProject, id=project_id)
  nft_image = ProjectNftImage.objects.get(project_obj=user_project_obj)

  if request.method == "POST":
    print(request.POST)
    nft_image_file = request.FILES.getlist('nft_image')
    if len(nft_image_file) > 0:  # update nft-image for project
      user_project_obj.title = request.POST['project_title']
      user_project_obj.description = request.POST['project_description']
      user_project_obj.project_website = request.POST['project_website']
      user_project_obj.github_webite = request.POST['project_github_website']
      user_project_obj.discord_website = request.POST['project_discord_website']
      user_project_obj.save()
      
      # ProjectNftImage.objects.

  return render(request, 'create_project.html', {'user_project': user_project_obj, 'nft_image': nft_image})




def nft_page_example(request):
  return render(request, 'nft_page_example.html')



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


# TODO:
  # create profile-page and go from there



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
    print('data:', data)

    if 'nonce_signature' in data and 'pk_address' in data:
      user_pk_address = data["pk_address"]
      user_nonce_signature = data["nonce_signature"]

      if Web3User.objects.filter(user_pk_address=user_pk_address).exists():
        user_obj = Web3User.objects.get(user_pk_address=user_pk_address)

        if UserNonce.objects.filter(user=user_obj).exists():
            saved_nonce_obj = UserNonce.objects.get(user=user_obj)
            saved_nonce = saved_nonce_obj.nonce
            # hash_msg = web3.Web3.sha3(text=saved_nonce)
            hash_msg = web3.Web3.sha3(text=saved_nonce)
            # pk2 = w3.eth.account.recover_message(hash_msg, signature=user_nonce_signature)
            recovered_public_key = w3.eth.account.recoverHash(hash_msg, signature=user_nonce_signature)
            # print(f"recovered-has: {pk2} / user-sig: {user_nonce_signature} / user-pk-add: {user_pk_address}")

            if recovered_public_key == user_obj.user_pk_address:
              UserNonce.objects.filter(user=user_obj).delete()
              login(request, user_obj)
              return Response({'success': True, 'message': 'user successfully logged in.'})

          # TODO: 
            # add all error-messages for all cases** (ensure it works well on user-FE-side)

    else:
      pass





 

 