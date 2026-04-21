# EventIQ Local Setup Guide

Follow these steps to set up and run the EventIQ project on your local machine.

## Prerequisites
- **Python 3.10+** installed on your system.
- **Git** (if you are cloning the repository).
- A Gemini API Key from Google AI Studio.

## Installation Steps

### 1. Clone the Repository
Clone the project to your local machine and navigate into the project directory:
```bash
git clone <repository_url>
cd myproject
```
*(If you already have the files locally, just open your terminal and navigate to the `myproject` folder containing `manage.py`.)*

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage your project's dependencies:
```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment
Activate the environment so that packages are installed locally rather than globally.

- **On macOS and Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **On Windows:**
  ```cmd
  .venv\Scripts\activate
  ```

### 4. Install Dependencies
Install all the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
The application requires certain environment variables (like the Gemini API Key) to function properly. 

Create a `.env` file in the same directory as `manage.py` (the root of the project source code) and add your keys:
```env
# .env
DEBUG=True
SECRET_KEY=your_django_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
*Note: Make sure to replace `your_gemini_api_key_here` with your actual Google Gemini API key.*

### 6. Apply Database Migrations
EventIQ uses SQLite by default. To create the database tables, run the following commands:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Run the Development Server
Finally, start the Django development server:
```bash
python manage.py runserver
```

### 8. Access the Application
Open your web browser and navigate to:
[http://localhost:8000/](http://localhost:8000/)

You should now see the EventIQ application running locally!

---
## Troubleshooting
- **"ModuleNotFoundError"**: Make sure you have activated your virtual environment before running the server or installing dependencies.
- **"Command 'python' not found"**: On some systems, try using `python3` instead of `python`.
