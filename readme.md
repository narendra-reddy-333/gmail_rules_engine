This repository contains the Python scripts, which involves integrating with the Gmail API and storing emails in SQlite
database and performing rule-based operations on emails.

## Project Structure

### Classes

* GmailAPI: This script authenticates with the Gmail API, fetches emails from the inbox.
* EmailDatabase: stores emails in a SQLite3 database and fetches the same.
* RulesProcessor: First parses the rules from rules.json and then fetches all mails from database and applies the rules.

### Files:

* rules.json: This file stores the email processing rules in JSON format.
* database.db: This is the SQLite3 database file where emails are stored.
  Requirements
* token.pickle, credentials.json: Gmail API auth creds.

### Requirements

Python 3.x
The following Python libraries:
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
sqlalchemy
Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/narendra-reddy-333/gmail_rules_engine
    ```

2. Create a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    Install the required Python libraries:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up API credentials:
    * Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
    * Enable the Gmail API for your project.
    * Create OAuth client ID credentials and download the JSON file.
    * Rename the JSON file to `credentials.json` and place it in the project directory.

4. Running the Scripts:
   * Run `main.py` to fetch emails and store them in the database and apply rules.
   ```bash
    python main.py
    ```

**Rules Configuration**

The `rules.json` file contains the rules for processing emails. Each rule has the following structure:

```json
{
  "predicate": "all",  // or "any"
  "conditions": [
    {
      "field": "from",
      "predicate": "contains",
      "value": "example.com"
    },
    {
      "field": "subject",
      "predicate": "equals",
      "value": "Important Update"
    }
  ],
  "actions": [
    {
      "action": "mark_as_read"
    },
    {
      "action": "move_to",
      "destination": "Important"
    }
  ]
}