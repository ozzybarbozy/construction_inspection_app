from app import create_app, db
from app.models import RFI, User, UserRole, Stakeholder
from datetime import datetime, time

def test_rfi_creation():
    app = create_app()
    with app.app_context():
        # Create test data
        # Create a contractor stakeholder
        contractor_stakeholder = Stakeholder.query.filter_by(role='Contractor').first()
        if not contractor_stakeholder:
            contractor_stakeholder = Stakeholder(name='Test Contractor', role='Contractor')
            db.session.add(contractor_stakeholder)
            db.session.commit()
        
        # Create a user with contractor stakeholder
        contractor = User.query.filter_by(username='test_contractor').first()
        if not contractor:
            contractor = User(
                username='test_contractor',
                email='test@contractor.com',
                password='test123',
                stakeholder_id=contractor_stakeholder.id,
                name='Test',
                surname='Contractor'
            )
            db.session.add(contractor)
            db.session.commit()
        
        # Create a test RFI
        test_rfi = RFI(
            title='Test RFI',
            description='Test RFI Description',
            submitted_by=contractor.username,
            status='Open',
            priority='Normal',
            building_code='B01',
            discipline_code='ARC',
            drawing_number='DWG-001',
            inspection_date=datetime.now().date(),
            inspection_time=time(10, 0),
            assigned_to_id=contractor.id
        )
        
        # Generate RFI number
        test_rfi.rfi_number = RFI.generate_rfi_number(test_rfi.discipline_code, test_rfi.building_code)
        
        db.session.add(test_rfi)
        db.session.commit()
        
        # Print the created RFI
        print('\nCreated RFI:')
        print(f'RFI Number: {test_rfi.rfi_number}')
        print(f'RFI ID: {test_rfi.id}')
        print(f'Building Code: {test_rfi.building_code}')
        print(f'Discipline Code: {test_rfi.discipline_code}')
        print(f'Status: {test_rfi.status}')
        
        # Create another RFI with the same building and discipline code to test sequential numbering
        second_rfi = RFI(
            title='Second Test RFI',
            remarks='Second Test RFI Description',
            submitted_by=contractor.username,
            status='Open',
            priority='Normal',
            building_code='B01',
            discipline_code='ARC',
            drawing_number='DWG-002',
            inspection_date=datetime.now().date(),
            inspection_time=time(14, 0),
            assigned_to_id=contractor.id
        )
        
        # Generate RFI number for second RFI
        second_rfi.rfi_number = RFI.generate_rfi_number(second_rfi.discipline_code, second_rfi.building_code)
        
        db.session.add(second_rfi)
        db.session.commit()
        
        # Print the second RFI
        print('\nCreated Second RFI:')
        print(f'RFI Number: {second_rfi.rfi_number}')
        print(f'RFI ID: {second_rfi.id}')
        print(f'Building Code: {second_rfi.building_code}')
        print(f'Discipline Code: {second_rfi.discipline_code}')
        print(f'Status: {second_rfi.status}')

if __name__ == '__main__':
    test_rfi_creation() 