import csv
import io
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FinancialRecord
from .forms import RecordForm, UploadFileForm
from .forecasting import generate_forecast
import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def dashboard(request):
    # Historical Data
    records = FinancialRecord.objects.all().order_by('date')
    
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
    forecast_data = generate_forecast(months=12)

    context = {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'historical_chart_data': json.dumps(historical_chart_data),
        'forecast_data': json.dumps(forecast_data) if forecast_data else json.dumps({}),
    }
    return render(request, 'dashboard.html', context)

def add_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record added successfully!')
            return redirect('dashboard')
    else:
        form = RecordForm()
    return render(request, 'add_record.html', {'form': form})

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
                        description=row.get('Description', '')
                    ))
                
                FinancialRecord.objects.bulk_create(records)
                messages.success(request, f'Successfully uploaded {len(records)} records.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error processing file: {e}')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def report_list(request):
    records = FinancialRecord.objects.all().order_by('-date')
    return render(request, 'reports.html', {'records': records})

def export_pdf(request):
    records = FinancialRecord.objects.all().order_by('-date')
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

