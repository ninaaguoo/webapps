from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, Http404

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from matchbti.forms import (
    LoginForm, RegisterForm, AgeForm, GenderForm, EthnicityForm, HeightForm, SexualityForm, 
    PreferencesForm, MBTIForm, ReligionForm, SchoolForm, WorkForm, NewPicForm, BioForm,
    ProfileForm)


from matchbti.models import Profile, Message

import json

from social_django.views import auth
from math import radians, cos, sin, asin, sqrt

def my_auth_action(request):
    redirect_uri = "http://localhost:8000/oauth/complete/google-oauth2/"
    return redirect(auth(request, "google-oauth2", redirect_uri=redirect_uri))

def profile_exists(action_function):
    def my_wrapper_function(request, *args, **kwargs):
        try:
            request.user.profile
            return action_function(request, *args, **kwargs)
        except:
            request.user.profile = Profile(user=request.user,
                                           first_name=request.user.first_name,
                                           last_name=request.user.last_name)
            request.user.profile.save()

    return my_wrapper_function 

def profile_complete(action_function):
    def my_wrapper_function(request, *args, **kwargs):
            for field in ['age', 'gender', 'ethnicity', 'height', 'mbti', 'preferences', 
                          'religion', 'school', 'sexuality', 'work', 'picture', 'bio', 'latitude', 'longitude']:
                        if getattr(request.user.profile, field)== '' or getattr(request.user.profile, field) == None or getattr(request.user.profile, field) == []:
                            if field == "latitude" or field == "longitude":
                                return redirect(reverse('geolocation'))
                            else:
                                return redirect(reverse('question', args=(field,)))
            return action_function(request, *args, **kwargs)
    return my_wrapper_function  


@login_required
@profile_exists
@profile_complete
#make sure theyd di profile decorator after oauth
def global_action(request):
    if request.method == "GET":
        return render(request, 'global.html', { 'items': Profile.objects.all()})
    
    new_profile = Profile(bio=request.POST['bio'], user=request.user)
    new_profile.save()
    return render(request, 'global.html', { 'items': Profile.objects.all()})

@login_required
@profile_exists
@profile_complete
def matches_action(request):
    if request.method == "GET":
        return render(request, 'matches.html', { 'matches': request.user.profile.matches.all()})

    return render(request, 'matches.html', { 'matches': request.user.profile.matches.all()})
 

@login_required
@profile_exists
@profile_complete
def profile_action(request):
    context = {}
    profile = request.user.profile
    if request.method == 'GET':
        form = ProfileForm(instance=profile)
        context = {'profile': profile, 'form': form}
        return render(request, 'profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES, instance=profile)
    if not form.is_valid():
        context = {'profile': profile, 'form': form}
        return render(request, 'profile.html', context)
    
    profile = request.user.profile
    profile.id = profile.id
    profile.first_name = profile.first_name
    profile.bio = form.cleaned_data['bio']
    profile.age = profile.age
    profile.picture = form.cleaned_data['picture']
    profile.content_type = form.cleaned_data['picture'].content_type
    profile.save()
    form.save()

    context = {'profile': request.user.profile,
                'form': ProfileForm(instance=profile)}
    
    return render(request, 'profile.html', context)

# Create your views here.
def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('global'))

@login_required
@profile_exists
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    new_user.profile = Profile(user=new_user, 
                               first_name=new_user.first_name,
                               last_name=new_user.last_name,)
    new_user.profile.save()

    login(request, new_user)
    return redirect(reverse('question', args=('age',)))

@login_required
@profile_exists
@profile_complete
def dislike(request):
    user_to_dislike = get_object_or_404(User, id=request.POST['id'])
    request.user.profile.dislikes.add(user_to_dislike)
    request.user.profile.discoverable.remove(user_to_dislike)
    request.user.profile.save()
    #should switch to next profile 
    return get_list_json_dumps_serializer_mbti(request)

@login_required
@profile_exists
@profile_complete
def like(request):
    user_to_like = get_object_or_404(User, id=request.POST['id'])
    curr_user = request.user
    curr_user.profile.likes.add(user_to_like)
    curr_user.profile.discoverable.remove(user_to_like)
    #matched
    if curr_user in user_to_like.profile.likes.all():
        curr_user.profile.matches.add(user_to_like)
        user_to_like.profile.matches.add(curr_user)

    user_to_like.profile.save()
    curr_user.profile.save()
    return get_list_json_dumps_serializer_mbti(request)

