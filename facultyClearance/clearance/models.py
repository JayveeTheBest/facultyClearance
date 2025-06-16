from django.db import models
from django.contrib.auth.models import User


# Department model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Faculty Member profile
class FacultyMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_part_time = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name()


# Department Chair profile
class DepartmentChair(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.OneToOneField(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()


# College Dean profile
class CollegeDean(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()


# Requirement model for dynamic clearance items
class Requirement(models.Model):
    ROLE_CHOICES = [
        ('faculty', 'Faculty Member'),
        ('chair', 'Department Chair'),
        ('part_timer', 'Part-time Faculty'),
    ]

    title = models.CharField(max_length=255)
    applicable_to = models.CharField(max_length=10, choices=ROLE_CHOICES, default='faculty')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Upload model to associate uploaded files with requirements
class Upload(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='uploads')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.requirement.title} - {self.status}"
