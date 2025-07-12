from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('',  views.index, name="index"),
    path('blog/',  views.blog, name="blog"),
    path('blog/<int:id>/', views.blog, name="blog_detail"),
    path('explore/',  views.explore, name="explore"),
    path('about/',  views.about, name="about"),
    path('profile/',  views.profile, name="profile"),
    path('profile/<str:username>/', views.profile, name='user_profile'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/unlike/', views.unlike_post, name='unlike_post'),
    path('post/<int:post_id>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('post/<int:post_id>/unbookmark/', views.unbookmark_post, name='unbookmark_post'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)