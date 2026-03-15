import os
import django
import pandas as pd
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinancialRecord
from core.forecasting import generate_forecast

from django.contrib.auth.models import User

def populate_test_data():
    print("Populating test data...")
    User.objects.filter(username='testuser').delete()
    user = User.objects.create_user(username='testuser', password='password123')
    
    FinancialRecord.objects.all().delete()
    
    # Load from the sample CSV created earlier (simulating the view logic)
    try:
        df = pd.read_csv('sample_data.csv')
        records = []
        for _, row in df.iterrows():
            records.append(FinancialRecord(
                date=row['Date'],
                category=row['Category'].upper(),
                amount=row['Amount'],
                description=row['Description'],
                user=user
            ))
        FinancialRecord.objects.bulk_create(records)
        print(f"Created {len(records)} records for user 'testuser'.")
        return user
    except FileNotFoundError:
        print("sample_data.csv not found!")
        return None

def test_forecasting(user):
    print("\nTesting Forecasting Engine...")
    forecast = generate_forecast(user=user, months=12)
    
    if not forecast:
        print("Forecast returned None!")
        return

    print("Forecast Results (Next 6 Months):")
    print(f"{'Date':<12} | {'Revenue':<10} | {'Expenses':<10} | {'Profit':<10}")
    print("-" * 50)
    for i in range(len(forecast['dates'])):
        d = forecast['dates'][i]
        r = forecast['revenue'][i]
        e = forecast['expenses'][i]
        p = forecast['profit'][i]
        print(f"{d:<12} | {r:<10.2f} | {e:<10.2f} | {p:<10.2f}")

if __name__ == '__main__':
    user = populate_test_data()
    if user:
        test_forecasting(user)
