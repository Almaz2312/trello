from django.urls import path

from boards.api import views


urlpatterns = [
    # Boards API urls
    path('', views.BoardListAPIView.as_view(), name='board_api'),
    path('<int:pk>/', views.BoardDetailUpdateDeleteAPIView.as_view(), name='board_api_detail'),

    # Members API urls
    path('members/', views.MembersListAPIView.as_view()),

    # Column API urls
    path('column/', views.ColumnListCreateAPIView.as_view()),
    path('column/<int:pk>', views.ColumnDetailUpdateDeleteAPIView.as_view()),

    # Card API with Comments in detail view urls
    path('card/', views.CardListCreateAPIView.as_view()),
    path('card/<int:pk>', views.CardDetailDeleteUpdate.as_view()),

    # CheckList API urls
    path('checklist/card: <card_id>', views.CheckListCreateAPIView.as_view()),
    path('checklist/<int:pk>', views.CheckDetailUpdateDeleteAPIView.as_view()),

    # Archive API urls
    path('archive/', views.ArchiveListCreateAPIView.as_view()),

    # File API urls
    path('file/', views.FileLisCreateAPIView.as_view()),
    path('file/', views.FileDetailDeleteAPIView.as_view()),
]
