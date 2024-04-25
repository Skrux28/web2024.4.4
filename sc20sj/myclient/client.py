import argparse
import json
import datetime
import random
import requests
import sys

session = requests.Session()

def is_valid_date(date_str):
    """
    Check if a date string is in the valid format 'dd/mm/yyyy'.
    :param date_str: A string representing the date.
    :return: True if the date is valid, False otherwise.
    """
    try:
        datetime.datetime.strptime(date_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def format_news_data(data, agency_name):
    """
    Formats news data into a readable string format including agency name.
    :param data: JSON data containing news stories.
    :param agency_name: Name of the news agency.
    :return: Formatted string containing news details.
    """
    news_output = [f"===== News from: {agency_name} ====="]
    for story in data.get('stories', []):
        news_output.append(f"{story['headline']} (Published on {story['story_date']})")
        news_output.append(f"Details: {story['story_details']} [Author: {story['author']} ID: {story['key']}]")
    return '\n'.join(news_output)

class NewsClient:
    """
    A client for interacting with a news service API.
    """
    def __init__(self):
        """
        Initializes the NewsClient instance.
        """
        self.base_url = None
        self.logged_in = False
        self.sessionData = {"login_url": "", "logged_in": False, "agencies": []}
        self.session = requests.Session()

    def login(self, url):
        """
        Logs in to the news service using a username and password.
        :param url: The base URL of the news service.
        """
        self.base_url = url
        username = input("Enter username: ")
        password = input("Enter password: ")
        payload = {"username": username, "password": password}
        response = session.post(f"{self.base_url}/api/login/", data=payload)
        if response.status_code == 200:
            self.logged_in = True
            print(response.text)
        else:
            print(f"Login failed: {response.text}")

    def logout(self):
        """
        Logs out of the news service.
        """
        if not self.logged_in:
            print("You are not logged in.")
            return
        response = session.post(f"{self.base_url}/api/logout/")
        if response.status_code == 200:
            self.logged_in = False
            print(response.text)
        else:
            print(f"Logout failed: {response.text}")

    def post_story(self):
        """
        Posts a news story to the service. Requires login.
        """
        if not self.logged_in:
            print("You need to login first.")
            return
        headline = input("Enter story headline: ")
        category = input("Enter story category: ")
        region = input("Enter story region: ")
        details = input("Enter story details: ")
        payload = {
            "headline": headline,
            "category": category,
            "region": region,
            "details": details
        }
        response = requests.post(f"{self.base_url}/api/stories", json=payload)
        if response.status_code == 201:
            print("Story posted successfully")
        else:
            print(f"Failed to post story: {response.text}")

    def retrieve_and_display_news(self, opts):
        """
        Retrieves and displays news stories based on filter criteria. Requires login.
        :param opts: A Namespace containing filter options like category, region, and date.
        """
        if not self.logged_in:
            print("You need to login first.")
            return
        base_headers = {'Accept': 'application/json'}
        story_cat = (getattr(opts, 'category', '*') or '*').strip('"')
        story_region = (getattr(opts, 'region', '*') or '*').strip('"')
        story_date = (getattr(opts, 'date', '*') or '*').strip('"')

        if story_cat not in ['*', 'pol', 'art', 'tech', 'trivia']:
            return "Error: Invalid category specified."
        if story_region not in ['*', 'uk', 'w', 'eu']:
            return "Error: Invalid region specified."
        if story_date != '*' and not is_valid_date(story_date):
            return "Error: Invalid date format. Use 'dd/mm/yyyy'."

        filter_criteria = {
            'story_cat': story_cat,
            'story_region': story_region,
            'story_date': story_date
        }

        agency_id = (getattr(opts, 'identifier', '') or '').strip('"')
        news_agencies = self.get_news_agencies()

        if agency_id:
            agency = next((agency for agency in news_agencies if agency['agency_code'] == agency_id), None)
            if not agency:
                return "Error: No agency found with the specified identifier."
            return self.query_agency_for_news(agency, filter_criteria, base_headers)

        results = []
        for agency in news_agencies:
            news = self.query_agency_for_news(agency, filter_criteria, base_headers)
            if news:
                print(news)
                print("\n")
                results.append(news)
                if len(results) >= 20:  # limit to first 20 results across all agencies
                    break
        return '\n'.join(results)

    def get_news_agencies(self):
        """
        Retrieves the list of all news agencies from the directory service.
        :return: A list of news agencies.
        """
        response = self.session.get("http://newssites.pythonanywhere.com/api/directory")
        return json.loads(response.text) if response.ok else []

    def query_agency_for_news(self, agency, filters, headers):
        """
        Queries a single news agency for news stories based on filters.
        :param agency: The agency to query.
        :param filters: The filter criteria for news stories.
        :param headers: HTTP headers for the request.
        :return: Formatted news stories from the specified agency.
        """
        endpoint = f"{agency['url']}/api/stories"
        query = '&'.join(f'{key}={value}' for key, value in filters.items())
        response = self.session.get(f"{endpoint}?{query}", headers=headers)
        if not response.ok:
            return f"Failed to fetch news from {agency['agency_name']}"
        return format_news_data(response.json(), agency['agency_name'])

    def list_agencies(self):
        """
        Lists all registered news agencies. Requires login.
        """
        if not self.logged_in:
            print("You need to login first.")
            return
        url = 'https://newssites.pythonanywhere.com/api/directory/'
        response = session.get(url)
        if response.status_code == 200:
            agencies = response.json()
            random_agencies = random.sample(agencies, 20)
            for agency in agencies:
                print(agency)
        else:
            print(response.json())

    def delete_story(self, story_key):
        """
        Deletes a specific news story by its unique key.
        :param story_key: The key of the story to delete.
        """
        response = requests.delete(f"{self.base_url}/api/stories/{story_key}")
        if response.status_code == 200:
            print("Story deleted successfully")
        else:
            print(f"Failed to delete story: {response.text}")


def main():
    client = NewsClient()
    parser = argparse.ArgumentParser(description="Interact with an online news service through a series of commands.")
    subparsers = parser.add_subparsers(title="Available Commands", dest="command",
                                       help='Commands to manage news interactions')
    news_parser = subparsers.add_parser("news", help="Retrieve news stories by applying various filters.")
    news_parser.add_argument("-id", help="Specify the unique identifier of the news service to target.")
    news_parser.add_argument("-cat",
                             help="Select the category of news to display, such as politics, technology, or arts.")
    news_parser.add_argument("-reg", help="Choose the geographic region for the news stories, e.g., UK, EU, etc.")
    news_parser.add_argument("-date", help="Filter news occurring on or after a particular date in dd/mm/yyyy format.")

    while True:
        command = input("Enter command: ").strip()
        parts = command.split()
        if command.startswith("login"):
            if len(parts) < 2:
                print('URL is required for the login command.')
                continue
            url = command.split()[1]
            client.login(url)
        elif command == "logout":
            client.logout()
        elif command == "post":
            client.post_story()
        elif command.startswith("news"):
            client.retrieve_and_display_news(parser.parse_args(command.split()))  # 传递 'news' 之后的参数
        elif command == "list":
            client.list_agencies()
        elif command.startswith("delete"):
            story_key = command.split()[1]
            client.delete_story(story_key)
        elif command == "exit":
            sys.exit()
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()
