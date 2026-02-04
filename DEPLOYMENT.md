# Deployment Guide

Follow these steps to move and run the **Financial Forecast System** on another computer.

## 1. Prepare the Files
If you are moving the project by copying a folder (USB, Zip, etc.):
1. **Copy** the entire `FinancialForecastSystem` folder.
2. **Exclude** the `venv` folder. It is specific to your current machine and will be recreated.
3. **(Optional)** Exclude `db.sqlite3` if you want a fresh database. Keep it if you want to transfer your existing data.

## 2. Install Prerequisites
On the new computer, ensure you have:
- **Python 3.10 or higher** installed.

## 3. Setup on the New Machine
Open a terminal (Command Prompt or PowerShell) in the project folder on the new machine.

### Windows
```powershell
# 1. Create a new virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize Database (Only if you didn't copy db.sqlite3)
python manage.py migrate

# 5. Run the server
python manage.py runserver
```

### Mac / Linux
```bash
# 1. Create a new virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize Database (Only if you didn't copy db.sqlite3)
python manage.py migrate

# 5. Run the server
python manage.py runserver
```

## 4. Access the App
Open your browser and verify it works at:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)
