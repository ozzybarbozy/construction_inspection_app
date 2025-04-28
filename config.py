import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rfi.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings for Yandex SMTP
    MAIL_SERVER = 'smtp.yandex.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'oozgenc@yandex.com'  # Replace with your Yandex email
    MAIL_PASSWORD = 'lwoozsctpkpdcjhj'  # Replace with your Yandex account password
    MAIL_DEFAULT_SENDER = ('Construction Inspection App', 'oozgenc@yandex.com')  # Replace with your Yandex email