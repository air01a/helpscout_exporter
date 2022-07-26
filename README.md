# helpscout_exporter
Helpscout mailboxes exporter (csv list + html files with mails)

# install
Create a .env file 
`touche .env`

Add your client id & secret
```
HELPSCOUT_CLIENT_ID=abc
HELPSCOUT_CLIENT_SECRET=def
```

# usage
List mailboxes
`python3 export.py -l`

Download conversation from a mailbox
`python3 export.py -e 123123`

Set the start and end pages from which to download conversations.  Useful for resuming an existing export that failed.
`python3 export.py -e 123123 --start 2 --end 29`

Attachments can be downloaded by setting a flag within the script (Line #172)
