from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)

# Configure Flask Mail for Outlook.com
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587  # Port 587 for STARTTLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'sasipriya004@outlook.com'  # Enter your Outlook.com email address
app.config['MAIL_PASSWORD'] = 'Karu14399!'  # Enter your Outlook.com email password
app.config['MAIL_DEFAULT_SENDER'] = 'sasipriya004@outlook.com'  # Enter your Outlook.com email address

mail = Mail(app)

# Function to send email
def send_email():
    with app.app_context():
        subject = 'Test Email'
        recipient = 'sasipriya004@outlook.com'  # Replace with the recipient's email address

        # Build the email body
        body = "This is a test email sent from Flask."

        msg = Message(subject=subject, recipients=[recipient], body=body)

        mail.send(msg)

if __name__ == '__main__':
    send_email()
