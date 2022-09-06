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
  password = None

  objects = UserManager()

  USERNAME_FIELD = 'user_pk_address'
  REQUIRED_FIELDS = []


class UserNonce(models.Model):
  nonce = models.CharField(max_length=100)
  user = models.ForeignKey(Web3User, on_delete=models.CASCADE)


class CreatorProfile(models.Model):
  user = models.ForeignKey(Web3User, on_delete=models.CASCADE)
  creator_name = models.CharField(max_length=2000, blank=True, null=True)
  creator_website = models.URLField(blank=True, null=True)
  creator_contact_info = models.CharField(max_length=2000, blank=True, null=True)


# TODO: add creator foreign-key (user FK is not necessary here)
class UserProject(models.Model):
  title = models.CharField(max_length=2000)
  description = models.TextField()
  project_website = models.URLField(blank=True, null=True)
  github_webite = models.URLField(blank=True, null=True)
  discord_website = models.URLField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


# TODO: add creator foreign-key (user FK is not necessary here)
class ProjectNftImage(models.Model):
  project_obj = models.ForeignKey(UserProject, on_delete=models.CASCADE)
  nft_image = models.ImageField(upload_to='nft_images/', verbose_name='Image')




