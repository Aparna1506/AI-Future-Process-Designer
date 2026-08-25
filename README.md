# AI Future Process Designer

## Overview

AI Future Process Designer is a web application that shows how AI and automation can be used to improve hospital processes.

For this project, I focused on hospital operations and looked at how common activities can be improved using AI while keeping important decisions with hospital staff.

The application breaks a hospital process into smaller steps and shows:

**Current Process → Problems → AI Opportunities → Future Process → Benefits**

The information is stored in a structured database so that each part of the process can be viewed and compared separately.

This project is a prototype created using sample healthcare process data. It is not connected to a real hospital system and is not intended for clinical decision-making.

---

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- FastAPI
- SQLAlchemy

### Database
- SQLite

### API Documentation
- FastAPI Swagger / OpenAPI

---

## Features

- View hospital processes
- Break processes into individual activities
- Identify problems in the current process
- Map problems to possible AI opportunities
- Compare current and future activities
- Show human, AI and hybrid responsibilities
- View expected process improvements
- Access the backend through REST APIs
- Explore and test APIs through FastAPI Swagger documentation
---

## Project Design

The project follows the complete process from the current situation to the expected result:

**Current Process → Activities → Problems → AI Opportunities → Future Process → Responsibility → Benefits**

Each part is stored separately in the database. This makes the information easier to update, compare, and query.

### Current and Future Process

The application keeps the current activities and future activities separate. A transformation record connects them and shows what happened to each activity.

An activity can be:

* Automated
* Improved with AI
* Removed
* Newly added
* Kept unchanged

### Human and AI Responsibility

Each future activity has a responsibility level:

* **Human** — handled by hospital staff
* **AI** — handled by the system
* **Hybrid** — AI assists, but a person makes the final decision

This is especially important for healthcare because important decisions should remain with qualified staff.

### Expected Benefits

The project stores before-and-after values for areas such as:

* Time
* Cost
* Quality
* Compliance
* Patient experience

The application can then show the expected change instead of only describing the benefit in words.

## Architecture

The application has three main parts:

```text
┌─────────────────────────┐
│       Frontend          │
│      HTML / CSS / JS    │
└────────────┬────────────┘
             │
          REST API
             │
             ▼
┌─────────────────────────┐
│       FastAPI           │
│   Backend / API Logic   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        SQLite           │
│        Database         │
└─────────────────────────┘
```

The frontend is used to view and compare the processes. The FastAPI backend handles the requests and retrieves the required information. SQLite stores the project data.

### Data Model

The main relationships in the database are:

```text
Industry
   │
   └── Process
         │
         ├── Activity
         │     └── Problem
         │           └── AI Opportunity
         │
         ├── Future Activity
         │
         ├── Transformation
         │
         └── Benefit

Role ─────────── Activity / Future Activity

System ───────── Activity / Future Activity
```

The database uses separate tables and relationships instead of keeping the complete process as one large text field. This allows individual activities, problems, AI opportunities, future activities, and benefits to be accessed separately.


## API

Base URL:

```text
http://localhost:8000
```

### Main Routes

| Method | Route                               | Purpose                                 |
| ------ | ----------------------------------- | --------------------------------------- |
| GET    | `/`                                 | Check that the API is running           |
| GET    | `/docs`                             | Open the FastAPI documentation          |
| GET    | `/industries`                       | View available industries and processes |
| GET    | `/processes`                        | View all hospital processes             |
| GET    | `/processes/{id}`                   | View one process                        |
| GET    | `/processes/{id}/activities`        | View current activities                 |
| GET    | `/processes/{id}/problems`          | View problems in a process              |
| GET    | `/processes/{id}/ai-opportunities`  | View possible AI solutions              |
| GET    | `/processes/{id}/future-activities` | View the future process                 |
| GET    | `/processes/{id}/transformations`   | Compare current and future activities   |
| GET    | `/processes/{id}/benefits`          | View expected benefits                  |
| GET    | `/processes/{id}/reasoning-chain`   | View the complete process chain         |
| GET    | `/processes/{id}/compare`           | View the current-to-future comparison   |
| POST   | `/processes/{id}/activities`        | Add a current activity                  |
| POST   | `/activities/{id}/problems`         | Add a problem to an activity            |
| POST   | `/problems/{id}/ai-opportunities`   | Add an AI opportunity                   |

The `/docs` page is provided by FastAPI and can be used to test the API endpoints.

## Running the Project Locally

### 1. Start the Backend

Open a terminal and go to the backend folder:

```bash
cd backend
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create the sample database:

```bash
python seed.py
```

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### 2. Start the Frontend

Open another terminal and go to the frontend folder:

```bash
cd frontend
```

Start the local server:

```bash
python -m http.server 8080
```

Open the application at:

```text
http://localhost:8080
```

## Deployment

The application is deployed on Render for demonstration purposes.

Live application:

https://ai-future-process-designer-2.onrender.com/

The backend uses FastAPI and the frontend communicates with it through REST API requests.

### Backend

The backend can be hosted on a service such as Render.

The backend needs:

* Python
* FastAPI
* SQLAlchemy
* SQLite

The start command is:

```bash
python seed.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend

The frontend contains static HTML, CSS and JavaScript files, so it can be hosted on services such as Netlify, Vercel or GitHub Pages.

After deploying the backend, the frontend API address needs to be updated to the deployed backend URL.


## Project Structure

```text
AI_Healthcare_Project/
│
├── backend/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── seed.py
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
└── README.md
```


## Data Used

The project uses sample hospital process data.

The data includes information about:

* Hospital processes
* Current activities
* Problems
* AI opportunities
* Future activities
* Human and AI responsibilities
* Systems used
* Expected benefits
* Current-to-future transformations

The data is stored locally in SQLite.

No real patient information is used.


## AI Approach

The project uses a structured approach to identify where AI and automation could be useful in hospital processes.

The process is represented as:

Current Activity
       ↓
Problem
       ↓
AI Opportunity
       ↓
Future Activity
       ↓
Human / AI Responsibility
       ↓
Expected Benefit

For healthcare-related activities, the final decision remains with the appropriate hospital staff where required.

## Limitations

This is a prototype and has some limitations:

* The project uses sample data.
* It is not connected to a real hospital system.
* The expected benefits are estimates.
* There is no real patient data.
* Authentication and user management are not included.
* The project does not make clinical decisions.

## Future Improvements

If the project were developed further, I would add:

* User authentication
* More hospital processes
* More detailed reporting
* Charts for process improvements
* Audit logs
* Integration with hospital systems
* Better monitoring and error reporting
* More detailed evaluation of AI opportunities

## Conclusion

The project demonstrates how a hospital process can be broken down into smaller activities, problems and possible AI improvements.

The main focus is on making the reasoning structured and easy to understand rather than keeping it as large blocks of text.

The same approach could later be used for other industries by changing the process data and business rules.


## Project Links

**Live Application:**  
https://ai-future-process-designer-2.onrender.com/

**GitHub Repository:**  
https://github.com/Aparna1506/AI-Future-Process-Designer


