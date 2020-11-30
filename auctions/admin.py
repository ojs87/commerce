from django.contrib import admin
from .models import Auction, Bid

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("name", "categories", "auctionauthor")

class BidAdmin(admin.ModelAdmin):
    list_display = ("auction", "user", "bidvalue")

# Register your models here.
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
