from django.shortcuts import redirect
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import FilledDocument
from .serializers import FilledDocumentSerializer

class DocumentListView(generics.ListAPIView):
    serializer_class = FilledDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FilledDocument.objects.filter(filled_by=self.request.user).order_by('-created_at')


class DocumentDownloadView(generics.RetrieveAPIView):
    serializer_class = FilledDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FilledDocument.objects.filter(filled_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.output_file:
            return redirect(instance.output_file.url)  # или отдаём файл напрямую
        return Response({"success": False, "error": "Файл не найден"}, status=404)