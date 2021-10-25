"""
Download conversations from a Help Scout mailbox and save to CSV file.
Be sure to replace the App ID and Secret in the authorization call as well
as the Mailbox ID in the conversations API call.
Python: 3.9.0
"""

import csv
import datetime
import requests

# The token endpoint.
auth_endpoint = 'https://api.helpscout.net/v2/oauth2/token'

# Preparing our POST data.
post_data = ({
    'grant_type': 'client_credentials',
    'client_id': '',
    'client_secret': ''
})

# Send the data.
r = requests.post(auth_endpoint, data=post_data)

# Save our token.
token = r.json()['access_token']
print(token)
all_conversations = False
page = 1

# Prepare our headers for all endpoints using token.
endpoint_headers = {
    'Authorization': 'Bearer {}'.format(token)
}





r = requests.get("https://api.helpscout.net//v2/mailboxes", headers=endpoint_headers)
print(r.json())
print("")
print("")
#r = requests.get("https://api.helpscout.net/v2/conversations/1650904553/threads/", headers=endpoint_headers)
#print(r.json())

# Creates our file, or rewrites it if one is present.
with open('conversations.csv', mode="w", newline='', encoding='utf-8') as fh:
    # Define our columns.
    columns = ['ID', 'Customer Name', 'Customer email addresses', 'Assignee', 'Status', 'Subject', 'Created At',
               'Closed At', 'Closed By', 'Resolution Time (seconds)']  
    csv_writer = csv.DictWriter(fh, fieldnames=columns) # Create our writer object.
    csv_writer.writeheader() # Write our header row.
    
    while not all_conversations:
        # Prepare conversations endpoint with status of conversations we want and the mailbox.
        conversations_endpoint = 'https://api.helpscout.net/v2/conversations?status=all&mailbox=72187&page={}'.format(
            page
        )
        r = requests.get(conversations_endpoint, headers=endpoint_headers)
        conversations = r.json()



        # Cycle over conversations in response.
        for conversation in conversations['_embedded']['conversations']:
            conversations_endpoint = 'https://api.helpscout.net/v2/conversations/{}/threads'.format(
                conversation['id']
            )

            customer_name = '{} {}'.format(
                conversation['primaryCustomer']['first'],
                conversation['primaryCustomer']['last']
            )

            assignee = '{} {}'.format(conversation['assignee']['first'], conversation['assignee']['last']) \
            if 'assignee' in conversation else ''
            subject = conversation['subject'] if 'subject' in conversation else 'No subject'
            closed_at = conversation['closedAt'] if 'closedAt' in conversation else ''


            r = requests.get(conversations_endpoint, headers=endpoint_headers)
            threads = r.json()['_embedded']['threads']
            for thread in threads:
                body = ''
                createdBy = thread['createdBy']['email']
                if 'body' in thread.keys():
                    body += "\n<br>From:"+createdBy+"<br/>"+thread['body']
                print(body)

        if page == conversations['page']['totalPages']:
            all_conversations = True
            continue
        else:
            page += 1