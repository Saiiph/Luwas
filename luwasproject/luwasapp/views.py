from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm, LoginForm, IncidentReportForm
from .models import IncidentReport


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
            form.save()
            return redirect('home') # Redirect to a home page 
    else:
        form = IncidentReportForm()
    return render(request, 'incident/create.html', {'form': form})

#Incident List View
def incident_list_view(request):    
    incidents = IncidentReport.objects.all()
    return render(request, 'incident/list.html', {'incidents': incidents})

#Incident Detail View
def incident_detail_view(request, pk):
    incident = get_object_or_404(IncidentReport, pk=pk)
    return render(request, 'incident/detail.html', {'incident': incident})