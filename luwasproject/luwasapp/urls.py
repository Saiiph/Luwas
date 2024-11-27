from django.urls import path
from . import views

urlpatterns = [
    # User Authentication
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # User Management
    
    # Incident Reports Management
    path('incidents/new/', views.incident_create_view, name='incident_create'),
    path('incidents/', views.incident_list_view, name='incident_list'),
    path('incidents/<int:pk>/', views.incident_detail_view, name='incident_detail'), 
    path('incidents/<int:pk>/update/', views.incident_update_view, name='incident_update'),
    path('incidents/<int:pk>/delete/', views.incident_delete_view, name='incident_delete'),
]
