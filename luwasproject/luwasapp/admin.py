from django.contrib import admin
from .models import User, RespondentProfile, Department, Establishment

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'contact_information', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('date_joined',)

class RespondentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession', 'birth_date', 'department', 'establishment')
    search_fields = ('user__username', 'user__email', 'profession', 'department__name', 'establishment__name')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'department')
    search_fields = ('name', 'location', 'department__name')

admin.site.register(User, UserAdmin)
admin.site.register(RespondentProfile, RespondentProfileAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Establishment, EstablishmentAdmin)