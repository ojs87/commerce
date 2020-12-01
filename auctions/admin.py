from django.contrib import admin
from .models import Auction, Bid, User, Comment

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("name", "categories", "auctionauthor")

class BidAdmin(admin.ModelAdmin):
    list_display = ("auction", "user", "bidvalue")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("auction", "user")

# Register your models here.
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)
