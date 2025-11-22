from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
<<<<<<< HEAD
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # User Management
    path('kelola-user/', views.kelola_user_view, name='kelola_user'),
    path('tambah-user/', views.tambah_user_view, name='tambah_user'),
    path('edit-user/<int:id>/', views.edit_user_view, name='edit_user'),
    path('hapus-user/<int:id>/', views.hapus_user_view, name='hapus_user'),
    
    # Hama Management
    path('data-hama/', views.data_hama_view, name='data_hama'),
    path('tambah-hama/', views.tambah_hama_view, name='tambah_hama'),
    path('edit-hama/<int:id>/', views.edit_hama_view, name='edit_hama'),
    path('hapus-hama/<int:id>/', views.hapus_hama_view, name='hapus_hama'),
    
    # Pencegahan Management
    path('data-pencegahan/', views.data_pencegahan_view, name='data_pencegahan'),
    path('tambah-pencegahan/', views.tambah_pencegahan_view, name='tambah_pencegahan'),
    path('edit-pencegahan/<int:id>/', views.edit_pencegahan_view, name='edit_pencegahan'),
    path('hapus-pencegahan/<int:id>/', views.hapus_pencegahan_view, name='hapus_pencegahan'),
    
    # Lahan Management
    path('data-lahan/', views.data_lahan_view, name='data_lahan'),
    path('tambah-lahan/', views.tambah_lahan_view, name='tambah_lahan'),
    path('edit-lahan/<int:id>/', views.edit_lahan_view, name='edit_lahan'),
]
=======
    path('', views.dashboard_view, name='dashboard'),
    path('kelola-user/', views.kelola_user_view, name='kelola_user'),
    path('tambah-user/', views.tambah_user_view, name='tambah_user'),
    path('edit-user/<int:id>/', views.edit_user_view, name='edit_user'),

    path('data-hama/', views.data_hama_view, name='data_hama'),
    path('tambah-hama/', views.tambah_hama_view, name='tambah_hama'),       # <-- tambah ini
    path('edit-hama/<int:id>/', views.edit_hama_view, name='edit_hama'),    # <-- dan ini (opsional)
    path('data-pencegahan/', views.data_pencegahan_view, name='data_pencegahan'),
    path('tambah-pencegahan/', views.tambah_pencegahan_view, name='tambah_pencegahan'),  # ⬅️ tambahkan ini

    path('data-lahan/', views.data_lahan_view, name='data_lahan'),
    path('tambah-lahan/', views.tambah_lahan_view, name='tambah_lahan'),
    path('edit-lahan/<int:id>/', views.edit_lahan_view, name='edit_lahan'),
]
>>>>>>> 002ca9f904786c4b20dacc25f539d698733278cc
