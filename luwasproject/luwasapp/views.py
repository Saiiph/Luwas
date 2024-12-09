from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import requests

from django.contrib import messages


from .forms import SignupForm, LoginForm, IncidentReportForm
from .models import IncidentReport, Establishment, Department, IncidentAssignment, User

from .utils import get_location_from_coordinates


from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
import json


#======================================================GENERAL VIEW======================================================#
#Homepage view
def home_view(request):
    return render(request, 'general/home.html')

# Dashboard view
@login_required
def dashboard_view(request):
    user = request.user

    # Group incidents by category and count them
    incidents_by_category = list(IncidentReport.objects.values('category').annotate(count=Count('category')).order_by('-count'))

    # Group incidents by status and count them
    incidents_by_status = list(IncidentReport.objects.values('status').annotate(count=Count('status')).order_by('-count'))

    # Group user's assigned incidents by category and count them
    user_incidents_by_category = list(IncidentAssignment.objects.filter(user=user).values('incident_report__category').annotate(count=Count('incident_report__category')).order_by('-count'))

    # Group user's assigned incidents by status and count them
    user_incidents_by_status = list(IncidentAssignment.objects.filter(user=user).values('incident_report__status').annotate(count=Count('incident_report__status')).order_by('-count'))

    # Mapping of category/status keys to display names
    category_display_names = {
        'medical_emergency': 'Medical Emergency',
        'fire_incident': 'Fire Incident',
        'road_accident': 'Road Accident',
        'natural_disaster': 'Natural Disaster',
        'crime_related': 'Crime Related',
        'domestic_violence': 'Domestic Violence',
        'psychological_crisis': 'Psychological Crisis',
        'missing_person': 'Missing Person',
        'poisoning': 'Poisoning',
        'gas_leak': 'Gas Leak',
        'electrical_hazard': 'Electrical Hazard',
        'hazardous_materials': 'Hazardous Materials',
        'flooding': 'Flooding',
        'earthquake': 'Earthquake',
        'typhoon': 'Typhoon',
        'animal_attack': 'Animal Attack',
        'terrorist_threat': 'Terrorist Threat',
        'building_collapse': 'Building Collapse',
        'public_disturbance': 'Public Disturbance',
        'child_abuse': 'Child Abuse',
        'elderly_abuse': 'Elderly Abuse'
    }

    status_display_names = {
        'reported': 'Reported',
        'resolved': 'Resolved',
        'closed': 'Closed'
    }

    context = {
        'user': user,
        'incidents_by_category': json.dumps(incidents_by_category),
        'incidents_by_status': json.dumps(incidents_by_status),
        'user_incidents_by_category': json.dumps(user_incidents_by_category),
        'user_incidents_by_status': json.dumps(user_incidents_by_status),
        'category_display_names': json.dumps(category_display_names),
        'status_display_names': json.dumps(status_display_names)
    }
    return render(request, 'general/dashboard.html', context)

#======================================================USER VIEW======================================================#
#Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')  # Redirect to a login page
    else:
        form = SignupForm()
    return render(request, 'general/signup.html', {'form': form})

#Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to Dashboard
    else:
        form = LoginForm()
    return render(request, 'general/login.html', {'form': form})

#Logout view
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logout

#User Profile view
@login_required
def user_profile_view(request):
    user = request.user
    context = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'contact_information': user.contact_information,
        'address': user.address,
        'profession': user.profession,
        'birth_date': user.birth_date,
        'department': user.department,
        'establishment': user.establishment,
    }
    return render(request, 'profile/user_profile.html', context)

