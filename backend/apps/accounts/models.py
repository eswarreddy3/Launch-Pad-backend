from django.contrib.auth.models import AbstractUser
from django.db import models


class College(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ("free", "Free User"),
        ("subscriber", "Subscriber"),
        ("college_admin", "College Admin"),
        ("super_admin", "Super Admin"),
    ]

    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="free")
    is_college_student = models.BooleanField(default=False)
    college_name = models.CharField(max_length=200, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    current_year = models.IntegerField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    college = models.ForeignKey(
        College,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    bio = models.TextField(blank=True)
    total_points = models.IntegerField(default=0)
    total_stars = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email} — profile"
