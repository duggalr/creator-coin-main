from django.urls import path
from . import views


urlpatterns = [
  path('', views.home, name='home'),
  path('project-page/<int:project_id>', views.project_page, name='project_page'),
  path('explore', views.explore_project, name='explore_project'),
  path('create-project', views.create_project, name='create_project'),
  path('edit-project/<int:project_id>', views.edit_project, name='edit_project'),

  path('user_profile', views.user_profile, name='user_profile'),
  path('logout', views.logout_view, name='logout'),

  path('nft_page_example', views.nft_page_example, name='nft_page_example'),

  path('generate_nonce', views.UserNonceView.as_view(), name='user_nounce_view'),
  path('login', views.LoginView.as_view(), name='user_login_view'),
  
]




