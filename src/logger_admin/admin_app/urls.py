from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_logs_view, name="admin_logs"),
    path("reset_blocks/", views.reset_blocks_view, name="reset_blocks"),
]
