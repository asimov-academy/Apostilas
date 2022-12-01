
from imbox import Imbox # pip install imbox
from datetime import datetime
import pandas as pd

username = 'seu.email@gmail.com'
password = open('passwords/token', 'r').read()
host = "imap.gmail.com"
download_folder = "attachments"
    
mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
messages = mail.messages()
# message.keys()

for (uid, message) in messages:
    message.subject
    message.body
    message.sent_from
    message.sent_to
    message.cc
    message.headers
    pd.to_datetime(message.date)

    for attach in message.attachments:
        with open(download_folder, "wb") as fp:
            fp.write(attach.get('content').read())
    break

mail.logout()