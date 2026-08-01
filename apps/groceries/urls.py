from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('add/', views.bill_add, name='bill_add'),
    path('<int:bill_id>/edit/', views.bill_edit, name='bill_edit'),
    path('<int:bill_id>/update/', views.bill_update, name='bill_update'),
    path('<int:bill_id>/delete/', views.bill_delete, name='bill_delete'),
    path('extra/', views.extra_list, name='extra_list'),
    path('extra/add/', views.extra_add, name='extra_add'),
    path('extra/<int:extra_id>/edit/', views.extra_edit, name='extra_edit'),
    path('extra/<int:extra_id>/update/', views.extra_update, name='extra_update'),
    path('extra/<int:extra_id>/delete/', views.extra_delete, name='extra_delete'),
]
