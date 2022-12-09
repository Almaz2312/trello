from django.urls import path

from boards.api import views


urlpatterns = [
    # Boards API urls
    path('', views.BoardListAPIView.as_view(), name='board_api'),
    path('<int:pk>/', views.BoardDetailUpdateDeleteAPIView.as_view(), name='board_api_detail'),

    # Members API urls
    path('members/', views.MembersListAPIView.as_view(), name='member_api'),
    path('members/<int:pk>/', views.MembersDetailUpdateDeleteAPIView.as_view(), name='member_api_detail'),

    # Column API urls
    path('column/', views.ColumnListCreateAPIView.as_view(), name='column_api'),
    path('column/<int:pk>/', views.ColumnDetailUpdateDeleteAPIView.as_view(), name='column_api_detail'),

    # Card API with Comments in detail view urls
    path('card/', views.CardListCreateAPIView.as_view(), name='card_api'),
    path('card/<int:pk>/', views.CardDetailDeleteUpdate.as_view(), name='card_api_detail'),

    # CheckList API urls
    path('checklist/', views.CheckListCreateAPIView.as_view(), name='checklist_api'),
    path('checklist/<int:pk>/', views.CheckDetailUpdateDeleteAPIView.as_view(), name='checklist_api_detail'),

    # Archive API urls
    path('archive/', views.ArchiveListCreateAPIView.as_view(), name='archive_api'),
    path('archive/<int:pk>', views.ArchiveDetailUpdateDeleteView.as_view(), name='archive_api_detail'),

    # File API urls
    path('file/', views.FileListCreateAPIView.as_view(), name='file_api'),
    path('file/<int:pk>/', views.FileDetailDeleteAPIView.as_view(), name='file_api_detail'),

    # Comment API urls
    path('comment/card/<int:pk>/', views.CommentCreateAPIView.as_view(), name='comment_api'),

    # Marks API url
    path('mark/', views.MarkListAPIView.as_view(), name='mark_api'),
    path('mark/<int:pk>/', views.MarkDetailUpdateDeleteAPIView.as_view(), name='mark_api_detail'),

    # Favourite API urls
    path('favourite/', views.FavouriteListAPIView.as_view(), name='favourite_api'),
    path('favourite/<int:pk>/', views.FavouriteDetailDeleteView.as_view(), name='favourite_api_detail')
]
