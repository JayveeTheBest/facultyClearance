from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inline-upload/<int:req_id>/', views.inline_upload, name='inline_upload'),
    path('upload/<int:req_id>/', views.upload, name='upload'),
    path('reupload/<int:req_id>/', views.reupload, name='reupload'),
    path('upload/success/', views.upload_success, name='upload_success'),
    path('approvals/', views.approvals, name='approvals'),
    path('approvals/<int:upload_id>/approve/', views.approve_upload, name='approve_upload'),
    path('approvals/<int:upload_id>/reject/', views.reject_upload, name='reject_upload'),
    path('submissions/', views.submissions, name='submissions'),
]