#start chat with user with user_id
@login_required
@profile_exists
@profile_complete
def chat_action(request, id):
    true_match = False
    real_user = False
    for user in User.objects.all():
        if user.profile.id == id:
            real_user = True
    if real_user == False:
        return _my_json_error_response("You can not chat with a non-user", status=403)
    if request.user.profile.id == id:
        return _my_json_error_response("You can not chat with yourself", status=403)
    for match in request.user.profile.matches.all():
        if match.profile.id == id:
            true_match = True
    if true_match == False:
        return _my_json_error_response("You can not chat with someone who is not a match", status=403)
    user_mbti = request.user.profile.mbti
    receiver = get_object_or_404(User, id=id)
    receiver_mbti = receiver.profile.mbti
    text = "You have matched with " + receiver.first_name + " " + receiver.last_name + " who is an " + receiver_mbti + "! "

    #check E or I
    if user_mbti[0] == receiver_mbti[0]:
        if user_mbti[0] == "E":
            text += """You are both extroverted. Two extroverts tend to have highly energetic relationships, 
                     always having flowing discussions with their shared passion for companionship. """
        else:
            text += """You are both introverted, both appreciate their space and solitude and will often allow 
                        their partner to have similar space without feeling pressure to speak or spend time with others. """
    else:
        text += """Extroverts will often be drawn to the relaxed and nonchalant attitude of their introverted counterparts, 
                    and similarly, introverts see extroverts as enjoyable to be around and fairly engaging, finding it admirable 
                    that someone can be so comfortable with other people. This creates a delicate balance where each person 
                    finds pleasure in the other's company, whereas they are not competing for one another's attention. """
    
    #check N or S
    if user_mbti[1] == receiver_mbti[1]:
        if user_mbti[1] == "N":
            text += """Intuitive Types enjoy spirited conversation and exchanging opinions and ideas, and they tend to understand what 
                    is truly implied by cryptic or less-than-honest discussion. Couples with two Intuitive Types tend to get along because 
                    they both respect and understand the other’s tendency to live in their own heads and their desire for excitement and novelty. """
        else:
            text += """Two Sensing Types, the couple is (together and separately) incredibly logical, taking information as it is, and living 
                    in the present as opposed to spending the present moment worrying about other things—namely underlying meanings that others
                    may think of. """
    else:
        text += """The Sensing Type admires the creativity and inventive nature of the Intuitive Type, while at times, the Intuitive Type 
                    finds the Sensing Type to be a refreshing, down-to-earth alternative to their more abstract mindset. MBTI Intuitive 
                    Types enjoy the logical thought processes and present mindfulness of their Sensing Type opposites, which helps them 
                    live more in that moment in reality and less in their heads. """
        
    
    #check F or T
    if user_mbti[2] == receiver_mbti[2]:
        if user_mbti[2] == "F":
            text += """Feeler relationships are often intimate and affectionate. They view their partner as someone that they were meant to 
                    connect with, and they want to do everything in their power to show that person that they love and support them. """
        else:
            text += """A relationship featuring two individuals who share the MBTI Thinking Preference is often manageable, 
                    with both individuals enjoying logical discussion. Even if they share conflicting views with the other person, 
                    they still tend to enjoy the topic of conversation. They state their opinion and accept their partner's opinions without
                    feeling the need to engage in a power struggle or an all-out argument. """
    else:
        text += """Thinking Types are attracted to Feeling Types inherently encouraging and nurturing persona, being more inclined to open
                 up and become more empathetic. On a similar note, Feelers will also appreciate a Thinker's ability to help them alter their 
                 views and allow for a more objective view when it is necessary, which can help the Feeler learn to control their emotions and
                 better understand others' intentions. """
    
    #check P or J
    if user_mbti[3] == receiver_mbti[3]:
        if user_mbti[3] == "P":
            text += """Two Perceivers who enter in a relationship have a mutual respect for their partner's desire for space and liberty to do as
                    they wish, without the pressures of strict boundaries or schedules. They thoroughly enjoy spending time with one another, doing 
                    anything that pleases them at that moment. """
        else:
            text += """A relationship formed of two Judging Types is one that requires less proactive preference understanding, as each 
                    person ultimately appreciates his or her partner's desire for order, neatness, and structure, whether in their home or in their work
                    and life schedules. They are often very committed to their partner and resolve conflict as soon as it arises in order to keep their 
                    relationship strong. """
    else:
        text += """Judging Types are often made up of individuals that enjoy quick resolutions, quick turnarounds, and are quick decision-makers. 
                    When in public and at work, Judging Types are often seen as highly regimented and organized, while being a bit more flexible 
                    during their personal time. Those with the Perceiving Type Preference, on the other hand, are often drawn to the flexible and 
                    spontaneous part of life, and tend to experience stress when structure and order are forced upon them, or when they are asked to
                    make quick choices without ample time to weigh each option. In fights, Judging Types will hide their regimented tendencies and try 
                    their hand at being more flexible, and Perceiving Types will reign in their spontaneity and try to appear more organized. """


    return render(request, 'chat.html', {'messages': Message.objects.all(), 
                                             'user_id': request.user.id,
                                             'receiver_id': id,
                                             'first_name': receiver.first_name,
                                             'last_name': receiver.last_name,
                                             'prompt': text})
    # return redirect(reverse('chat'))
    

