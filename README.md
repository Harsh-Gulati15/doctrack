# DocTrack: AI-Assisted Document Inward & Workflow Tracking System

DocTrack is a comprehensive web-based application designed to digitize, categorize, and track physical documents as they flow through an organization. It leverages OCR and AI (Google Gemini) to automate data entry, intelligently route documents to appropriate departments, and enforce SLAs for document processing.

## Features

- **Document Registration:** Receptionists can quickly log incoming documents (courier, speed post, hand delivery).
- **OCR Processing:** Automatically extract text from scanned PDFs and images using Tesseract OCR.
- **AI Categorisation & Routing:** Utilizes Google Gemini to analyze document text and suggest the appropriate document type and target department.
- **Workflow & SLA Tracking:** Route documents between departments and track SLA deadlines to ensure timely processing.
- **Acknowledgments & Escalations:** Users acknowledge receipt of documents; automated escalations trigger if SLAs are breached.
- **Audit Trails:** Comprehensive logging of all actions and state changes for compliance and tracking.

## Tech Stack

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF)
- **Database:** MySQL 8.0
- **Frontend:** HTML5, Bootstrap 5.3, Jinja2
- **Document Processing:** Tesseract OCR, Poppler (pdf2image), pdfplumber
- **AI/ML:** Google Gemini API

## Prerequisites

- Python 3.10+
- MySQL 8.0
- Tesseract OCR 5.x
- Poppler (for PDF processing)
- Google Gemini API key

## Installation on Windows

Follow these step-by-step instructions to set up DocTrack locally:

1. **Install Python 3.10+** from python.org

2. **Install MySQL 8.0**
   - Download from mysql.com
   - Create database:
   ```sql
   CREATE DATABASE doctrack_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Install Tesseract OCR on Windows**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run the installer (default path: `C:\Program Files\Tesseract-OCR`)
   - Add to PATH or set `TESSERACT_PATH` in `.env`
   - Verify: open cmd and run `tesseract --version`

4. **Install Poppler for Windows**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract to `C:\poppler`
   - Set `POPPLER_PATH` in `.env` to the bin directory: `C:\poppler\Library\bin`

5. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd doctrack
   ```

6. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

7. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: WeasyPrint requires GTK libraries on Windows. Install from: https://github.com/nickvdyck/weasyprint-win*

8. **Configure environment**
   - Copy `.env.example` to `.env` (or edit `.env`)
   - Set all required variables:
     - `FLASK_SECRET_KEY` (generate a random key)
     - MySQL credentials
     - `GEMINI_API_KEY` (from Google AI Studio)
     - Mail settings (optional)
     - `TESSERACT_PATH`
     - `POPPLER_PATH`

9. **Seed the database**
   ```bash
   python seed.py
   ```

10. **Run the application**
    ```bash
    python run.py
    ```
    Open http://localhost:5000 in your browser.

## Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Super Admin | admin | admin123 |
| Receptionist | receptionist | user123 |
| Finance Dept | fin_user | user123 |
| HR Dept | hr_user | user123 |
| IT Dept | it_user | user123 |

## User Roles

- **Receptionist:** Responsible for registering incoming documents, uploading files, and initiating the workflow.
- **Department User (`dept_user`):** Reviews documents routed to their department, acknowledges receipt, and manages the document workflow.
- **Admin / Super Admin:** Manages users, departments, system configurations, and monitors system-wide SLAs and audit logs.

## Project Structure

```
doctrack/
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes/              # Application blueprints
│   ├── templates/           # Jinja2 templates (Bootstrap 5.3)
│   ├── static/              # CSS, JS, and image assets
│   └── utils/               # OCR, AI, and helper functions
│
├── uploads/                 # Directory for uploaded documents
├── venv/                    # Python virtual environment
├── .env                     # Environment variables configuration
├── config.py                # Configuration classes
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── seed.py                  # Database seeding script
└── README.md                # Project documentation
```

## Troubleshooting

- **Tesseract not found:** Ensure Tesseract is installed and `TESSERACT_PATH` is correctly set in `.env` (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- **Poppler not found:** Check if `POPPLER_PATH` is set correctly pointing to the `bin` folder.
- **MySQL connection error:** Verify database credentials in `.env` and ensure the MySQL server is running.
- **WeasyPrint issues on Windows:** Ensure GTK libraries are installed properly.
- **Gemini API errors:** Verify that `GEMINI_API_KEY` is set and valid.

## License

MIT License
