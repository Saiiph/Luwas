from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignupForm, LoginForm, IncidentReportForm
from .models import IncidentReport
from .utils import get_geolocation_data

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
                return redirect('home')  # Redirect to Dashboard
    else:
        form = LoginForm()
    return render(request, 'general/login.html', {'form': form})

#Create Incident View
def incident_create_view(request):
    if request.method == 'POST':
        form = IncidentReportForm(request.POST)
        if form.is_valid():
            # Get geolocation data
            geolocation_data = get_geolocation_data()  # Optionally pass the user's IP address
            if geolocation_data:
                city = geolocation_data.get("city", "Unknown City")
                country = geolocation_data.get("country", "Unknown Country")
                latitude = geolocation_data.get("latitude")
                longitude = geolocation_data.get("longitude")
                location = f"{city}, {country}"

                # Save form with additional data
                incident = form.save(commit=False)
                incident.location = location
                incident.latitude = latitude
                incident.longitude = longitude
                incident.save()

                return redirect('home')  # Redirect to a home page
    else:
        # Prepopulate location data for display
        geolocation_data = get_geolocation_data()
        initial_data = {}
        if geolocation_data:
            city = geolocation_data.get("city", "Unknown City")
            country = geolocation_data.get("country", "Unknown Country")
            latitude = geolocation_data.get("latitude")
            longitude = geolocation_data.get("longitude")
            location = f"{city}, {country}"
            initial_data = {
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
            }
        form = IncidentReportForm(initial=initial_data)

    return render(request, 'incident/create.html', {'form': form})


#Incident List View
def incident_list_view(request):    
    incidents = IncidentReport.objects.all()
    return render(request, 'incident/list.html', {'incidents': incidents})

#Incident Detail View
def incident_detail_view(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    return render(request, 'incident/detail.html', {'incident': incident})