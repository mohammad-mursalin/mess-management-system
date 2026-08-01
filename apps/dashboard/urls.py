from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard_home'),
    path('month-summary/', views.month_summary, name='month_summary'),
]
