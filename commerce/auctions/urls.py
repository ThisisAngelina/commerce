from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListingListView.as_view(), name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('new', views.ListingCreateView.as_view(), name='listing_create'),
    path('listing/<int:pk>', views.ListingDetailView.as_view(), name='listing_view'),
    path('bid/<int:listing_id>', views.place_bid, name='bid'),
    path('watch/<int:listing_id>', views.add_to_remove_from_watchlist, name='add_to_remove_from_watchlist'),
    path('close/<int:listing_id>', views.close_listing, name='close_listing'),
    path('comment/<int:listing_id>', views.comment, name='comment'),

    #add name='bid' url for bidding
    
]
