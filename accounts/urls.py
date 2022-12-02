from django.urls import path, include

from accounts.views import ActivateAccount, Dashboard, Register, CustomSetPasswordView


urlpatterns = [
    path('active/<uuid:activation_code>/', ActivateAccount.as_view(), name='activate_account'),
    path("reset/<uidb64>/<token>/", CustomSetPasswordView.as_view(), name='custom_password_reset_confirm'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('register/', Register.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth/', include('social_django.urls'), name='social'),

]
