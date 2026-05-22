from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, login, logout
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsAdminUser  # создадим позже

User = get_user_model()

# --- Регистрация ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Можно сразу авторизовать или вернуть токен
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "data": {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username
                }
            },
            "message": "Пользователь успешно зарегистрирован."
        }, status=status.HTTP_201_CREATED)


# --- Логин ---
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)  # сессия
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "data": {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role
                }
            },
            "message": "Вход выполнен."
        })


# --- Логаут ---
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Удаляем токен, если используется TokenAuthentication
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        logout(request)
        return Response({"success": True, "message": "Выход выполнен."})


# --- Админ: список пользователей ---
class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


# --- Админ: детали/редактирование/удаление пользователя ---
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def perform_update(self, serializer):
        # Запрет снятия роли admin с самого себя (опционально)
        if self.request.user.id == serializer.instance.id and 'role' in serializer.validated_data:
            if serializer.validated_data['role'] != 'admin':
                raise serializers.ValidationError("Нельзя снять роль администратора с самого себя.")
        serializer.save()

    def perform_destroy(self, instance):
        # Мягкое удаление не предусмотрено моделью, но можно сделать деактивацию
        instance.is_active = False
        instance.save()
        # Либо реальное удаление: instance.delete()