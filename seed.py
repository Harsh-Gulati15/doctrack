from app import create_app
from app.models import db, User, Department
import bcrypt

def seed():
    app = create_app()
    with app.app_context():
        # Check if already seeded
        if User.query.filter_by(username='admin').first():
            print('Database already seeded. Skipping.')
            return
        
        # Create all tables
        db.create_all()

        # Create departments
        finance = Department(department_name='Finance', department_code='FIN')
        hr = Department(department_name='Human Resources', department_code='HR')
        it = Department(department_name='Information Technology', department_code='IT')
        
        db.session.add_all([finance, hr, it])
        db.session.commit()

        def hash_password(password):
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

        # Create admin
        admin = User(
            username='admin',
            password_hash=hash_password('admin123'),
            full_name='System Administrator',
            email='admin@doctrack.local',
            role='superadmin'
        )
        db.session.add(admin)

        # Create receptionist
        receptionist = User(
            username='receptionist',
            password_hash=hash_password('user123'),
            full_name='Front Desk Receptionist',
            email='reception@doctrack.local',
            role='receptionist'
        )
        db.session.add(receptionist)

        # Create dept users
        fin_user = User(
            username='fin_user',
            password_hash=hash_password('user123'),
            full_name='Finance Officer',
            email='finance@doctrack.local',
            role='dept_user',
            department_id=finance.department_id
        )
        
        hr_user = User(
            username='hr_user',
            password_hash=hash_password('user123'),
            full_name='HR Officer',
            email='hr@doctrack.local',
            role='dept_user',
            department_id=hr.department_id
        )
        
        it_user = User(
            username='it_user',
            password_hash=hash_password('user123'),
            full_name='IT Officer',
            email='it@doctrack.local',
            role='dept_user',
            department_id=it.department_id
        )
        
        db.session.add_all([fin_user, hr_user, it_user])
        db.session.commit()

        # Set department heads
        finance.head_user_id = fin_user.user_id
        hr.head_user_id = hr_user.user_id
        it.head_user_id = it_user.user_id
        
        db.session.commit()

        print('\n=== Database seeded successfully! ===')
        print('\nLogin credentials:')
        print('  Super Admin: admin / admin123')
        print('  Receptionist: receptionist / user123')
        print('  Finance: fin_user / user123')
        print('  HR: hr_user / user123')
        print('  IT: it_user / user123')

if __name__ == '__main__':
    seed()
