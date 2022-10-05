from django.urls import path
from . import views




urlpatterns = [
  path('', views.home, name='home'),
  path('home_two', views.home_two, name='home_two'),
  path('home_original', views.home_original, name='home_original'),

  path('project-page/<int:project_id>', views.project_page, name='project_page'),  # TODO: delete this and other stuff, related to 'project'

  path('profile/<int:profile_id>', views.user_token_page, name='user_token_page'),
  
  path('explore', views.explore_project, name='explore_project'),

  path('launch_token', views.launch_token_form, name='launch_token_form'),
 
  path('create-profile', views.create_profile, name='create_profile'),
  path('edit-user-profile/<int:profile_id>', views.edit_user_profile, name='edit_user_profile'),

  path('user_profile', views.user_profile, name='user_profile'),
  path('logout', views.logout_view, name='logout'),

  # path('nft_page_example', views.nft_page_example, name='nft_page_example'),

  path('generate_nonce', views.UserNonceView.as_view(), name='user_nounce_view'),
  path('login', views.LoginView.as_view(), name='user_login_view'),


  path('github_login', views.github_login, name='github_login'),
  path('github_callback', views.github_callback, name='github_callback'),


  path('deploy_new_nft', views.deploy_new_nft, name='deploy_new_nft'),
  
  path('mint_new_nft_token', views.mint_new_nft_token, name='mint_new_nft_token'),
  

]



# TODO: 
  # bake the texture and get this to work 
    # need to get exported model ready/complete so can start backend


