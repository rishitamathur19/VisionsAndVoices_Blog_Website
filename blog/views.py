from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm, PostForm, CommentForm
from .models import Profile, Post, Comment
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.http import JsonResponse

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def index(request):
    profile = Profile.objects.get(user=request.user)
    posts = Post.objects.all()[:4]    
    return render(request, 'index.html', {'posts': posts, 'profile': profile})

@login_required
def explore(request):
    most_popular_posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:3]
    recent_posts = Post.objects.all().order_by('-created_at')
    users = Profile.objects.all()
    profile = Profile.objects.get(user=request.user)

    context = {
        'most_popular_posts': most_popular_posts,
        'recent_posts': recent_posts,
        'users': users,
        'profile': profile
    }

    return render(request, 'explore.html', context)

def blog(request, id=None):
    profile = Profile.objects.get(user=request.user)
    if id:
        post = get_object_or_404(Post, id=id)
        related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:3]
        recent_posts = Post.objects.all().order_by('-created_at')[:3]
        
        comments = post.comments.all()
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user 
                comment.post = post 
                comment.save()
                return redirect('blog_detail', id=post.id)
        else:
            form = CommentForm()

        return render(request, 'blog.html', {
            'post': post,
            'profile': profile,
            'related_posts': related_posts,
            'recent_posts': recent_posts,
            'comments': comments,
            'form': form,
        })

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'posts': posts, 'profile': profile})

@login_required
def about(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'about.html', {'profile': profile})

@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile, created = Profile.objects.get_or_create(user=request.user)
    posts = Post.objects.filter(user=user).order_by('-created_at')

    saved_posts = Post.objects.filter(saved_by=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('profile')
        elif 'create_post' in request.POST:
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                post = post_form.save(commit=False)
                post.user = request.user 
                post.save()
                return redirect('profile')
        elif 'edit_post' in request.POST:
            post_id = request.POST.get('edit_post_id')   
            post = get_object_or_404(Post, id=post_id, user=request.user)
            post_form = PostForm(request.POST, request.FILES, instance=post)
            if post_form.is_valid():
                post_form.save()
                return redirect('profile')

    else:
        form = ProfileForm(instance=profile)
        post_form = PostForm()

    for post in posts:
        post.is_bookmarked = post.is_bookmarked(user)

    return render(request, 'profile.html', {'form': form, 'profile': profile, 'post_form': post_form, 'posts': posts, 'saved_posts': saved_posts, 'user': user})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # ENSURE THE USER IS LOGGED IN BEFORE LIKING THE POST
    if request.user.is_authenticated:
        post.like(request.user)  # ADDING USER TO LIKES
        return JsonResponse({'status': 'liked', 'like_count': post.like_count})
    else:
        return JsonResponse({'status': 'error', 'message': 'You need to be logged in to like posts.'})

@login_required
def unlike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # ENSURE THE USER IS LOGGED IN BEFORE UNLIKING THE POST
    if request.user.is_authenticated:
        post.unlike(request.user)  # REMOVING USER FROM LIKES
        return JsonResponse({'status': 'unliked', 'like_count': post.like_count})
    else:
        return JsonResponse({'status': 'error', 'message': 'You need to be logged in to unlike posts.'})

@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # ADD THE USER TO THE SAVED_BY FIELD TO BOOKMARK
        post.saved_by.add(request.user)
        return JsonResponse({'status': 'bookmarked'})

@login_required
def unbookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # Remove THE USER FROM THE SAVED_BY FIELD TO UNBOOKMARK
        post.saved_by.remove(request.user)
        return JsonResponse({'status': 'unbookmarked'})