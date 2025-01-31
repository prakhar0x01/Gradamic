from django.urls import path
from . import views

urlpatterns = [
    path('', views.materials_list, name='materials_list'),
    path('<int:pk>/', views.material_detail, name='material_detail'),
    path('<int:pk>/download/', views.download_notes, name='download_notes'),
]