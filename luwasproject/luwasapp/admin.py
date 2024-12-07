from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, Establishment, IncidentReport, IncidentAssignment

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'contact_information', 'address', 'profession', 'birth_date', 'department', 'establishment', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), 
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'contact_information', 'address', 'profession', 'birth_date', 'department', 'establishment', 'profile_image'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('date_joined',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'department')
    search_fields = ('name', 'location', 'department__name')

class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('reportid', 'incident_type', 'severity', 'status', 'location', 'timestamp', 'category')
    search_fields = ('incident_type', 'severity', 'status', 'location')
    list_filter = ('incident_type', 'severity', 'status', 'timestamp')

class IncidentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'incident_report', 'notification_sent', 'assigned_at')
    search_fields = ('user__username', 'incident_report__reportid')
    list_filter = ('notification_sent', 'assigned_at')

admin.site.register(User, UserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Establishment, EstablishmentAdmin)
admin.site.register(IncidentReport, IncidentReportAdmin)
admin.site.register(IncidentAssignment, IncidentAssignmentAdmin)