    API endpoints:
        api/boards/
                /,                  -- Board List Create View
                <int:pk>/           -- Board Detail Put Patch Delete View
            
                # Members API urls
                members/            -- Members List View
            
                # Column API urls
                column/             -- Column List Create View
                column/<int:pk>     -- Column Detail Put Patch View
            
                # Card API with Comments in detail view urls
                card/               -- Card List Create View
                card/<int:pk>       -- Card Detail Put Patch Delete View
            
                # CheckList API urls
                checklist/card: <card_id>   -- CheckList List Based on Cards View
                checklist/<int:pk>          -- Checklist Detail View
            
                # Archive API urls
                path('archive/', views.ArchiveListCreateAPIView.as_view()),
            
                # File API urls
                path('file/', views.FileLisCreateAPIView.as_view()),
                path('file/', views.FileDetailDeleteAPIView.as_view()),