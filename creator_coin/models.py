from email.policy import default
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.utils import timezone




class UserManager(BaseUserManager):

  def create_user(self, pk_address):
    if pk_address is None:
      raise TypeError('Users must have a public key address.')

    user = self.model(user_pk_address=pk_address)
    user.save()

    return user

  def create_superuser(self, pk_address):
    user = self.create_user(pk_address)
    user.is_superuser = True
    user.save()

    return user


class Web3User(AbstractBaseUser):
  user_pk_address = models.CharField(max_length=100, unique=True)
  is_superuser = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  github_verified = models.BooleanField(default=False)

  password = None

  objects = UserManager()

  USERNAME_FIELD = 'user_pk_address'
  REQUIRED_FIELDS = []


class UserNonce(models.Model):
  nonce = models.CharField(max_length=100)
  user = models.ForeignKey(Web3User, on_delete=models.CASCADE)


class CreatorProfile(models.Model):
  # user_obj = models.ForeignKey(Web3User, on_delete=models.CASCADE)
  user_obj = models.OneToOneField(Web3User, on_delete=models.CASCADE)
  creator_name = models.CharField(max_length=2000, blank=True, null=True)
  creator_email = models.CharField(max_length=255, blank=True, null=True)
  creator_personal_website = models.URLField(blank=True, null=True)
  creator_github_website = models.URLField(blank=True, null=True)
  creator_discord_website = models.URLField(blank=True, null=True)
  creator_description = models.TextField(blank=True, null=True)
  # creator_contact_info = models.CharField(max_length=2000, blank=True, null=True)
  updated_at = models.DateTimeField(auto_now=True)


class CreatorProjectLog(models.Model):
  creator_obj = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
  log_title = models.CharField(max_length=2000, blank=True, null=True)
  log_description = models.TextField(blank=True, null=True)
  log_created_date = models.DateTimeField(auto_now_add=True)



# class UserToken(models.Model):
#   user_obj = models.ForeignKey(Web3User, on_delete=models.CASCADE)
#   token_name = models.CharField(max_length=2000, blank=True, null=True)
#   token_symbol = models.CharField(max_length=100, blank=True, null=True)
#   token_image = models.ImageField(upload_to='token_images/', verbose_name='Image')
#   created_at = models.DateTimeField(auto_now_add=True)
#   # updated_at = models.DateTimeField(auto_now=True)

class UserNft(models.Model):
  creator_obj = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
  nft_name = models.CharField(max_length=2000, blank=True, null=True)
  nft_symbol = models.CharField(max_length=3, blank=True, null=True)
  nft_price = models.FloatField()
  nft_total_supply = models.IntegerField()
  nft_media_file = models.FileField()
  nft_created_date = models.DateTimeField(auto_now_add=True)
  nft_updated_at = models.DateTimeField(auto_now=True)
  nft_ipfs_url = models.CharField(max_length=2000, blank=True, null=True)

  # nft_deployed_date = models.DateTimeField(auto_now_add=True, blank=True, null=True) # TODO: remove the null/blank=True after reseting DB
  nft_deployed = models.BooleanField(default=False)
  nft_deployed_contract_address = models.CharField(max_length=2000, blank=True, null=True)
  nft_deployed_transaction_hash = models.CharField(max_length=2000, blank=True, null=True)
  nft_deployed_contract_data = models.CharField(max_length=2000, blank=True, null=True)
  nft_deployed_nonce = models.IntegerField(default=-1)
  nft_deployed_chain_id = models.IntegerField(default=-1)


# All purchases will be recorded here
  # after, can add transfers, etc. as well 
# TODO: update this table with etherscan api
class UserNftTransactionHistory(models.Model):
  nft_obj = models.ForeignKey(UserNft, on_delete=models.CASCADE)
  transaction_hash = models.CharField(max_length=2000, blank=True, null=True)
  transaction_created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True) # TODO: remove the null/blank=True after reseting DB


# Displays the nft's user bought
# TODO: update this table with etherscan api
class UserNftCollection(models.Model):
  creator_obj = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
  # nft_obj = models.ForeignKey(UserNft, on_delete=models.CASCADE)
  nft_transaction_history_obj = models.ForeignKey(UserNftTransactionHistory, on_delete=models.CASCADE, blank=True, null=True)
  transaction_created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True) # TODO: remove the null/blank=True after reseting DB

 
# class UserNftTotalSupply(models.Model):
#   nft_obj = models.ForeignKey(UserNft, on_delete=models.CASCADE)
#   total_sold = models.IntegerField()


class GithubProfile(models.Model):
  user_obj = models.ForeignKey(Web3User, on_delete=models.CASCADE)
  github_username = models.CharField(max_length=2000)
  github_profile_url = models.URLField() 
  github_avatar_url = models.URLField()
  # verified_date = models.DateTimeField(auto_now_add=True)  # TODO: add


# class UserProject(models.Model):
#   creator_profile = models.ForeignKey(CreatorProfile, on_delete=models.CASCADE)
#   title = models.CharField(max_length=2000)
#   description = models.TextField()
#   project_website = models.URLField(blank=True, null=True)
#   github_webite = models.URLField(blank=True, null=True)
#   discord_website = models.URLField(blank=True, null=True)
#   created_at = models.DateTimeField(auto_now_add=True)
#   updated_at = models.DateTimeField(auto_now=True)


# class ProjectNftImage(models.Model):
#   project_obj = models.ForeignKey(UserProject, on_delete=models.CASCADE)
#   nft_image = models.ImageField(upload_to='nft_images/', verbose_name='Image')



class UserBetaEmails(models.Model):
  """
  Emails saved from the homepage
  """
  user_email = models.EmailField()








 


