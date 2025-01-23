from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)

    class Meta:
        # Specify the app label explicitly to avoid potential conflicts
        app_label = 'todos'

    def __str__(self):
        return self.username

# Todo model
class Todo(models.Model):
    title = models.CharField(max_length=255, blank=False)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, 
        related_name='todos', 
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
