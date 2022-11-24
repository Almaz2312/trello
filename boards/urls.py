from django.urls import path
from boards import views


urlpatterns = [

    # Boards urls
    path('', views.BoardView.as_view(), name='board_list'),
    path('last_seen/', views.LastSeenView.as_view(), name='last_seen_list'),
    path('<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('delete:<int:pk>/', views.BoardDeleteView.as_view(), name='board_delete'),
    path('update:<int:pk>/', views.UpdateBoardView.as_view(), name='board_update'),
    path('create_board/', views.CreateBoardView.as_view(), name='create_board'),

    # Columns urls
    path('column/', views.ColumnView.as_view(), name='column_list'),
    path('column/<int:pk>/', views.ColumnDetailView.as_view(), name='column_detail'),
    path('column/delete:<int:pk>/', views.ColumnDeleteView.as_view(), name='column_delete'),
    path('column/update:<int:pk>/', views.ColumnUpdateView.as_view(), name='column_update'),
    # path('column/create/', views.ColumnCreateView.as_view(), name='column_create'),

    # Cards urls
    path('card/', views.CardListView.as_view(), name='card_list'),
    path('card/mark:<mark>/', views.CardMarkListView.as_view(), name='card_mark'),
    path('card/create/', views.CardCreateView.as_view(), name='card_create'),
    path('card/<int:pk>/', views.CardDetailView.as_view(), name='card_detail'),
    path('card/update:<int:pk>/', views.CardUpdateView.as_view(), name='card_update'),
    path('card/delete/:<int:pk>/', views.CardDeleteView.as_view(), name='card_delete'),

    # Checklists urls
    path('checklist/', views.CheckListView.as_view(), name='checklist_list'),
    path('checklist/create/', views.ChecklistCreateView.as_view(), name='checklist_create'),
    path('checklist/<int:pk>/', views.CheckListDetailView.as_view(), name='checklist_detail'),
    path('checklist/update:<int:pk>/', views.CheckListUpdateView.as_view(), name='checklist_update'),
    path('checklist/delete/:<int:pk>/', views.CheckListDeleteView.as_view(), name='checklist_delete'),

    # Marks urls
    path('mark/', views.MarkView.as_view(), name='mark_list'),
    path('mark/create/', views.MarkCreateView.as_view(), name='mark_create'),
    path('mark/<int:pk>/', views.MarkDetailView.as_view(), name='mark_detail'),
    path('mark/update:<int:pk>/', views.MarkUpdateView.as_view(), name='mark_update'),
    path('mark/delete/:<int:pk>/', views.MarkDeleteView.as_view(), name='mark_delete'),

    # Favourites urls
    path('favourite/', views.FavouriteView.as_view(), name='favourite_list'),
    path('favourite/create/', views.FavouriteCreateView.as_view(), name='favourite_create'),
    path('favourite/<int:pk>/', views.FavouriteDetailView.as_view(), name='favourite_detail'),
    path('favourite/update:<int:pk>/', views.FavouriteUpdateView.as_view(), name='favourite_update'),
    path('favourite/delete:<int:pk>/', views.FavouriteDeleteView.as_view(), name='favourite_delete'),

    # Archive urls
    path('archive/', views.ArchiveView.as_view(), name='archive_list'),
    path('archive/create/', views.ArchiveCreateView.as_view(), name='archive_create'),
    path('archive/<int:pk>/', views.ArchiveDetailView.as_view(), name='archive_detail'),
    path('archive/update:<int:pk>/', views.ArchiveUpdateView.as_view(), name='archive_update'),
    path('archive/delete/:<int:pk>/', views.ArchiveDeleteView.as_view(), name='archive_delete'),

    path('search_boards/', views.search_by_user, name='search_by_user'),
    # path('search_cards/', views.search_by_mark, name='search_by_mark'),
]
