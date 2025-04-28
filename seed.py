import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Database dosyasını otomatik sil
db_path = os.path.join(os.getcwd(), 'instance', 'rfi.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("✅ Eski veritabanı dosyası silindi.")

# Flask uygulamasını oluştur ve context aç
app = create_app()
with app.app_context():
    # Veritabanını sıfırla
    db.create_all()

    # Admin kullanıcısını oluştur
    hashed_pw = generate_password_hash('Admin123', method='pbkdf2:sha256')
    admin = User(username='admin', email='admin@example.com', password=hashed_pw, role='admin')

    db.session.add(admin)
    db.session.commit()

    print("✅ Database reset and admin user created successfully.")

if __name__ == '__main__':
    pass