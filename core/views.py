import csv
import io
import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FinancialRecord
from .forms import RecordForm, UploadFileForm
from .forecasting import generate_forecast
from .suggestions_engine import generate_suggestions
import json
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from xhtml2pdf import pisa


@login_required
def dashboard(request):
    # Historical Data
    records = FinancialRecord.objects.filter(user=request.user).order_by('date')

    
    # Simple summary metrics
    total_revenue = sum(r.amount for r in records if r.category == 'REVENUE')
    total_expenses = sum(r.amount for r in records if r.category == 'EXPENSE')
    net_profit = total_revenue - total_expenses
    
    # Prepare chart data (Historical)
    df = pd.DataFrame(list(records.values('date', 'category', 'amount')))
    historical_chart_data = {'dates': [], 'revenue': [], 'expenses': [], 'profit': []}

    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = df['amount'].astype(float)
        monthly = df.groupby([pd.Grouper(key='date', freq='ME'), 'category'])['amount'].sum().reset_index()
        
        # Pivot to align dates
        pivot = monthly.pivot(index='date', columns='category', values='amount').fillna(0)
        historical_chart_data['dates'] = [d.strftime('%Y-%m-%d') for d in pivot.index]
        historical_chart_data['revenue'] = pivot.get('REVENUE', pd.Series([0]*len(pivot))).tolist()
        historical_chart_data['expenses'] = pivot.get('EXPENSE', pd.Series([0]*len(pivot))).tolist()
        historical_chart_data['profit'] = (pivot.get('REVENUE', 0) - pivot.get('EXPENSE', 0)).tolist()

    # Forecast Data (Next 12 Months)
    forecast_data = generate_forecast(user=request.user, months=12)

    # Specific Next Month Forecast
    next_month_forecast = {
        'revenue': 0,
        'expenses': 0,
        'profit': 0,
        'date': ''
    }
    
    if forecast_data and forecast_data['dates']:
        next_month_forecast['date'] = forecast_data['dates'][0]
        next_month_forecast['revenue'] = forecast_data['revenue'][0]
        next_month_forecast['expenses'] = forecast_data['expenses'][0]
        next_month_forecast['profit'] = forecast_data['profit'][0]

    # Prepare Monthly Breakdown for Table
    monthly_forecasts = []
    if forecast_data and forecast_data['dates']:
        for i in range(len(forecast_data['dates'])):
            monthly_forecasts.append({
                'date': datetime.strptime(forecast_data['dates'][i], '%Y-%m-%d'),
                'revenue': forecast_data['revenue'][i],
                'expenses': forecast_data['expenses'][i],
                'profit': forecast_data['profit'][i],
            })

    # Generate Suggestions
    suggestions_data = generate_suggestions(user=request.user, forecast_data=forecast_data)

    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'historical_chart_data': json.dumps(historical_chart_data),
        'forecast_data': json.dumps(forecast_data) if forecast_data else json.dumps({}),
        'next_month_forecast': next_month_forecast,
        'annual_projection': forecast_data.get('annual_projection') if forecast_data else None,
        'monthly_forecasts': monthly_forecasts,
        'suggestions_data': suggestions_data,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_record(request):

    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()

            messages.success(request, 'Record added successfully!')
            return redirect('dashboard')
    else:
        form = RecordForm()
    return render(request, 'add_record.html', {'form': form})

@login_required
def upload_data(request):

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            
            # Simple CSV Parsing
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                records = []
                for row in reader:
                    # Expecting columns: Date, Category, Amount, Description
                    # Basic validation and mapping needed
                    records.append(FinancialRecord(
                        date=row.get('Date'),
                        category=row.get('Category').upper(), # Ensure correct case
                        amount=float(row.get('Amount', 0)),
                        description=row.get('Description', ''),
                        user=request.user
                    ))

                
                FinancialRecord.objects.bulk_create(records)
                messages.success(request, f'Successfully uploaded {len(records)} records.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def report_list(request):
    records = FinancialRecord.objects.filter(user=request.user).order_by('-date')

    return render(request, 'reports.html', {'records': records})

@login_required
def export_pdf(request):
    records = FinancialRecord.objects.filter(user=request.user).order_by('-date')

    template_path = 'reports.html'
    context = {'records': records}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to your dashboard.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
