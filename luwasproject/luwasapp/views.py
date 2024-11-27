from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import SignupForm, LoginForm, IncidentReportForm
from .models import IncidentReport

from .utils import get_location_from_coordinates

#Homepage view
def home_view(request):
    return render(request, 'general/home.html')

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

# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'general/dashboard.html',)


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

@login_required
#Incident Detail View
def incident_detail_view(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    return render(request, 'incident/detail.html', {'incident': incident})

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
    
    # Get incidents that match the relevant categories
    incidents = IncidentReport.objects.filter(category__in=relevant_categories)

    return render(request, 'incident/list.html', {'incidents': incidents})
