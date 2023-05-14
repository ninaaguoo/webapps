"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.global_action, name='global'),
    # path('global/', views.global_action, name='global'),
    path('login/', views.login_action, name='login'),
    path('register/', views.register_action, name='register'),
    path('logout/', views.logout_action, name='logout'),
    path('follower/', views.follower_action, name='follower'),
    path('profile/', views.profile_action, name='profile'),
    path('otherprofile/<int:id>/', views.otherprofile_action, name='otherprofile'),
    # path('global/', views.add_post, name='global'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('otherprofile/<int:user_id>/', views.follow, name='follow'),  
    path('otherprofile/<int:user_id>/', views.unfollow, name='unfollow'),
    path('socialnetwork/get-global', views.get_list_json_dumps_serializer, name='get-global'),
    path('socialnetwork/get-follower', views.get_list_json_dumps_serializer_follower, name='get-follower'),
    path('socialnetwork/add-item', views.add_item, name='ajax-add-item'),
    path('socialnetwork/add-comment', views.add_comment, name='ajax-add-comment')
]
