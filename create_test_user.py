from Website import db, create_app
from Website.models import User

app = create_app()

with app.app_context():
    # Create a new user with a known password
    password = 'testpassword123'
    new_user = User(username='testuser', email='test@example.com', password=password)
    db.session.add(new_user)
    db.session.commit()

    # Fetch the user and check password
    user = User.query.filter_by(email='test@example.com').first()
    if user:
        print(f"User found: {user.username}")
        print(f"Password hash in database: {user.password_hash}")
        if user.check_password(password):
            print("Password check passed.")
        else:
            print("Password check failed.")