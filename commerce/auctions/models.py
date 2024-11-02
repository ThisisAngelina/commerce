from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=200, unique = True) #make sure there are no duplicate Categories by setting the unique property as True
    
    def __str__(self):
        return self.name #override the standard str method to return the category's name



class Listing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings") #every category can have multuple listings. Every listing has its category
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", null=True)
    title = models.CharField(max_length=200)     
    description = models.CharField(max_length=1000, validators=[MinLengthValidator(20)]) # asking users to input a listing description that is at least 100 characters long
    starting_bid = models.FloatField(validators=[MinValueValidator(0.01)])
    image_url = models.URLField(max_length=200, blank = True, null = True) #the url can be blank
    open =  models.BooleanField(default = True) #the standard status for a listing is "open"
    created_at =models.DateTimeField(auto_now_add=True) #automatically add the timestamp to the listing - useful to sort the listings chronologically for the display
    
    def __str__(self):
        return f"{self.title} starting at {self.starting_bid}"



class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlisted")

    class Meta:
        unique_together = ("user", "listing") #make sure a user cannot have duplicate listings in their watchlist

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid = models.FloatField(validators=[MinValueValidator(0.01)])

    class Meta:
        ordering = ['-bid']  # automatically orders bids from highest to lowest in any selections (like in a filter set)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing.title}"

