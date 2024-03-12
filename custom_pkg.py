import requests
import urllib3
import ssl
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

def send_email(data, name):
    # Configure email settings
    smtp_server = 'smtp-relay.brevo.com'
    smtp_port = 587
    sender_email = 'lenti.pacurar@gmail.com'
    receiver_email = 'office.siventys@gmail.com'
    password = 'Rsy0dKXbnq1FWJGO'

    # Create email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = 'Cautarea d-voastra pentru: '+name

    # Get the current date
    current_date = datetime.now()

    # Format the current date as a long date
    formatted_date = current_date.strftime("%Y-%b-%d")

    # Attach data to email
    part = MIMEApplication(data)
    part.add_header('Content-Disposition', 'attachment', 
                    filename='RezultatCautare_'+name+' din '+formatted_date+'.html')
    msg.attach(part)

    # Add an HTML body to the email
    text_body = 'Cautarea d-voastra din portalul https://scsanctions.un.org/search/ a returnat rezultatul din fisierul atasat.'
    msgBody = MIMEText(text_body, 'html')
    msg.attach(msgBody)

    try:
        # Connect to SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        logging.info('Error occurred while fetching data.')
        return 'Email sent successfully'
    except Exception as e:
        return f"Failed to send email: {e}"
