from django.urls import path, re_path, reverse_lazy
from django.views.generic import RedirectView

from . import views



urlpatterns = [
  path('', views.home, name='home'),
  # path('home_original', views.home_original, name='home_original'),  # TODO: delete this
  
  path('manifesto/', views.about_page, name='about_page'),
  # re_path(r'^manifesto/$', RedirectView.as_view(url = reverse_lazy('about_page') )),

  path('explore/', views.explore_project, name='explore_project'),
  # re_path(r'^explore/$', RedirectView.as_view(url = reverse_lazy('explore_project') )),

  path('profile/<int:profile_id>/', views.user_token_page, name='user_token_page'),
  # re_path(r'^profile/(?P<profile_id>\d+)/$', RedirectView.as_view(url = reverse_lazy('user_token_page') )),
  
  path('edit-user-profile/<int:profile_id>/', views.edit_user_profile, name='edit_user_profile'),

  path('create-nft/', views.create_token_form, name='create_token_form'),
  # re_path(r'^create-nft/$', RedirectView.as_view(url = reverse_lazy('create_token_form') )),
  path('update-nft/', views.update_token_form, name='update_token_form'),
 
  path('delete-nft/', views.delete_non_minted_nft, name='delete_non_minted_nft'),


  path('fetch-nft-main-data/<int:profile_id>/', views.fetch_nft_main_data, name='fetch_nft_main_data'),
  path('get-nft-metadata/', views.get_minted_nft_metadata, name='get_minted_nft_metadata'),
  path('save-nft-metadata/', views.save_nft_metadata, name='save_nft_metadata'),
  
  path('nft-launch-final/', views.nft_launch_final, name='nft_launch_final'),
  


  path('handle-account-change/', views.handle_account_change, name='handle_account_change'),



  path('create-profile/', views.create_profile, name='create_profile'),
  # re_path(r'^create-profile/$', RedirectView.as_view(url = reverse_lazy('create_profile') )),

  path('my-profile', views.my_profile, name='my_profile'),

  # TODO: correct once this functionality is added... 
  path('deploy_new_nft/', views.deploy_new_nft, name='deploy_new_nft'),  
  path('mint_new_nft_token/<int:profile_id>/', views.mint_new_nft_token, name='mint_new_nft_token'),

  # path('user_profile/', views.user_profile, name='user_profile'),
  path('logout/', views.logout_view, name='logout'),

  path('generate_nonce/', views.UserNonceView.as_view(), name='user_nounce_view'),
  path('login/', views.LoginView.as_view(), name='user_login_view'),

  path('github_login/', views.github_login, name='github_login'),
  path('github_callback/', views.github_callback, name='github_callback'),

  path('verify_user_profile/', views.verify_user_profile, name='verify_user_profile'),


]





