from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='fixed_bill_list'),
    path('add/', views.bill_add, name='fixed_bill_add'),
    path('<int:bill_id>/edit/', views.bill_edit, name='fixed_bill_edit'),
    path('<int:bill_id>/update/', views.bill_update, name='fixed_bill_update'),
    path('<int:bill_id>/delete/', views.bill_delete, name='fixed_bill_delete'),
]
