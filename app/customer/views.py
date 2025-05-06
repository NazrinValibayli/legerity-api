from rest_framework import generics, status
from rest_framework.response import Response
from customer.serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"access": response.data["access"]}, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
