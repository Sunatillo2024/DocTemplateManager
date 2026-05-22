from django.urls import path
from .views import DocumentListView, DocumentDownloadView

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list'),
    path('<uuid:pk>/', DocumentDownloadView.as_view(), name='document-download'),
]