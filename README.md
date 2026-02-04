# Financial Forecast System

A modern Django web application for tracking financial records and generating forecasts.

## Features
- **Dashboard**: Visual overview of Revenue, Expenses, and Profit (Historical + Forecast).
- **Forecasting Engine**: Uses Linear Regression (Scikit-Learn) to predict future trends.
- **Data Entry**: Manual form entry or CSV upload.
- **Reporting**: Detailed lists and PDF export.
- **Modern UI**: Built with Bootstrap 5 and Chart.js.

## Prerequisites
- Python 3.10+
- Virtualenv (recommended)

## Installation

1. **Install Dependencies**
   ```bash
   # From project root
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # source venv/bin/activate # On Mac/Linux
   
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
2. Open your browser to `http://127.0.0.1:8000/`.

## Using Sample Data
A `sample_data.csv` is provided in the root directory.
1. Go to **Upload Data**.
2. Select `sample_data.csv`.
3. Click **Upload**.
4. Check the **Dashboard** to see the charts and forecasts.

## Project Structure
- `config/`: Django project settings.
- `core/`: Main app containing models, views, and logic.
    - `forecasting.py`: Prediction logic.
    - `views.py`: Request handlers.
    - `models.py`: Database schema.
- `templates/`: HTML files (Bootstrap 5).

## Tech Stack
- Django 5.x
- Pandas & Scikit-Learn
- Chart.js
- Bootstrap 5
