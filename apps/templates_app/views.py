import io, os, uuid, subprocess, tempfile
from django.http import HttpResponse, FileResponse
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Template
from apps.documents.models import FilledDocument
from .serializers import (
    TemplateListSerializer,
    TemplateDetailSerializer,
    TemplateCreateUpdateSerializer,
)
from .utils import fill_template
from apps.accounts.permissions import IsAdminUser

# --- Пользовательские эндпоинты ---
class TemplateListView(generics.ListAPIView):
    serializer_class = TemplateListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Template.objects.filter(is_active=True)
        search = self.request.query_params.get('q', '')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.order_by('-created_at')


class TemplateDetailView(generics.RetrieveAPIView):
    serializer_class = TemplateDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Template.objects.filter(is_active=True)


class TemplateFillView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            template = Template.objects.get(pk=pk, is_active=True)
        except Template.DoesNotExist:
            return Response({"success": False, "error": "Шаблон не найден"}, status=404)

        filled_data = request.data.get('filled_data')
        output_format = request.data.get('output_format', 'docx')

        if not filled_data or not isinstance(filled_data, dict):
            return Response({"success": False, "error": "Не указаны данные для заполнения"}, status=400)

        if output_format not in ['pdf', 'docx']:
            return Response({"success": False, "error": "Неверный формат вывода"}, status=400)

        try:
            # Копируем шаблон во временный файл
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_input:
                with open(template.file.path, 'rb') as f:
                    tmp_input.write(f.read())
                input_path = tmp_input.name

            output_docx = os.path.join(tempfile.gettempdir(), f'output_{uuid.uuid4()}.docx')
            fill_template(input_path, filled_data, output_docx)
            os.unlink(input_path)

            filled_doc = FilledDocument.objects.create(
                template=template,
                filled_by=request.user,
                filled_data=filled_data,
                output_format=output_format,
            )

            if output_format == 'pdf':
                output_pdf = output_docx.replace('.docx', '.pdf')
                subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', os.path.dirname(output_docx), output_docx
                ], check=True, timeout=30)

                with open(output_pdf, 'rb') as f:
                    pdf_bytes = f.read()
                filled_doc.output_file.save(f'{uuid.uuid4()}.pdf', io.BytesIO(pdf_bytes))
                filled_doc.save()

                response = HttpResponse(pdf_bytes, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="document.pdf"'

                try:
                    os.unlink(output_docx)
                    os.unlink(output_pdf)
                except Exception:
                    pass
                return response

            else:  # docx
                with open(output_docx, 'rb') as f:
                    docx_bytes = f.read()
                filled_doc.output_file.save(f'{uuid.uuid4()}.docx', io.BytesIO(docx_bytes))
                filled_doc.save()

                response = HttpResponse(docx_bytes,
                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = 'attachment; filename="document.docx"'

                try:
                    os.unlink(output_docx)
                except Exception:
                    pass
                return response

        except subprocess.CalledProcessError as e:
            return Response({"success": False, "error": f"Ошибка конвертации PDF: {str(e)}"}, status=500)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)


# --- Админские эндпоинты ---
class AdminTemplateListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TemplateCreateUpdateSerializer
        return TemplateListSerializer

    def get_queryset(self):
        return Template.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        template = serializer.save()
        if template.file and template.file_type == 'docx':
            template.extract_and_save_placeholders()


class AdminTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = Template.objects.all()               

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TemplateCreateUpdateSerializer
        return TemplateDetailSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()