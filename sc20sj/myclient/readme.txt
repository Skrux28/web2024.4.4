# News Service Client Application

This command-line application is designed to interact with a news service API, allowing users to log in, post news stories, retrieve news, and logout. Below you will find detailed instructions on how to setup and use the application.

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/Skrux28/web2024.4.4.git
   ```

2. **Install dependencies:**
   ```
   pip install requests
   ```

## Configuration

Before using the client, you must configure the `base_url` of your news service. This can be done by modifying the `base_url` variable inside the `NewsClient` class if not dynamically set during runtime.

## Usage

The application supports several commands to interact with the news service:

### Login

To log in to a news service:

```
login <url>
```

- `<url>`: sc20sj.pythonanywhere.com.
- This command prompts the user to enter a username and password.
1. username: skrux  passwords:1597823aboABCabo
2. username: gzhao  passwords:gzhao



### Logout

To log out from the current session:

```
logout
```

### Post a Story

To post a new news story:

```
post
```

- This command prompts the user to enter the story’s headline, category, region, and details.

### Retrieve News

To fetch news stories based on filters:

```
news [-id=] [-cat=] [-reg=] [-date=]
```

- `-id`: Optional. The ID of the news service. If omitted, the application will fetch news from all registered services.
- `-cat`: Optional. The category of the news. Defaults to all categories if omitted.
- `-reg`: Optional. The region of the news. Defaults to all regions if omitted.
- `-date`: Optional. The date from which news stories are required, in `dd/mm/yyyy` format. Defaults to all dates if omitted.

### List News Services

To list all registered news services in the directory:

```
list
```

### Delete a Story

To delete a specific news story:

```
delete <story_key>
```

- `<story_key>`: The unique key of the story to delete.

## Troubleshooting

If you encounter issues with the application, please check the following:

- Ensure that the news service URL is correct and the service is operational.
- Verify that your internet connection is stable.
- Check that all required Python packages are installed.

For further assistance, contact the support team at sc20sj@leeds.ac.uk

---
