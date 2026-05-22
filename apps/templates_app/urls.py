from django.urls import path
from .views import TemplateListView, TemplateDetailView, TemplateFillView

urlpatterns = [
    path('', TemplateListView.as_view(), name='template-list'),
    path('<uuid:pk>/', TemplateDetailView.as_view(), name='template-detail'),
    path('<uuid:pk>/fill/', TemplateFillView.as_view(), name='template-fill'),
]