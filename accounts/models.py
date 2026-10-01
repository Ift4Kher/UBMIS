from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        INSPECTOR = "INSPECTOR", "Inspector"
        DRIVER = "DRIVER", "Driver"
        STUDENT = "STUDENT", "Student"
        FACULTY = "FACULTY", "Faculty"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)

    def is_admin(self):
        return self.is_superuser
    
    def is_inspector(self):
        return self.role == self.Role.INSPECTOR
    
    def is_driver(self):
        return self.role == self.Role.DRIVER

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_faculty(self):
        return self.role == self.Role.FACULTY
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
