import click
import csv
from flask.cli import with_appcontext
from . import db
from .models import Building, DisciplineCode

@click.command('import-data')
@with_appcontext
def import_data():
    """Import buildings and discipline codes from CSV files."""
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
                    click.echo(f"Adding building: {building.code} - {building.name}")
    
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
                    click.echo(f"Adding discipline: {discipline.code} - {discipline.name}")
    
    try:
        db.session.commit()
        click.echo("Successfully imported buildings and discipline codes!")
    except Exception as e:
        db.session.rollback()
        click.echo(f"Error importing data: {str(e)}", err=True) 