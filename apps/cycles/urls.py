from django.urls import path
from . import views

urlpatterns = [
    path('update-fixed-member-rate/', views.update_fixed_member_rate, name='update_fixed_member_rate'),
]
