# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, TodoSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Todo
from .custom_authentication import CookieJWTAuthentication
from .helper import cookie_options


class CheckAuthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"authenticated": False, "message": "Session expired. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Validate the refresh token
            RefreshToken(refresh_token)
            return Response({"authenticated": True}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"authenticated": False, "message": "Session expired. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]  # Overrides global permissions
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully!', "success": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]  # Overrides global permissions
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Prepare response
            response = Response({
                'message': 'Login successful',
            }, status=status.HTTP_200_OK)

            # Set cookies for access and refresh tokens
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                # secure=cookie_options.get('secure', False),  # Use True for HTTPS in production
                # samesite=cookie_options.get('samesite', 'None'),
                max_age= cookie_options.get('access_token_expiry_in_minutes', 30) * 60
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                # secure=cookie_options.get('secure', False),  # Use True for HTTPS in production
                # samesite=cookie_options.get('samesite', 'None'),
                max_age=cookie_options.get('refresh_token_expiry_in_minutes', 24*60) * 60
            )

            return response
        return Response({'message': 'Invalid credentials', "authenticated": False}, status=status.HTTP_401_UNAUTHORIZED)
    

class LogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"message": "Logged out successfully"}, status=200)
        # Clear cookies by setting them to expire immediately
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    

# List and Create Todos
class TodoListCreateView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch todos for the authenticated user
        todos = Todo.objects.filter(user=request.user)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Add a new todo for the authenticated user
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve, Update, and Delete Todo
class TodoDetailView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Todo.objects.get(pk=pk, user=user)
        except Todo.DoesNotExist:
            return None

    def get(self, request, pk):
        todo = self.get_object(pk, request.user)
        if todo:
            serializer = TodoSerializer(todo)
            return Response(serializer.data)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        todo = self.get_object(pk, request.user)
        if todo:
            serializer = TodoSerializer(todo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        todo = self.get_object(pk, request.user)
        if todo:
            todo.delete()
            return Response({'message': 'Todo deleted'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)    
