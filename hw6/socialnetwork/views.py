from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, Http404

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm, PostForm
from socialnetwork.models import Post, Profile, Comment

import json

@login_required
def add_post(request):
    context = {}
    new_item = Post(user=request.user, text=request.POST['text'], creation_time=timezone.now())
    form = PostForm(request.POST, instance=new_item)
    if not form.is_valid():
        context['form'] = form
    else:
        # Must copy content_type into a new model field because the model
        # FileField will not store this in the database.  (The uploaded file
        # is actually a different object than what's return from a DB read.)
        context['form'] = PostForm()
    new_item.save()
    context['posts'] = Post.objects.all().order_by("-creation_time")
    return render(request, 'socialnetwork/global.html', context)

@login_required
def global_action(request):
    if request.method == "GET":
        return render(request, 'socialnetwork/global.html', { 'posts': Post.objects.all().order_by("-creation_time") })
    
    if 'text' not in request.POST or not request.POST['text']:
        #deal with error
        print("error")
        return render(request, 'socialnetwork/global.html', { 'posts': Post.objects.all().order_by("-creation_time") })
    
    new_post = Post(text=request.POST['text'], user=request.user, creation_time=timezone.now())
    new_post.save()
    return render(request, 'socialnetwork/global.html', { 'posts': Post.objects.all().order_by("-creation_time") })

@login_required
def follower_action(request):
    context = {'posts': []}
    for post in Post.objects.all():
        if post.user in request.user.profile.following.all():
            context['posts'].append(post)
    context['posts'].reverse() 
    return render(request, 'socialnetwork/follower.html', context)    

@login_required
def profile_action(request):
    context = {}
    if request.method == 'GET':
        context = {'profile': request.user.profile,
                   'form': ProfileForm(initial={'bio': request.user.profile.bio})}
        return render(request, 'socialnetwork/profile.html', context)
    
    #POST request means update
    form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
    if not form.is_valid():
        print("no")
        context = {'profile':request.user.profile, 'form': form}
        return render(request, 'socialnetwork/profile.html', context)
    
    profile = request.user.profile
    profile.bio = form.cleaned_data['bio']
    profile.picture = form.cleaned_data['picture']
    profile.content_type = form.cleaned_data['picture'].content_type
    profile.save()
    form.save()

    context = {'profile': request.user.profile,
                'form': ProfileForm(initial={'bio': request.user.profile.bio})}
    
    return render(request, 'socialnetwork/profile.html', context)

@login_required
def otherprofile_action(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == "GET":
        return render(request, 'socialnetwork/otherprofile.html', {'profile': user.profile})
    #breakpoint()
    if (user in request.user.profile.following.all()):
        return unfollow(request, user_id=id)
    else:
        return follow(request, user_id=id)

# Create your views here.
def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('global'))

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    new_user.profile = Profile(user=new_user)
    new_user.profile.save()

    login(request, new_user)
    return redirect(reverse('global'))

@login_required
def unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return render(request, 'socialnetwork/otherprofile.html', {'profile': user_to_unfollow.profile})

@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return render(request, 'socialnetwork/otherprofile.html', {'profile': user_to_follow.profile})

@login_required
def get_photo(request, id):
    item = get_object_or_404(Profile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, item.picture, type(item.picture)))

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)

def get_list_json_dumps_serializer(request):
    # To make quiz11 easier, we permit reading the list without logging in. :-)
    if not request.user.is_authenticated:
       return _my_json_error_response("User must be logged in.", status=401)
    
    posts = Post.objects.order_by("creation_time")
    comments = Comment.objects.order_by("creation_time")
    return serialHelper(posts, comments)

    # To make quiz11 work, we need to allow cross-origin access.
    # Normally, we would just return the HTTPResponse (as shown above and in all the functions in this example).
    # But to make quiz11 work, we need to set the 'Access-Control-Allow-Origin' header in the response,
    # so in the version of this example deployed on www.cmu-webapps.org, the lines below are uncommented
    # (and the return statement above is commented out).

    # response = HttpResponse(response_json, content_type='application/json')
    # response['Access-Control-Allow-Origin'] = '*'
    # return response

def get_list_json_dumps_serializer_follower(request):
    # To make quiz11 easier, we permit reading the list without logging in. :-)
    # if not request.user.is_authenticated:
    #     return _my_json_error_response("You must be logged in to do this operation", status=403)
    posts = []
    comments = []
    for post in Post.objects.all():
        profile = Profile.objects.get(id=request.user.id)
        if post.user in profile.following.all():
            posts.append(post)
            for comment in Comment.objects.all():
                if comment.post == post:
                    comments.append(comment)

    return serialHelper(posts, comments)

def serialHelper(posts, comments):
    response_data = {'Posts': [],
                     'Comments': []}
    for model_item in posts:
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'user_id':model_item.user.id,
            'first_name': model_item.user.first_name,
            'last_name': model_item.user.last_name,
            'creation_time': str(model_item.creation_time)
        }
        response_data['Posts'].append(my_item)

    #unshifted tab for comment loop
    
    for comment_item in comments:
        cmt_item = {
            'id':comment_item.id,
            'text':comment_item.text,
            'user_id': comment_item.creator.id,
            'first_name': comment_item.creator.first_name,
            'last_name': comment_item.creator.last_name,
            'creation_time': str(comment_item.creation_time),
            'post_id': comment_item.post.id
        }
        response_data['Comments'].append(cmt_item)
    
    response_json = json.dumps(response_data)

    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

#add error codes
def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

def add_item(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    
    if not 'item' in request.POST or not request.POST['item']:
        return _my_json_error_response("You must enter an item to add.", status=400)

    new_item = Post(text=request.POST['item'], user=request.user, creation_time=timezone.now())
    new_item.save()

    return get_list_json_dumps_serializer(request)
    #return redirect(reverse('global'))

def add_comment(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    
    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter an item to add.", status=400)
    
    if not 'post_id' in request.POST or not request.POST['post_id'] or not request.POST['post_id'].isnumeric():
        return _my_json_error_response("missing or wrong post id", status=400)

    if not Post.objects.filter(id=int(request.POST['post_id'])).exists():
        return _my_json_error_response("missing or wrong post id", status=400)
    
    new_item = Comment(text=request.POST['comment_text'], creator=request.user, creation_time=timezone.now(), post=Post.objects.get(id=request.POST['post_id']))
    new_item.save()

    # if request.POST['stream'] == 'global':
    return serialHelper(posts=[], comments=[new_item])
    # else:
    #return get_list_json_dumps_serializer_follower(request)
    # return redirect(reverse('global'))
    # response_data = {'Comments': []}
    # cmt_item = {
    #     'id':new_item.id,
    #     'text':new_item.text,
    #     'user_id': new_item.creator.id,
    #     'first_name': new_item.creator.first_name,
    #     'last_name': new_item.creator.last_name,
    #     'creation_time': str(new_item.creation_time),
    #     'post_id': new_item.post.id
    # }
    # response_data['Comments'].append(cmt_item)
    # return json.dumps(response_data)