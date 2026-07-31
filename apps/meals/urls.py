from django.urls import path
from . import views

urlpatterns = [
    path('entry-grid/', views.entry_grid, name='entry_grid'),
    path('meal-cell-update/', views.meal_cell_update, name='meal_cell_update'),
]
