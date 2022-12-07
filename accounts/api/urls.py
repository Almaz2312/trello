from django.urls import path, include
from accounts.api import views

urlpatterns = [

    path('register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('activation/<slug:activation_code>', views.ActivationAPIView.as_view(), name='api_activation'),
    path('login/', views.LoginAPIView.as_view(), name='api_login'),
    path('restore_password/', views.ResetPasswordAPIView.as_view()),
    path('restore_complete/', views.ResetPasswordCompleteView.as_view()),
    path('logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('google_oauth/', views.GoogleLoginView.as_view()),
    path('rest_login/', include('rest_framework.urls'))
]
