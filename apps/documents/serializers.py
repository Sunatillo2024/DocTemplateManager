from rest_framework import serializers
from .models import FilledDocument

class FilledDocumentSerializer(serializers.ModelSerializer):
    template_title = serializers.CharField(source='template.title', read_only=True)
    filled_by_email = serializers.CharField(source='filled_by.email', read_only=True)

    class Meta:
        model = FilledDocument
        fields = ('id', 'template_title', 'filled_by_email', 'output_format', 'created_at', 'output_file')
        read_only_fields = fields