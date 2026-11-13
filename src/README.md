# Mergington High School Activities API

A super simple FastAPI application that allows students to view extracurricular activities and teachers to manage enrollment.

## Features

- View all available extracurricular activities
- Teacher login for managing activity enrollment
- Public activity and participant listings

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                     | Validate teacher credentials using HTTP Basic authentication        |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student enrollment                                     |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only student removal                                    |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activities and signups are stored in memory, so they reset when the server restarts. Teacher credential hashes are stored separately in a local JSON file.

## Teacher accounts

Teacher accounts are provisioned by an administrator; there is no account-maintenance page. From the `src` directory, run:

```
python add_teacher.py <username>
```

The command prompts for a password and stores only a salted PBKDF2 hash in the local, git-ignored `teachers.json` file. `teachers.example.json` shows its format. If the local file is absent, public activity viewing remains available but enrollment management is disabled until an account is provisioned. Restart the app after adding an account. HTTP Basic credentials are held only in the browser until logout or page reload; use HTTPS when deploying beyond local development.

## Tests

Install the FastAPI test client dependency and run the focused API tests:

```
pip install httpx2
python -m unittest discover -s src -p "test_*.py"
```
