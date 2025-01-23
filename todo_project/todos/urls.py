from django.urls import path
from .views import RegisterView, LoginView, TodoDetailView, TodoListCreateView, CheckAuthView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('todos', TodoListCreateView.as_view(), name='todo-list-create'),
    path('todos/<int:pk>', TodoDetailView.as_view(), name='todo-detail'),
    path('check-auth', CheckAuthView.as_view(), name='check-auth'),
]