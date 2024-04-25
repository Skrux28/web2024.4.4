from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Story


@csrf_exempt
def api_login(request):
    """
    Handle login requests. Exempt from CSRF for API usage.
    :param request: The HTTP request object.
    :return: HttpResponse indicating success or failure.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)  # Authenticates user against database.
        if user and user.is_active:
            login(request, user)  # Logs the user in.
            return HttpResponse('Login successful!', content_type='text/plain', status=200)
        else:
            return HttpResponse('Invalid login!', content_type='text/plain', status=401)
    else:
        return HttpResponse('Request Method Not Allowed', content_type='text/plain', status=403)


@csrf_exempt
@login_required
def api_logout(request):
    """
    Handle logout requests. Exempt from CSRF for API usage.
    Requires user to be logged in.
    :param request: The HTTP request object.
    :return: HttpResponse indicating logout was successful.
    """
    if request.method == 'POST':
        logout(request)  # Logs the user out.
        return HttpResponse('You have logout successful!', content_type='text/plain', status=200)
    else:
        return HttpResponse('Request Method Not Allowed', content_type='text/plain', status=403)


@csrf_exempt
def api_stories(request):
    """
    Route requests to post or get stories based on the HTTP method.
    Exempt from CSRF to facilitate API access.
    :param request: The HTTP request object.
    :return: Calls either api_post_story or api_get_stories based on method.
    """
    if request.method == 'POST':
        return api_post_story(request)
    elif request.method == 'GET':
        return api_get_stories(request)
    else:
        return HttpResponse('Method not allowed', status=405)


@csrf_exempt
@login_required
def api_post_story(request):
    """
    Create a new story with provided JSON data. Requires user authentication.
    :param request: The HTTP request object.
    :return: JsonResponse indicating success or failure.
    """
    try:
        data = json.loads(request.body)
        headline = data.get('headline')
        category = data.get('category')
        region = data.get('region')
        details = data.get('details')

        if not (headline and category and region and details):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if len(headline) > 64 or len(details) > 128:
            return JsonResponse({"error": "Story headline or details exceeds maximum length"}, status=400)

        if category not in ['pol', 'art', 'tech', 'trivia'] or region not in ['uk', 'eu', 'w']:
            return JsonResponse({"error": "Invalid category or region"}, status=400)

        story = Story.objects.create(
            headline=headline, category=category, region=region, details=details, author=request.user,
            date=timezone.now()
        )
        return JsonResponse({"message": "Story posted successfully", "story_id": story.unique_key}, status=201)

    except Exception as e:
        return JsonResponse({"error": "Failed to post story: " + str(e)}, status=503)


@csrf_exempt
@login_required
def api_get_stories(request):
    """
    Retrieve stories based on filter criteria provided via query parameters.
    Requires user authentication.
    :param request: The HTTP request object.
    :return: JsonResponse containing a list of stories.
    """
    try:
        story_cat = request.GET.get('story_cat', '*')
        story_region = request.GET.get('story_region', '*')
        story_date = request.GET.get('story_date', '*')

        if story_cat == '*' and story_region == '*' and story_date == '*':
            stories = Story.objects.all()
        else:
            stories = Story.objects.filter(category=story_cat, region=story_region, date__gte=story_date)

        response_data = [
            {"key": str(story.unique_key), "headline": story.headline, "story_cat": story.category,
             "story_region": story.region, "author": story.author.username,
             "story_date": story.date.strftime('%Y-%m-%d %H:%M:%S'),
             "story_details": story.details}
            for story in stories
        ]
        return JsonResponse({"stories": response_data}, status=200)
    except Exception as e:
        return JsonResponse({"error": "Failed to retrieve stories: " + str(e)}, status=404)


@csrf_exempt
@login_required
def api_delete_story(request, key):
    """
    Delete a story identified by its unique key. Requires user to be the story's author.
    :param request: The HTTP request object.
    :param key: The unique key of the story to be deleted.
    :return: HttpResponse indicating success or failure.
    """
    if request.method == 'DELETE':
        try:
            story = Story.objects.get(unique_key=key)
            if request.user != story.author:
                return JsonResponse({"error": "You are not allowed to delete this story!"}, status=403)
            story.delete()
            return HttpResponse("Story deleted successfully", status=200)
        except Story.DoesNotExist:
            return HttpResponse("Story not found", status=404)
        except Exception as e:
            return HttpResponse("Failed to delete story: " + str(e), status=503)
    else:
        return HttpResponse("Method not allowed", status=405)
