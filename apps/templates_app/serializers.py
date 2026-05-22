from rest_framework import serializers
from .models import Template

class TemplateListSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    placeholder_count = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = ('id', 'title', 'description', 'file_type', 'placeholders', 'placeholder_count',
                  'uploaded_by', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'file_type', 'placeholders', 'uploaded_by', 'created_at', 'updated_at')

    def get_placeholder_count(self, obj):
        return len(obj.placeholders) if obj.placeholders else 0


class TemplateDetailSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    placeholder_count = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = '__all__'

    def get_placeholder_count(self, obj):
        return len(obj.placeholders) if obj.placeholders else 0


class TemplateCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ('title', 'description', 'file')

    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['docx', 'doc']:
            raise serializers.ValidationError("Разрешены только файлы .docx и .doc")
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Максимальный размер файла — 10 МБ.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        template = Template.objects.create(uploaded_by=user, **validated_data)
        # Автоматически извлечь плейсхолдеры после сохранения
        if template.file and template.file_type == 'docx':
            template.extract_and_save_placeholders()
        return template