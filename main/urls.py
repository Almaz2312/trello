"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from boards.api import views


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('accounts.urls')),
    path('boards/', include('boards.urls')),
    path('api/accounts/', include('accounts.api.urls')),
    path('api/boards/', include('boards.api.urls')),
    path('api/card/', views.CardListCreateAPIView.as_view(), name='card_api'),
    path('api/card/<int:pk>/', views.CardDetailDeleteUpdate.as_view(), name='card_api_detail'),
    path('api/members/', views.MembersListAPIView.as_view(), name='member_api'),
    path('api/members/<int:pk>/', views.MembersDetailUpdateDeleteAPIView.as_view(), name='member_api_detail'),
    path('api/column/', views.ColumnListCreateAPIView.as_view(), name='column_api'),
    path('api/column/<int:pk>/', views.ColumnDetailUpdateDeleteAPIView.as_view(), name='column_api_detail'),
    path('api/checklist/', views.CheckListCreateAPIView.as_view(), name='checklist_api'),
    path('api/checklist/<int:pk>/', views.CheckDetailUpdateDeleteAPIView.as_view(), name='checklist_api_detail'),
    path('api/archive/', views.ArchiveListCreateAPIView.as_view(), name='archive_api'),
    path('api/archive/<int:pk>', views.ArchiveDetailUpdateDeleteView.as_view(), name='archive_api_detail'),
    path('api/file/', views.FileListCreateAPIView.as_view(), name='file_api'),
    path('api/file/<int:pk>/', views.FileDetailDeleteAPIView.as_view(), name='file_api_detail'),
    path('api/comment/card/<int:card_id>/', views.CommentCreateAPIView.as_view(), name='comment_api'),
    path('api/mark/', views.MarkListAPIView.as_view(), name='mark_api'),
    path('api/mark/<int:pk>/', views.MarkDetailUpdateDeleteAPIView.as_view(), name='mark_api_detail'),
    path('api/favourite/', views.FavouriteListAPIView.as_view(), name='favourite_api'),
    path('api/favourite/<int:pk>/', views.FavouriteDetailDeleteView.as_view(), name='favourite_api_detail')

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)