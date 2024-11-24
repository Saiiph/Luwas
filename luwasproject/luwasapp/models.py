from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin

class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('Please provide a valid email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self._create_user(username, email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, default='')
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    contact_information = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    profession = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    establishment = models.ForeignKey('Establishment', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Establishment(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='establishments')

    def __str__(self):
        return self.name

class IncidentReport(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    reportid = models.AutoField(primary_key=True)
    incident_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=25, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    location = models.CharField(max_length=255)    
    timestamp = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='incidents', null=True, blank=True)

    def __str__(self):
        return f'Incident {self.reportid} - {self.status}'
    
class IncidentAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    incident_report = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='assignments')
    notification_sent = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} assigned to Incident {self.incident_report.reportid}'

