import os
import sys
import csv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Building, DisciplineCode

def import_buildings():
    app = create_app()
    with app.app_context():
        # Import buildings
        with open('app/static/BuildingCode.csv', 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            for row in csv_reader:
                building = Building(
                    code=row['BuildingCode'],
                    name=row['BuildingName'],
                    description=None
                )
                existing = Building.query.filter_by(code=building.code).first()
                if not existing:
                    db.session.add(building)
                    print(f"Adding building: {building.code} - {building.name}")
        
        # Import discipline codes
        with open('app/static/DisciplineCode.csv', 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            for row in csv_reader:
                discipline = DisciplineCode(
                    code=row['DisciplineCode'],
                    name=row['Discipline'],
                    description=None
                )
                existing = DisciplineCode.query.filter_by(code=discipline.code).first()
                if not existing:
                    db.session.add(discipline)
                    print(f"Adding discipline: {discipline.code} - {discipline.name}")
        
        try:
            db.session.commit()
            print("Successfully imported buildings and discipline codes!")
        except Exception as e:
            db.session.rollback()
            print(f"Error importing data: {str(e)}")

if __name__ == '__main__':
    import_buildings() 