from django.contrib import admin
from .models import AllowedField, AllowedTable, User, Query
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "role")


# class CustomUserChangeForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = User
#         fields = ('username', 'password', 'role')

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "role")

        
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    # fieldsets = (
    #     (None, {'fields': ('username', 'password')}),
    #     (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    #     (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions')}),
    #     (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    # )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (("Permissions"), {"fields": ("is_active", "role")}),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role")


class QueryAdmin(admin.ModelAdmin):
    readonly_fields = ('author',)

# admin.site.register(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(AllowedTable)
admin.site.register(AllowedField)


# Register your models here.
