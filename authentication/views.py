from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CurrentUserSerializer, LoginSerializer


class CsrfView(APIView):
	permission_classes = [AllowAny]

	@method_decorator(ensure_csrf_cookie)
	def get(self, request, *args, **kwargs):
		return Response({'detail': 'CSRF cookie set'})


class LoginView(APIView):
	permission_classes = [AllowAny]

	def post(self, request, *args, **kwargs):
		serializer = LoginSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']
		login(request, user)
		return Response(CurrentUserSerializer(user).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
	permission_classes = [AllowAny]

	def post(self, request, *args, **kwargs):
		logout(request)
		return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		return Response(CurrentUserSerializer(request.user).data)
