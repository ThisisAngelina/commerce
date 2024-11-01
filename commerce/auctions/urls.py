from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListingListView.as_view(), name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('new', views.ListingCreateView.as_view(), name='listing_create'),
    path('listing/<int:pk>', views.ListingDetailView.as_view(), name='listing_view'),

    #add name='bid' url for bidding
    
]
