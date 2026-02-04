import os
import django
import pandas as pd
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FinancialRecord
from core.forecasting import generate_forecast

def populate_test_data():
    print("Populating test data...")
    FinancialRecord.objects.all().delete()
    
    # Load from the sample CSV created earlier (simulating the view logic)
    try:
        df = pd.read_csv('sample_data.csv')
        records = []
        for _, row in df.iterrows():
            records.append(FinancialRecord(
                date=row['Date'],
                category=row['Category'],
                amount=row['Amount'],
                description=row['Description']
            ))
        FinancialRecord.objects.bulk_create(records)
        print(f"Created {len(records)} records.")
    except FileNotFoundError:
        print("sample_data.csv not found!")

def test_forecasting():
    print("\nTesting Forecasting Engine...")
    forecast = generate_forecast(months=6)
    
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
    populate_test_data()
    test_forecasting()
