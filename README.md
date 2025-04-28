# Construction Inspection App

A Flask-based web application for managing construction inspection processes, including RFIs (Request for Information), ITPs (Inspection Test Plans), and stakeholder management.

## Features

- **User Management**
  - Role-based access control (Admin, Manager, Inspector, Viewer)
  - User authentication and authorization
  - Secure password handling

- **RFI Management**
  - Create, edit, and delete RFIs
  - Track RFI status and details
  - Location-based organization

- **ITP Management**
  - Create and manage Inspection Test Plans
  - Define ITP phases and activities
  - Track verification documents
  - Manage stakeholder responsibilities

- **Stakeholder Management**
  - Add and manage stakeholders
  - Assign stakeholders to users
  - Track stakeholder roles and responsibilities

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ozzybarbozy/construction_inspection_app.git
   cd construction_inspection_app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python seed.py
   ```

## Configuration

1. Create a `config.py` file in the root directory with the following content:
   ```python
   import os

   class Config:
       SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
       SQLALCHEMY_TRACK_MODIFICATIONS = False
   ```

2. Set up environment variables (optional):
   ```bash
   export FLASK_APP=run.py
   export FLASK_ENV=development
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python run.py
   ```

2. Access the application at `http://localhost:5000`

## Default Admin Account

- Username: `admin`
- Password: `admin123`

**Note:** Change the admin password immediately after first login.

## Project Structure

```
construction_inspection_app/
├── app/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── models.py
│   ├── routes.py
│   └── templates/
│       ├── admin/
│       └── ...
├── config.py
├── requirements.txt
├── run.py
└── seed.py
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework
- Bootstrap for UI components
- SQLAlchemy for database management 