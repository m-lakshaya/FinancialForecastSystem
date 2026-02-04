from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_record, name='add_record'),
    path('upload/', views.upload_data, name='upload_data'),
    path('reports/', views.report_list, name='reports'),
    path('reports/pdf/', views.export_pdf, name='export_pdf'),
]
