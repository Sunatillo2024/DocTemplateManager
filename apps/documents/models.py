import uuid
from django.db import models
from apps.accounts.models import User
from apps.templates_app.models import Template

def output_upload_path(instance, filename):
    # Путь: outputs/<uuid>_<original_name>
    return f'outputs/{instance.id}_{filename}'

class FilledDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='filled_documents')
    filled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='filled_documents')
    filled_data = models.JSONField(default=dict)  # словарь ключ-значение
    output_file = models.FileField(upload_to=output_upload_path, blank=True, null=True)
    output_format = models.CharField(max_length=4, choices=[('pdf', 'PDF'), ('docx', 'DOCX')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заполненный документ'
        verbose_name_plural = 'Заполненные документы'

    def __str__(self):
        return f'{self.template.title} - {self.filled_by.email if self.filled_by else "Аноним"}'