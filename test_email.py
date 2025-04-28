from flask import Flask
from flask_mail import Mail, Message
from config import Config

# Flask uygulaması oluştur
app = Flask(__name__)
app.config.from_object(Config)

# Mail objesi oluştur
mail = Mail(app)

# App contexti ile çalış
with app.app_context():
    msg = Message(
        subject='Test Email from Construction App',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=['oguzcan.ozgenc@gmail.com'],  # TEST için kendi mail adresin
        body='This is a test email sent from your Construction Inspection App using Brevo SMTP.'
    )

    try:
        mail.send(msg)
        print('✅ Email sent successfully!')
    except Exception as e:
        print(f'❌ Failed to send email: {e}')