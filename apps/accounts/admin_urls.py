from django.urls import path
from .views import UserListView, UserDetailView

urlpatterns = [
    path('users/', UserListView.as_view(), name='admin-users-list'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
]