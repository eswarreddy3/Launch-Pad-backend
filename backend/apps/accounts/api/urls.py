from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, MeView, ChangePasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="accounts-register"),
    path("login/", LoginView.as_view(), name="accounts-login"),
    path("logout/", LogoutView.as_view(), name="accounts-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="accounts-token-refresh"),
    path("me/", MeView.as_view(), name="accounts-me"),
    path("change-password/", ChangePasswordView.as_view(), name="accounts-change-password"),
]
