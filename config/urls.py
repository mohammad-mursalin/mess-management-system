from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('apps.dashboard.urls')),
    path('meals/', include('apps.meals.urls')),
    path('groceries/', include('apps.groceries.urls')),
    path('bills/', include('apps.bills.urls')),
    path('members/', include('apps.members.urls')),
    path('cycles/', include('apps.cycles.urls')),
]
