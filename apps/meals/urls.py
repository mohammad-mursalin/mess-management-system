from django.urls import path
from . import views

urlpatterns = [
    path('entry-grid/', views.entry_grid, name='entry_grid'),
    path('entry-grid-body/', views.entry_grid_body, name='entry_grid_body'),
    path('meal-cell-update/', views.meal_cell_update, name='meal_cell_update'),
]
