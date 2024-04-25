from django.db import models
from django.contrib.auth.models import User


class Story(models.Model):
    # Choices for the category field
    DoesNotExist = None
    CATEGORY_CHOICES = [
        ('pol', 'Politics'),  # Political stories
        ('art', 'Art'),  # Art-related stories
        ('tech', 'Technology'),  # Technology-related stories
        ('trivia', 'Trivia'),  # Trivia and other light, fun stories
    ]

    # Choices for the region field
    REGION_CHOICES = [
        ('uk', 'UK'),  # Stories relevant to the United Kingdom
        ('eu', 'EU'),  # Stories relevant to the European Union
        ('w', 'World'),  # Stories with global relevance
    ]

    # Primary key for the story, automatically generated
    unique_key = models.AutoField(primary_key=True)

    # Title of the story, maximum length of 64 characters
    headline = models.CharField(max_length=64)

    # Category of the story, limited to predefined choices
    category = models.CharField(max_length=6, choices=CATEGORY_CHOICES)

    # Geographic region of the story, limited to predefined choices
    region = models.CharField(max_length=2, choices=REGION_CHOICES)

    # Author of the story, linked to Django's built-in User model
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Timestamp for when the story was added, automatically set to the current date and time on creation
    date = models.DateTimeField(auto_now_add=True)

    # Detailed text for the story, maximum length of 128 characters
    details = models.CharField(max_length=128)

    def __str__(self):
        # String representation of the Story, which will be used in the Django admin and other places
        return self.headline
