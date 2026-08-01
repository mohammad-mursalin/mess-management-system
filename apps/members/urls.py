from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('add/', views.add_member, name='add_member'),
    path('edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('toggle/<int:member_id>/', views.toggle_member_active, name='toggle_member_active'),
]
