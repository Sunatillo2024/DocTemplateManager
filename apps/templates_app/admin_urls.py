from django.urls import path
from .views import AdminTemplateListView, AdminTemplateDetailView

urlpatterns = [
    path('templates/', AdminTemplateListView.as_view(), name='admin-template-list'),
    path('templates/<uuid:pk>/', AdminTemplateDetailView.as_view(), name='admin-template-detail'),
]