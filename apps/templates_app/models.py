import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.accounts.models import User
from .utils import extract_placeholders

def template_upload_path(instance, filename):
    # Путь: templates/<uuid>_<original_name>
    return f'templates/{instance.id}_{filename}'

class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=template_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['docx', 'doc']),
        ],
        max_length=255,
        help_text="Только файлы .docx и .doc (макс. 10 МБ)"
    )
    file_type = models.CharField(max_length=10, editable=False)  # docx или doc
    placeholders = models.JSONField(default=list, blank=True)   # список строк
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='templates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически определяем file_type по расширению
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            self.file_type = ext if ext in ['docx', 'doc'] else 'docx'
        super().save(*args, **kwargs)

    def extract_and_save_placeholders(self):
        """Извлекает плейсхолдеры из файла и сохраняет в поле placeholders."""
        if self.file and self.file_type == 'docx':
            path = self.file.path
            self.placeholders = extract_placeholders(path)
            self.save(update_fields=['placeholders'])