from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Todo

# Custom UserAdmin
class UserAdmin(DefaultUserAdmin):
    model = User
    # Customize fields to display in the admin list view
    list_display = ('username', 'email', 'is_staff', 'is_active', 'password')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('email',)

# Register the User model
admin.site.register(User, UserAdmin)

# Custom TodoAdmin
class TodoAdmin(admin.ModelAdmin):
    model = Todo
    # Customize fields to display in the admin list view
    list_display = ('title', 'user', 'completed')
    list_filter = ('completed',)
    search_fields = ('title', 'user__username')

# Register the Todo model
admin.site.register(Todo, TodoAdmin)
