from django.urls import path, include

from accounts.views import ActivateAccount, Dashboard, Register

urlpatterns = [
    path('active/<uuid:activation_code>/', ActivateAccount.as_view(), name='activate_account'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('register/', Register.as_view(), name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth/', include('social_django.urls'), name='social'),

]
