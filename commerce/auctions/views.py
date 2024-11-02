from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Max

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
        context['bids'] = Bid.objects.filter(listing=requested_listing)
        context['max_bid'] = Bid.objects.filter(listing=requested_listing).aggregate(Max('bid'))['bid__max']
        return context 
    
def place_bid(request, listing_id):

    if request.method == 'POST':
        print("the authenticated user is ", request.user)
        print("the form was submitted")

    # get hold of the listing object 
        listing = Listing.objects.get(pk=listing_id)
        print("the requested listing object", listing)

    # get hold of the bid amount 
        bid = float(request.POST.get('bid'))
        if not bid:
            messages.warning("Ooops, please input a valid amount!")
            return redirect('listing_view', pk=listing_id)
        else:
            print("the bid placed is ", bid)

            # get hold of the max bid for the listing
            max_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max'] or listing.starting_bid #getting the max bid or the starting bid, if no bids exist
            print("the current max bid is ", max_bid)        
            #register the bid only if it surpasses the max bid for the listing
            if bid > max_bid:
                new_bid=Bid.objects.create(user=request.user, listing=listing, bid=bid) #the user object is accessible via request.user 
                print("the newly created Bid object is ", new_bid)
                new_bid.save()
                messages.success(request, "Your bid was successfully placed") #TODO figure out why the message appears when the user first visits the page
                return redirect('listing_view', pk=listing_id)
            else:
                messages.warning(request, 'Oops, your bid is smaller than the maximum existing bid for this listing! Increase your bid!')
                print("Oops, your bid is smaller than the maximum existing bid for this listing!")
                return redirect('listing_view', pk=listing_id)
    else:
        return redirect('listing_view', pk=listing_id)
    