# Update Account view
@login_required
def update_user_view(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.contact_information = request.POST['contact_information']
        user.address = request.POST['address']
        user.profession = request.POST['profession']
        user.birth_date = request.POST['birth_date']
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        return redirect('user_profile')
    return render(request, 'profile/update_user.html', {'user': user})

# Delete Account view
@login_required
def delete_user_view(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect('login')
    return render(request, 'profile/delete_user.html', {'user': user})


#======================================================INCIDENT VIEW======================================================#

# Create Incident View
def incident_create_view(request):
    if request.method == 'POST':
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            # Extract latitude and longitude from the form
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            
            # Get the location from the form (the value set by JavaScript)
            location = form.cleaned_data['location']

            # Save the form with additional data
            incident = form.save(commit=False)
            incident.latitude = latitude
            incident.longitude = longitude
            incident.location = location
            incident.save()

            return redirect('home')  # Redirect to a home page
    else:
        # Prepopulate form
        form = IncidentReportForm()

    return render(request, 'incident/create.html', {'form': form})


#Incident Detail View
@login_required
def incident_detail_view(request, pk):
    # Get the incident report
    incident = get_object_or_404(IncidentReport, pk=pk)
    
    # Check if the user is assigned to this incident
    is_assigned = IncidentAssignment.objects.filter(incident_report=incident, user=request.user).exists()

    # Fetch location details from Nominatim
    location_details = {}
    if incident.latitude and incident.longitude:
        NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": incident.latitude,
            "lon": incident.longitude,
            "format": "json",
        }
        try:
            response = requests.get(NOMINATIM_URL, params=params)
            if response.status_code == 200:
                location_details = response.json()
        except requests.RequestException as e:
            # Log error in production
            print(f"Error fetching location details: {e}")

    # Render the template
    return render(request, 'incident/detail.html', {
        'incident': incident,
        'is_assigned': is_assigned,
        'location_details': location_details,
    })


#Update Incident View
@login_required
def incident_update_view(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            return redirect('incident_detail', pk=pk)
    else:
        form = IncidentReportForm(instance=incident)
    return render(request, 'incident/update.html', {'form': form, 'incident': incident})

#Delete Incident View
@login_required
def incident_delete_view(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    if request.method == 'POST':
        incident.delete()
        return redirect('incident_list')
    return render(request, 'incident/delete.html', {'incident': incident})

@login_required
def incident_list_view(request):
    if not request.user.department:
        # If the user doesn't belong to any department, deny access
        return HttpResponseForbidden("You are not assigned to a department.")
    
    # Map categories to departments (create this mapping as needed)
    category_to_department = {
        'fire_incident': ['Fire Department', 'Medical Department', 'Emergency Response'],
        'medical_emergency': ['Medical Department', 'Emergency Response'],
        'road_accident': ['Transportation Department', 'Medical Department'],
        'natural_disaster': ['Disaster Response', 'Emergency Management Department'],
        'crime_related': ['Police Department', 'Law Enforcement'],
        'domestic_violence': ['Social Services', 'Domestic Violence Response Team'],
        'psychological_crisis': ['Mental Health Services', 'Crisis Intervention Team'],
        'missing_person': ['Police Department', 'Missing Persons Unit'],
        'poisoning': ['Poison Control Center', 'Health Department'],
        'gas_leak': ['Fire Department', 'Hazardous Materials (HazMat) Team'],
        'electrical_hazard': ['Electrical Utility Company', 'Fire Department'],
        'hazardous_materials': ['Hazardous Materials (HazMat) Response', 'Environmental Protection Agency'],
        'flooding': ['Emergency Management', 'Flood Control Department'],
        'earthquake': ['Emergency Management', 'Geological Survey Department'],
        'typhoon': ['National Disaster Risk Reduction and Management Council (NDRRMC)', 'Emergency Management'],
        'animal_attack': ['Animal Control', 'Emergency Medical Services (EMS)'],
        'terrorist_threat': ['Counter-Terrorism Unit', 'National Security Agency'],
        'building_collapse': ['Fire Department', 'Rescue and Emergency Response'],
        'public_disturbance': ['Public Safety', 'Police Department'],
        'child_abuse': ['Child Protective Services', 'Social Services'],
        'elderly_abuse': ['Adult Protective Services', 'Social Services']
    }

    # Get the department name of the logged-in user
    user_department_name = request.user.department.name

    # Filter categories where the user's department is involved
    relevant_categories = [
        category for category, departments in category_to_department.items()
        if user_department_name in departments
    ]
    
    # Group incidents by their status
    statuses = ['reported', 'resolved', 'closed']
    incidents_by_status = {
        status: IncidentReport.objects.filter(
            category__in=relevant_categories, status=status
        ).order_by('-timestamp')
        for status in statuses
    }

    return render(request, 'incident/list.html', {'incidents_by_status': incidents_by_status})


#============================Incident Assignment====================================================================

@login_required
def incident_assignment_list(request):
    assignments = IncidentAssignment.objects.filter(user=request.user)
    return render(request, 'incident_assignment/incident_assignment_list.html', {'assignments': assignments})

# Mapping of incident categories to departments
category_to_department = {
    'fire_incident': ['Fire Department', 'Medical Department', 'Emergency Response'],
    'medical_emergency': ['Medical Department', 'Emergency Response'],
    'road_accident': ['Transportation Department', 'Medical Department'],
    'natural_disaster': ['Disaster Response', 'Emergency Management Department'],
    'crime_related': ['Police Department', 'Law Enforcement'],
    'domestic_violence': ['Social Services', 'Domestic Violence Response Team'],
    'psychological_crisis': ['Mental Health Services', 'Crisis Intervention Team'],
    'missing_person': ['Police Department', 'Missing Persons Unit'],
    'poisoning': ['Poison Control Center', 'Health Department'],
    'gas_leak': ['Fire Department', 'Hazardous Materials (HazMat) Team'],
    'electrical_hazard': ['Electrical Utility Company', 'Fire Department'],
    'hazardous_materials': ['Hazardous Materials (HazMat) Response', 'Environmental Protection Agency'],
    'flooding': ['Emergency Management', 'Flood Control Department'],
    'earthquake': ['Emergency Management', 'Geological Survey Department'],
    'typhoon': ['National Disaster Risk Reduction and Management Council (NDRRMC)', 'Emergency Management'],
    'animal_attack': ['Animal Control', 'Emergency Medical Services (EMS)'],
    'terrorist_threat': ['Counter-Terrorism Unit', 'National Security Agency'],
    'building_collapse': ['Fire Department', 'Rescue and Emergency Response'],
    'public_disturbance': ['Public Safety', 'Police Department'],
    'child_abuse': ['Child Protective Services', 'Social Services'],
    'elderly_abuse': ['Adult Protective Services', 'Social Services']
}

from django.urls import reverse

def assign_user_to_incident_admin(request, user_id):
    users = User.objects.all()
    incidents = IncidentReport.objects.all()

    # Get the user who will be assigned
    user_to_assign = get_object_or_404(User, id=user_id)

    # Assuming the user has a 'department' field or related model, we can get the department
    user_department = getattr(user_to_assign, 'department', None)
    if not user_department:
        messages.error(request, 'User department not found.')
        return redirect('assign_user')

    # Convert the department to a string
    user_department_str = str(user_department).lower()

    # Filter incidents based on the user's department and category
    filtered_incidents = []
    for incident in incidents:
        incident_category = getattr(incident, 'category', None)
        if not incident_category:
            messages.error(request, f'Incident {incident.id} does not have a category.')
            continue
        incident_category = incident_category.lower()
        allowed_departments = category_to_department.get(incident_category, [])
        if user_department_str in [dept.lower() for dept in allowed_departments]:
            filtered_incidents.append(incident)

    if request.method == 'POST':
        incident_reportid = request.POST['incident']
        incident = get_object_or_404(IncidentReport, reportid=incident_reportid)

        assignment, created = IncidentAssignment.objects.get_or_create(
            user=user_to_assign,
            incident_report=incident
        )
        if created:
            messages.success(request, f'{user_to_assign.username} has been assigned to Incident {incident.reportid}.')
        else:
            messages.info(request, f'{user_to_assign.username} is already assigned to Incident {incident.reportid}.')
        
        return redirect(reverse('assign_user', args=[user_id]))
    
    return render(request, 'incident_assignment/assign_user.html', {
        'users': users, 
        'incidents': filtered_incidents,  # Pass the filtered incidents
        'user_to_assign': user_to_assign  # Pass the user to be assigned
    })
#====================================Admin View=====================================================================
@staff_member_required
def list_users_view(request):
    users = User.objects.all()
    return render(request, 'admin/list_users.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # Add the rest of the edit_user_view logic here


#====================================Admin View=====================================================================
@staff_member_required
def list_users_view(request):
    users = User.objects.all()
    return render(request, 'admin/list_users.html', {'users': users})



@user_passes_test(lambda u: u.is_superuser)
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    departments = Department.objects.all()

    # Get the selected department from the GET parameters (or use the user's current department)
    department_id = request.GET.get('department', user.department_id)

    # Fetch establishments based on the selected department
    establishments = Establishment.objects.filter(department_id=department_id)

    if request.method == 'POST':
        # Update user information with the form data
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.profession = request.POST['profession']

        if 'department' in request.POST:
            user.department_id = request.POST['department']
            user.establishment_id = request.POST.get('establishment', None)  
        
        user.save()
        
        if 'save' in request.POST:
            return redirect('list_users')
        else:
            return redirect('edit_user', user_id=user.id)

    context = {
        'user': user,
        'departments': departments,
        'establishments': establishments,
        'department_id': department_id  
    }
    return render(request, 'admin/edit_user.html', context)

