from django.urls import path

from boards.api import views


urlpatterns = [
    # Boards API urls
    path('', views.BoardListAPIView.as_view(), name='board_api'),
    path('<int:pk>/', views.BoardDetailUpdateDeleteAPIView.as_view(), name='board_api_detail'),

    # Members API urls

    # Column API urls


    # CheckList API urls


    # Archive API urls

    # File API urls

    # Comment API urls


    # Marks API url

    # Favourite API urls
]
