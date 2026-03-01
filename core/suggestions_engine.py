import pandas as pd
from datetime import datetime
from .models import FinancialRecord

def generate_suggestions(user, forecast_data=None):
    """
    Analyzes historical data and forecast to provide summaries and suggestions.
    """
    records = FinancialRecord.objects.filter(user=user).order_by('date')
    if not records.exists():
        return {
            'summary': "No data available to generate a summary.",
            'suggestions': ["Start by adding your historical revenue and expenses."]
        }

    df = pd.DataFrame(list(records.values('date', 'category', 'amount')))
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)

    # Current month vs Previous month
    df_monthly = df.groupby([pd.Grouper(key='date', freq='ME'), 'category'])['amount'].sum().reset_index()
    pivot = df_monthly.pivot(index='date', columns='category', values='amount').fillna(0)
    
    # Summary logic
    summary = []
    suggestions = []

    if len(pivot) >= 2:
        last_month = pivot.iloc[-1]
        prev_month = pivot.iloc[-2]

        last_rev = last_month.get('REVENUE', 0)
        prev_rev = prev_month.get('REVENUE', 0)
        last_exp = last_month.get('EXPENSE', 0)
        prev_exp = prev_month.get('EXPENSE', 0)

        # Revenue Analysis
        if last_rev > prev_rev:
            summary.append(f"Revenue is up by {((last_rev-prev_rev)/prev_rev*100):.1f}% compared to last month.")
        elif last_rev < prev_rev:
            summary.append(f"Revenue has decreased by {((prev_rev-last_rev)/prev_rev*100):.1f}% since last month.")
            suggestions.append("Analyze customer churn or sales strategy to reverse the revenue decline.")

        # Expense Analysis
        if last_exp > prev_exp:
            summary.append(f"Expenses have increased by {((last_exp-prev_exp)/prev_exp*100):.1f}% recently.")
            suggestions.append("Audit recent expenses to identify any unnecessary costs or 'subscription creep'.")
        elif last_exp < prev_exp:
            summary.append("You've successfully reduced your expenses compared to last month.")

        # Profit Margin
        last_profit = last_rev - last_exp
        if last_rev > 0:
            margin = (last_profit / last_rev) * 100
            summary.append(f"Your current profit margin is {margin:.1f}%.")
            if margin < 10:
                suggestions.append("Your profit margin is low. Consider increasing prices or streamlining operations to reduce costs.")
    else:
        summary.append("Gathering more data for a better month-over-month comparison.")

    # Forecast-based suggestions
    if forecast_data:
        future_profit = sum(forecast_data['profit'][:3]) / 3 # Simple 3-month avg
        current_profit = (pivot.iloc[-1].get('REVENUE', 0) - pivot.iloc[-1].get('EXPENSE', 0)) if not pivot.empty else 0
        
        if future_profit < current_profit:
            summary.append("The forecast indicates a potential decline in profits over the next few months.")
            suggestions.append("Proactively look for ways to boost sales or cut overhead before the predicted decline occurs.")

    # Generic beneficial suggestions if list is short
    if len(suggestions) < 3:
        suggestions.append("Ensure regular data entry for more accurate forecasting.")
        suggestions.append("Categorize your expenses more clearly to pinpoint where most of your money goes.")

    return {
        'summary_points': summary,
        'suggestions': suggestions
    }
