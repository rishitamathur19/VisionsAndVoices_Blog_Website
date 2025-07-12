from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.name 
    
class Post(models.Model):
    CATEGORY_CHOICES = [
        ('Personal Stories & Experiences', 'Personal Stories & Experiences'),
        ('Cultural & Social Commentary', 'Cultural & Social Commentary'),
        ('Futuristic & Visionary Ideas', 'Futuristic & Visionary Ideas'),
        ('Inspiration & Motivation', 'Inspiration & Motivation'),
        ('Philosophical & Deep Thought Pieces', 'Philosophical & Deep Thought Pieces'),
        ('Book Reviews & Recommendations', 'Book Reviews & Recommendations'),
        ('Travel & Cultural Exploration', 'Travel & Cultural Exploration'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def like(self, user):
        if user not in self.likes.all():
            self.likes.add(user)

    def unlike(self, user):
        if user in self.likes.all():
            self.likes.remove(user)

    def save_post(self, user):
        if user not in self.saved_by.all():
            self.saved_by.add(user)

    def unsave_post(self, user):
        if user in self.saved_by.all():
            self.saved_by.remove(user)

    def is_bookmarked(self, user):
        return self.saved_by.filter(id=user.id).exists()

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def save_count(self):
        return self.saved_by.count()

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    class Meta:
        ordering = ['created_at']