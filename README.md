# EventIQ - AI-Powered Event Management & budget Planner

EventIQ is a comprehensive web application for managing events, booking tickets, and planning monthly budgets with AI assistance. It features a modern, responsive UI and a robust Django backend.

## 🛠 Tech Stack

-   **Backend**: Python, Django Framework.
-   **Database**: SQLite (Default Django DB).
-   **Frontend**: HTML5, CSS3 (Custom "Outfit" Design System), JavaScript (Vanilla).
-   **Libraries**:
    -   `django`: Web framework.
    -   `qrcode`: For generating unique ticket QR codes.
    -   `Pillow`: Image processing for QR code generation.

## � Environment & Libraries

You may notice other folders and files in your environment (e.g., inside `venv/` or `lib/`). Here's what they do:

-   **`venv/` (Virtual Environment)**: An isolated container for this project's dependencies. It ensures libraries installed here don't conflict with other projects on your system.
    -   **`lib/python3.12/`**: Contains the standard Python library (built-in modules like `os`, `sys`, `datetime`) and the version specific files.
    -   **`site-packages/`**: The specific folder where third-party libraries (like Django) are installed.

### Key Dependencies Explained
-   **`django`**: The high-level Python web framework that powers the entire backend, handling URLs, database interactions, and HTML rendering.
-   **`asgiref`**: (ASGI Reference) A standard Python library that allows Django to handle **Asynchronous** requests (like chat features or background tasks). It is a core dependency installed automatically with Django.
-   **`sqlparse`**: A non-validating SQL parser for Python, used by Django to pretty-print SQL queries (often seen when debugging).
-   **`tzdata`**: Provides timezone data, essential for Django's accurate date/time handling across different regions.

## �📂 Project Structure

The project is organized into the following key directories:

-   `myproject/`: Core project configuration.
    -   `settings.py`: Global settings (Apps, Database, Static files).
    -   `urls.py`: Main URL routing key map.
    -   `views.py`: **Core Logic Center**. Contains all view functions including AI Agent, Booking, and Event handling.
-   `app1/`: Main application app.
    -   `models.py`: Database Models definition.
    -   `admin.py`: Admin interface configuration.
-   `templates/`: HTML Templates.
    -   `ai_agent.html`: **(New)** Split-screen interface for AI Planning & Expense Dashboard.
    -   `events.html`, `create_event.html`: Event management pages.
    -   `booking.html`, `ticket.html`: Booking flow and QR ticket display.
    -   `base.html`: Base template with navigation and common layout.
-   `static/`: Static assets.
    -   `style.css`: Comprehensive CSS variables and styling rules.
    -   `site.js`: Common JavaScript interactions.

## 📝 Important Files & Logic

### 1. Backend Logic
-   **`app1/models.py`**: Defines the data structure.
    -   **`Event`**: Stores event details (Title, Date, Location).
    -   **`Booking`**: Stores user bookings with unique `UUID` and `short_code`.
    -   **`Expense`**: **(New)** Tracks user expenses for the Budget Planner.
-   **`myproject/views.py`**: Handles user requests.
    -   **`ai_agent` View**:
        -   Processes "Ask AI Agent" requests by filtering events based on user input (Interest + Budget).
        -   Calculates monthly and yearly expense totals dynamically.
        -   Handles "Add Expense" form submissions.
    -   **`booking_confirmation`**: Generates a QR code image on-the-fly using `qrcode` and `BytesIO`.

### 2. Frontend Interface
-   **`templates/ai_agent.html`**:
    -   Features a **Split-Pane Design**:
        -   **Left**: AI Event Planner (Form + Dynamic Suggestions).
        -   **Right**: Expense Dashboard (Live Stats, Quick Add Form, Transaction List).
    -   Utilizes Django Template Language (DTL) to render data passed from `views.py`.

## 🚀 Key Features

1.  **Event Management**: Create and list events with dates and descriptions.
2.  **Smart Booking**: Users can book events, receiving a digital ticket with a scannable QR code.
3.  **Ticket Verification (Live Scanner)**:
    -   **Camera Scanning**: Real-time QR code detection using the device's camera.
    -   **Image Upload**: Verify tickets by uploading screenshots or photos.
    -   **Manual Entry**: Supports unique ticket IDs and short codes.
4.  **AI Budget Agent**:
    -   Users input interests (e.g., "Tech") and budget.
    -   The system intelligently suggests matching events from the database.
5.  **Expense Tracking**: A built-in dashboard to track personal spending alongside event planning.
6.  **Ticket Verification**: dedicated scanner page/API to verify ticket validity.
