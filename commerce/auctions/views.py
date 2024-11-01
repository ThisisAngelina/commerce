from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy

from .models import *
from .forms import *

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

# let users create new listings
class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'auctions/listing_create.html'
    success_url = reverse_lazy('index') 


# let users view all listings
class ListingListView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'auctions/index.html'
    context_object_name = 'listings'

# let users view the detailed page of a particular listing
class ListingDetailView(LoginRequiredMixin, DetailView):
    model = Listing
    template_name = 'auctions/listing_view.html'
    context_object_name = 'listing'

    # get hold of additional context (data contained in other models) and update the view's context to pass in additional info, beyond the generic DetailView
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requested_listing = self.kwargs.get('pk')
        context['bids'] = Bid.objects.filter(listing_id=requested_listing) #grabbing the set of all the bids made for that listing
        context['max_bid'] = context['bids'][0] #TODO to check that we are getting the highest bid this way #by the design of our Bid model, we should be getting the highest bid as the first element of the set 
        return context 
    
def place_bid(request, listing_id):

    if request.method == 'POST':
        pass 

    # get hold of the user object
   #user = 

    # get hold of the listing object 

    # get hold of the bid amount 

    # get hold of the max bid for the listing

    #register the bid only if it surpasses the max bid for the listing

    #otherwise, display an error in the html
   # message = 
    
   # Bid.objects.create()

    
