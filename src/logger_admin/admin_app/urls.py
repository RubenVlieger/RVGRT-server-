from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_logs_view, name='admin_logs'),
]