@login_required
@profile_exists
@profile_complete
def unmatch_action(request):
    user_to_unmatch = get_object_or_404(User, id=request.POST['id'])
    request.user.profile.matches.remove(user_to_unmatch)
    request.user.profile.likes.remove(user_to_unmatch)
    request.user.profile.dislikes.add(user_to_unmatch)
    user_to_unmatch.profile.matches.remove(request.user)
    user_to_unmatch.profile.likes.remove(request.user)
    user_to_unmatch.profile.dislikes.add(request.user)
    request.user.profile.save()
    user_to_unmatch.profile.save()
    return get_list_json_dumps_serializer_matches(request)

@login_required
@profile_exists
@profile_complete
def get_photo(request, id):
    profile = get_object_or_404(Profile, id=id)

    if not profile.picture:
        raise Http404

    return HttpResponse(profile.picture, content_type=profile.content_type)

@login_required
@profile_exists
@profile_complete
def add_message(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    
    if not 'item' in request.POST or not request.POST['item']:
        return _my_json_error_response("You must enter a message to add.", status=400)
    
    
    receiver = get_object_or_404(User, id=request.POST['receiver_id'])
    new_item = Message(text=request.POST['item'], receiver=receiver, user=request.user, creation_time=timezone.now())
    new_item.save()
    return get_list_json_dumps_serializer_messages(request, receiver.id)

def get_list_json_dumps_serializer_messages(request, receiver_id):
    # response_data = {'user_messages': [],
    #                  'receiver_messages': []}
    response_data = []
    receiver = get_object_or_404(User, id=receiver_id)
    for message in Message.objects.filter(user=request.user, receiver=receiver).order_by("creation_time"):
        #breakpoint()
        message_item = {
            'id': message.id,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'text': message.text,
            'creation_time': str(message.creation_time),
            'curr_user': True
        
        }
        response_data.append(message_item)
    for message in Message.objects.filter(user=receiver, receiver=request.user).order_by("creation_time"):
        message_item = {
            'id': message.id,
            'first_name': receiver.first_name,
            'last_name': receiver.last_name,
            'text': message.text,
            'creation_time': str(message.creation_time),
            'curr_user': False
        }
        response_data.append(message_item)
    response_data.sort(key=lambda x:x['creation_time'])
    response_json = json.dumps(response_data)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

def get_list_json_dumps_serializer_matches(request):
    response_data = []
    for user in request.user.profile.matches.all():
        curr_user = User.objects.filter(id=user.profile.id)
        matches_item = {
            'id': user.profile.id,
            'user_id':user.profile.user_id,
            'first_name': curr_user[0].first_name,
            'last_name': curr_user[0].last_name,
            'age': user.profile.age,
            'mbti': user.profile.mbti,
            'gender': user.profile.gender,
            'ethnicity': user.profile.ethnicity,
            'sexuality': user.profile.sexuality,
            'school': user.profile.school,
            'work': user.profile.work,
            'religion': user.profile.religion,
            'bio': user.profile.bio,
        }
        response_data.append(matches_item)
    response_json = json.dumps(response_data)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

def get_list_json_dumps_serializer_mbti(request):
    if not request.user.is_authenticated:
       return _my_json_error_response("User must be logged in.", status=401)
    response_data = []
    update_discoverable(request)
    for user in request.user.profile.discoverable.all():
        curr_user = User.objects.filter(id=user.profile.id)
        compatible_user = {
            'id': user.profile.id,
            'user_id':user.profile.user_id,
            'first_name': curr_user[0].first_name,
            'last_name': curr_user[0].last_name,
            'age': user.profile.age,
            'mbti': user.profile.mbti,
            'gender': user.profile.gender,
            'ethnicity': user.profile.ethnicity,
            'sexuality': user.profile.sexuality,
            'school': user.profile.school,
            'work': user.profile.work,
            'religion': user.profile.religion,
            'height': user.profile.height,
            'heightInches': user.profile.heightInches,
            'bio': user.profile.bio,
        }
        response_data.append(compatible_user)

    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

@login_required
@profile_exists
def question_func(request, field):
    form_dict = {'age': AgeForm, 
                 'gender': GenderForm,
                 'ethnicity': EthnicityForm,
                 'height': HeightForm,
                 'mbti': MBTIForm,
                 'preferences': PreferencesForm,
                 'religion': ReligionForm,
                 'school': SchoolForm,
                 'sexuality': SexualityForm,
                 'work': WorkForm,
                 'picture': NewPicForm,
                 'bio': BioForm}
    if not hasattr(request.user.profile, field):
        return redirect(reverse('global'))
    if getattr(request.user.profile, field) != '' and getattr(request.user.profile, field) != None and getattr(request.user.profile, field) != []:
        return redirect(reverse('global'))

    if request.method == 'GET':
        form = form_dict[field](instance = request.user.profile)
        context = {'profile': request.user.profile, 'form': form}
        html = 'questionnaire/' + str(field) + '.html'
        return render(request, html, context)
    
    if field == "picture":
        form = form_dict[field](request.POST, request.FILES)
    else:
        form = form_dict[field](request.POST, instance=request.user.profile)
    if not form.is_valid():
        context = {'profile': request.user.profile, 'form': form}
        html = 'questionnaire/' + str(field) + '.html'
        return render(request, context)
    
    if field == "picture":
        pic = form.cleaned_data["picture"]
        request.user.profile.picture = pic
        if pic and request.user.profile.content_type.startswith("image"):
            request.user.profile.content_type = pic.content_type

    request.user.profile.save()
    context = {}
    context['profile'] = request.user.profile

    if field == "picture":
        context['form'] = NewPicForm(initial={"picture": pic})
    else:
        context['form'] = form
    
    return redirect(reverse('global'))


@login_required
@profile_exists
def get_geolocation(request):
    if request.method == "GET":
        context = {}
        return render(request, 'questionnaire/geolocation.html', context)
        
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    request.user.profile.latitude = latitude
    request.user.profile.longitude = longitude
    request.user.profile.save()
            
    response_data = {"latitide": latitude, "longitude": longitude}
    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')

@login_required
def update_discoverable(request):
    user = request.user
    user.profile.discoverable.clear
    for otherUser in User.objects.all():#filter(mbti=mbti).values():
        #make sure doesn't show self
        if (user.profile.id != otherUser.profile.id and
            isPrefer(user, otherUser) and isPrefer(otherUser, user) and
            isNearby(user, otherUser) and
            otherUser not in user.profile.likes.all() and otherUser not in user.profile.dislikes.all() and
            otherUser not in user.profile.matches.all()):
            user.profile.discoverable.add(otherUser)
            user.profile.save()
            if (user not in otherUser.profile.likes.all() and user not in otherUser.profile.dislikes.all() and
            user not in otherUser.profile.matches.all()):
                otherUser.profile.discoverable.add(user)
                otherUser.profile.save()

def isNearby(user1, user2):
    lat1 = float(user1.profile.latitude)
    long1 = float(user1.profile.longitude)
    lat2 = float(user2.profile.latitude)
    long2 = float(user2.profile.longitude)

    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])

    # use Haversine formula to calculate difference in distances
    dLat = lat2 - lat1
    dLong = long2 - long1
    a = sin(dLat/2)**2 + cos(lat1) * cos(lat2) * sin(dLong/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956  #radius of earth in miles
    return (c*r < 30)

def isPrefer(user1, user2):
    if (user1.profile.gender == "Man"):
        return ("Men" in user2.profile.preferences or "Everyone" in user2.profile.preferences)
    elif (user1.profile.gender == "Woman"):
        return ("Women" in user2.profile.preferences or "Everyone" in user2.profile.preferences)
    return ("Nonbinary" in user2.profile.preferences or "Everyone" in user2.profile.preferences)

@login_required
@profile_exists
def edit_profile(request, id):
    my_instance = User.objects.get(id=id)
    if request.method == 'POST':
        form = User(request.POST, request.FILES, instance=my_instance)
        if form.is_valid():
            form.save()
            # redirect to success page or do something else
    else:
        form = User(instance=my_instance)
    return render(request, 'profile.html', {'form': form})