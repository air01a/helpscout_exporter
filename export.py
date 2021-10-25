"""
Download conversations from a Help Scout mailbox and save to CSV file.
Be sure to replace the App ID and Secret in the authorization call as well
as the Mailbox ID in the conversations API call.
Python: 3.9.0
"""

import csv
import datetime
import requests
import getopt,sys
import os 

CLIENT_ID = ''
CLIENT_SECRET = ''

def authenticate():
    # The token endpoint.
    auth_endpoint = 'https://api.helpscout.net/v2/oauth2/token'
    # Preparing our POST data.
    post_data = ({
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    # Send the data.
    r = requests.post(auth_endpoint, data=post_data)
    
    # Save our token.
    token = r.json()['access_token']
    return token


def list_mailboxes(endpoint_headers):
    r = requests.get("https://api.helpscout.net//v2/mailboxes", headers=endpoint_headers)

    for mailbox in r.json()["_embedded"]["mailboxes"]:
        print(str(mailbox["id"])+" : " + mailbox["name"])

def export_mailboxes(mailboxes_id, endpoint_headers):
    for mailbox_id in mailboxes_id.split(','): 
        print(mailbox_id)


    for mailbox_id in mailboxes_id.split(','): 
        all_conversations = False
        page = 1
        if not os.path.exists(mailbox_id+'/'):
            os.makedirs(mailbox_id+'/')

        # Creates our file, or rewrites it if one is present.
        with open(str(mailbox_id)+'.csv', mode="w", newline='', encoding='utf-8') as fh:
            # Define our columns.
            columns = ['ID', 'Customer Name', 'Customer email addresses', 'Assignee', 'Status', 'Subject', 'Created At',
                    'Closed At', 'Closed By', 'Resolution Time (seconds)']  
            csv_writer = csv.DictWriter(fh, fieldnames=columns) # Create our writer object.
            csv_writer.writeheader() # Write our header row.
            
            while not all_conversations:
                # Prepare conversations endpoint with status of conversations we want and the mailbox.
                conversations_endpoint = 'https://api.helpscout.net/v2/conversations?status=all&mailbox={}&page={}'.format(
                    mailbox_id,
                    page
                )

                r = requests.get(conversations_endpoint, headers=endpoint_headers)

                conversations = r.json()

                # Cycle over conversations in response.
                for conversation in conversations['_embedded']['conversations']:
                    print(conversation['id'])
                    # If the email is missing, we won't keep this conversation.
                    # Depending on what you will be using this data for,
                    # You might omit this.
                    if 'email' not in conversation['primaryCustomer']:
                        print('Missing email for {}'.format(customer_name))
                        continue

                    # Prepare customer name.
                    customer_name = '{} {}'.format(
                        conversation['primaryCustomer']['first'],
                        conversation['primaryCustomer']['last']
                    )

                    # Prepare assignee, subject, and closed date if they exist.
                    assignee = '{} {}'.format(conversation['assignee']['first'], conversation['assignee']['last']) \
                        if 'assignee' in conversation else ''
                    subject = conversation['subject'] if 'subject' in conversation else 'No subject'
                    closed_at = conversation['closedAt'] if 'closedAt' in conversation else ''

                    # If the conversation has been closed, let's get the resolution time and who closed it.
                    closed_by = ''
                    resolution_time = 0
                    if 'closedByUser' in conversation and conversation['closedByUser']['id'] != 0:
                        closed_by = '{} {}'.format(
                            conversation['closedByUser']['first'], conversation['closedByUser']['last']
                        )
                        createdDateTime = datetime.datetime.strptime(conversation['createdAt'], "%Y-%m-%dT%H:%M:%S%z")
                        closedDateTime = datetime.datetime.strptime(conversation['closedAt'], "%Y-%m-%dT%H:%M:%S%z")
                        resolution_time = (closedDateTime - createdDateTime).total_seconds()

                    csv_writer.writerow({
                        'ID': conversation['id'],
                        'Customer Name': customer_name,
                        'Customer email addresses': conversation['primaryCustomer']['email'],
                        'Assignee': assignee,
                        'Status': conversation['status'],
                        'Subject': subject,
                        'Created At': conversation['createdAt'],
                        'Closed At': closed_at,
                        'Closed By': closed_by,
                        'Resolution Time (seconds)': resolution_time
                    })

                    thread_endpoint = 'https://api.helpscout.net/v2/conversations/{}/threads'.format(
                        conversation['id']
                    )
                    r = requests.get(thread_endpoint, headers=endpoint_headers)
                    threads = r.json()['_embedded']['threads']
                    body = '<html><body>'
                    for thread in threads:
                        createdBy = thread['createdBy']['email']
                        if 'body' in thread.keys():
                            body += "\n<br><b>From:"+createdBy+"</b><br/>"+thread['body']+'<br /><tr>'
                    body += "</body></html>"
                    with open(mailbox_id+'/'+str(conversation['id'])+'.html', 'w+') as f:
                        f.write(body)

                if page == conversations['page']['totalPages']:
                    all_conversations = True
                    continue
                else:
                    page += 1


def main(argv):
    opt_list_mailboxes = False
    opt_export_mailboxes = None
    try:
        opts, args = getopt.getopt(argv,"le:",)
    except getopt.GetoptError:
        print('-l : list all messageries')
        print('-e id : export id')
        sys.exit(2)


    for (opt,arg) in opts:
        if (opt == '-l'):
            opt_list_mailboxes = True
        if (opt == '-e'):
            opt_export_mailboxes = arg

    token = authenticate()


    # Prepare our headers for all endpoints using token.
    endpoint_headers = {
        'Authorization': 'Bearer {}'.format(token)
    }


    if opt_list_mailboxes:
        list_mailboxes(endpoint_headers)


    if opt_export_mailboxes != None:
        export_mailboxes(opt_export_mailboxes,endpoint_headers) 
        

if __name__ == "__main__":
   main(sys.argv[1:])