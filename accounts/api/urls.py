from django.urls import path
from rest_framework.reverse import reverse_lazy

from accounts.api import views


urlpatterns = [

    path('register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('activation/', views.ActivationAPIView.as_view(), name='api_activation'),
    path('login/', views.LoginAPIView.as_view(), name='api_login'),
    path('reset_password/', views.ResetPasswordAPIView.as_view(), name='api_reset_password'),
    path('reset_complete/', views.ResetPasswordCompleteView.as_view(), name='api_reset_password_complete'),
    path('logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('google_oauth/', views.GoogleLoginView.as_view(), name='api_google_auth'),
    # path('google_oauth/', reverse_lazy(''))
]
