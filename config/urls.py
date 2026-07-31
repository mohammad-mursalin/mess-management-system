from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('meals/', include('meals.urls')),
    path('groceries/', include('groceries.urls')),
    path('bills/', include('bills.urls')),
]
