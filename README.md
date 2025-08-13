# CodeXray

CodeXray is a Django-based code analysis platform that includes:
- **GitHub Analyzer**: Analyze repositories and get insights about files and functions.
- **Bug Detector**: Debug code in multiple languages, get AI-powered corrections, and save history.

## Features
- GitHub repository analysis
- File-level function mapping
- AI-powered code bug detection
- Module-specific history tracking
- Glassmorphism + Neon styled UI

## Installation

1. Clone the repository:
\
git clone https://github.com/<your-username>/<repo-name>.git
   cd codexray
   
2. Create a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

    pip install -r requirements.txt

4. Set up the database:

    python manage.py migrate
    Create a superuser:
    python manage.py createsuperuser

5. Run the development server:

    python manage.py runserver

Usage
Access GitHub Analyzer from /github-analyzer/

Access Bug Detector from /bug-detector/

View Bug Detector history at /bug-detector/history/

Requirements
See requirements.txt

License
This project is licensed under the MIT License.
