import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from .models import FinancialRecord

def generate_forecast(user, months=12):
    """
    Generates a forecast for the next `months` months.
    Returns a dictionary with dates and predicted values for Revenue, Expense, and Profit.
    """
    records = FinancialRecord.objects.filter(user=user).order_by('date')

    if not records.exists():
        return None

    df = pd.DataFrame(list(records.values('date', 'category', 'amount')))
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)

    # Group by Month and Category
    df_monthly = df.groupby([pd.Grouper(key='date', freq='ME'), 'category'])['amount'].sum().reset_index()

    forecast_data = {
        'dates': [],
        'revenue': [],
        'expenses': [],
        'profit': []
    }

    last_date = df_monthly['date'].max()
    future_dates = [last_date + relativedelta(months=i) for i in range(1, months + 1)]
    forecast_data['dates'] = [d.strftime('%Y-%m-%d') for d in future_dates]

    for category in ['REVENUE', 'EXPENSE']:
        cat_df = df_monthly[df_monthly['category'] == category]
        
        if len(cat_df) < 2:
            # Not enough data to forecast, return empty or zeros
            predictions = [0] * months
        else:
            # Prepare data for Linear Regression
            cat_df = cat_df.sort_values('date')
            cat_df['ordinal_date'] = cat_df['date'].map(pd.Timestamp.toordinal)
            
            X = cat_df[['ordinal_date']]
            y = cat_df['amount']
            
            model = LinearRegression()
            model.fit(X, y)
            
            future_X = pd.DataFrame({'ordinal_date': [d.toordinal() for d in future_dates]})
            predictions = model.predict(future_X)
            predictions = [max(0, p) for p in predictions] # No negative values for simple forecast

        key = 'revenue' if category == 'REVENUE' else 'expenses'
        forecast_data[key] = predictions

    # Calculate Profit
    forecast_data['profit'] = [r - e for r, e in zip(forecast_data['revenue'], forecast_data['expenses'])]

    return forecast_data
