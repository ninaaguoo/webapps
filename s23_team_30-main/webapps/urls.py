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
from django.urls import path, include
from matchbti import views

urlpatterns = [
    path('', views.global_action, name='global'),
    path('login/', views.login_action, name='login'),
    path('register/', views.register_action, name='register'),
    path('matches/', views.matches_action, name='matches'),
    path('logout/', views.logout_action, name='logout'),
    path('profile/', views.profile_action, name='profile'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('chat/<int:id>', views.chat_action, name='chat'),  
    path('unmatch/', views.unmatch_action, name='unmatch'),  
    path('matchbti/add_message', views.add_message, name='ajax-add-message'),  
    path('matchbti/get-global', views.get_list_json_dumps_serializer_mbti, name='get-global'),
    path('matchbti/get-matches', views.get_list_json_dumps_serializer_matches, name='get-matches'),
    path('matchbti/get-messages/<int:receiver_id>', views.get_list_json_dumps_serializer_messages, name='get-messages'),
    path('matchbti/like', views.like, name='like'),
    path('matchbti/dislike', views.dislike, name='dislike'),
    path('question/<str:field>', views.question_func, name='question'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('geolocation', views.get_geolocation, name='geolocation')
]
