from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, College


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ("email", "username", "first_name", "last_name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "is_college_student")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Fynity",
            {
                "fields": (
                    "mobile",
                    "role",
                    "is_college_student",
                    "college",
                    "college_name",
                    "branch",
                    "current_year",
                    "semester",
                    "cgpa",
                    "roll_number",
                )
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "total_points", "total_stars", "streak_days", "last_active")
    search_fields = ("user__email",)
