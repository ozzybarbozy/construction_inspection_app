import csv
from app import create_app, db
from app.models import Building, DisciplineCode

def import_data():
    app = create_app()
    with app.app_context():
        # Import buildings
        with open('app/static/BuildingCode.csv', 'r', encoding='utf-8') as file:
            # Skip the header row
            next(file)
            csv_reader = csv.reader(file, delimiter=';')
            for row in csv_reader:
                if len(row) >= 2:  # Ensure we have both code and name
                    building = Building(
                        code=row[0],
                        name=row[1]
                    )
                    existing = Building.query.filter_by(code=building.code).first()
                    if not existing:
                        db.session.add(building)
                        print(f"Adding building: {building.code} - {building.name}")
        
        # Import discipline codes
        with open('app/static/DisciplineCode.csv', 'r', encoding='utf-8') as file:
            # Skip the header row
            next(file)
            csv_reader = csv.reader(file, delimiter=';')
            for row in csv_reader:
                if len(row) >= 2:  # Ensure we have both code and name
                    discipline = DisciplineCode(
                        code=row[0],
                        name=row[1]
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
    import_data() 