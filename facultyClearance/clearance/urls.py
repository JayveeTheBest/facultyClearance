from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_clearance_document, name='upload_clearance_document'),
    path('upload/success/', views.upload_success, name='upload_success'),
]
