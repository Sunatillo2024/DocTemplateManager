from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name='user/dashboard.html')), name='dashboard'),
    path('login/', TemplateView.as_view(template_name='auth/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='auth/register.html'), name='register'),
    path('fill/<uuid:template_id>/', login_required(TemplateView.as_view(template_name='user/fill_form.html')), name='fill-form'),
    path('my-documents/', login_required(TemplateView.as_view(template_name='user/my_documents.html')), name='my-documents'),
    # Админские страницы – позже добавим проверку прав
    path('admin/', login_required(TemplateView.as_view(template_name='admin/dashboard.html')), name='admin-dashboard'),
    path('admin/templates/', login_required(TemplateView.as_view(template_name='admin/templates.html')), name='admin-templates'),
    path('admin/templates/create/', login_required(TemplateView.as_view(template_name='admin/template_form.html')), name='admin-template-create'),
    path('admin/templates/<uuid:template_id>/edit/', login_required(TemplateView.as_view(template_name='admin/template_form.html')), name='admin-template-edit'),
    path('admin/users/', login_required(TemplateView.as_view(template_name='admin/users.html')), name='admin-users'),
]