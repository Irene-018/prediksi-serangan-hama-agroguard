from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    
    # Library Pencegahan Hama
    path('library/', views.library_view, name='library'),
    path('library/create/', views.library_create, name='library_create'),
    path('library/edit/<int:pk>/', views.library_edit, name='library_edit'),
    path('library/delete/<int:pk>/', views.library_delete, name='library_delete'),
    path('library/detail/<int:pk>/', views.library_detail, name='library_detail'),
]