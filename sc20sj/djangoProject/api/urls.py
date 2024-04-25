from django.urls import path
from . import views  # Importing views from the current package

urlpatterns = [
    # URL path for user login API
    path('api/login/', views.api_login, name='api_login'),

    # URL path for user logout API
    path('api/logout/', views.api_logout, name='api_logout'),

    # URL path for retrieving or posting stories
    path('api/stories/', views.api_get_stories, name='post_story'),

    # URL path for deleting a specific story by its unique key
    path('api/stories/<int:key>/', views.api_delete_story, name='api_delete_story'),
]