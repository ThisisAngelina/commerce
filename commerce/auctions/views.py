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
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

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
    return HttpResponseRedirect(reverse("login"))


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
        user = self.request.user
        requested_listing_id = self.kwargs.get('pk')
        requested_listing = Listing.objects.get(pk=requested_listing_id)

        #bids-related context
        context['bids'] = Bid.objects.filter(listing=requested_listing)
        context['max_bid'] = Bid.objects.filter(listing=requested_listing).aggregate(Max('bid'))['bid__max']

        #watchlist-related context

        #check if the listing is already in the user's watchlist
        try:
            Watchlist.objects.get(user=user, listing=requested_listing)
            context['watchlist_button'] = "Remove from" #if the item is already in the user's watchlist, make it impossible to add to the watchlist
        except ObjectDoesNotExist:
            context['watchlist_button'] = "Add to"
        
        # 'close this listing' button-related context
        if requested_listing.user == user:
            context['can_close'] = True #needed so that the 'close this listing' button is displayed only if the listing's author is the signed in user herself

        # context for whether the listing is already closed 
        if requested_listing.open == False:
            context['closed'] = True #display a note on the listing_view page that the listing is closed 
        
        # context for whether the winner of the auction is the signed-in user 
        if requested_listing.winner == user:
            context['you_won'] = True

        return context 


# let users place bids for items
@login_required   
def place_bid(request, listing_id):

    if request.method == 'POST':
    
    # get hold of the listing object 
        listing = Listing.objects.get(pk=listing_id)

    # get hold of the bid amount 
        bid = float(request.POST.get('bid'))
        if not bid:
            messages.warning("Ooops, please input a valid amount!")
            return redirect('listing_view', pk=listing_id)
        else:
            # get hold of the max bid for the listing
            max_bid = Bid.objects.filter(listing=listing).aggregate(Max('bid'))['bid__max'] or listing.starting_bid #getting the max bid or the starting bid, if no bids exist
            #register the bid only if it surpasses the max bid for the listing
            if bid > max_bid:
                new_bid=Bid.objects.create(user=request.user, listing=listing, bid=bid) #the user object is accessible via request.user 
                new_bid.save()
                messages.success(request, "Your bid was successfully placed") 
                return redirect('listing_view', pk=listing_id)
            else:
                messages.warning(request, 'Oops, your bid is smaller than the maximum existing bid for this listing! Increase your bid!')
                return redirect('listing_view', pk=listing_id)
    else:
        return redirect('listing_view', pk=listing_id)
    
#let users add the listing to their watchlist from the button on the listing_view page.
#TODO If the item is already on the watchlist, the user should be able to remove it.
@login_required
def add_to_remove_from_watchlist(request, listing_id):

    # define which listing the user is trying to perform the action for
    listing = Listing.objects.get(pk=listing_id)

    # check if the listing is already in the user's watchlist
    watchlist_entry, created = Watchlist.objects.get_or_create(user=request.user, listing=listing)

    if created:
        # item was not in the watchlist and has been added
        messages.success(request, "The item was added to your watchlist")
    else:
        # item was already in the watchlist, so remove it
        watchlist_entry.delete()
        messages.success(request, "The item was removed from your watchlist")

    return redirect('listing_view', pk=listing_id)


# allow the creator of the listing to close the listing
@login_required
def close_listing(request, listing_id):
    
    listing = Listing.objects.get(pk=listing_id)
    listing.open = False 
    listing.save()
    
    #define the winner of the auction: the person with the maximum bid 
    try:
        purchaser = Bid.objects.filter(listing=listing).order_by('-bid').first().user
        sold_for = Bid.objects.filter(listing=listing).order_by('-bid').first().bid
        #save this information in the listing's Listing model object
        listing.winner = purchaser 
        listing.sold_for = sold_for
        listing.save()
        messages.success(request, f"The listing was successfully closed. The winner is  {purchaser.username}")
        return redirect('listing_view', pk=listing_id)
    
    except ObjectDoesNotExist: #if there were no bids for the listing
        listing.winner = None
        listing.save()
        messages.success(request, "The listing was successfully closed")
        return redirect('listing_view', pk=listing_id)


        



    

