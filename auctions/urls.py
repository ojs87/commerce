from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.createlisting, name="createlisting"),
    path("listing/<str:slug>", views.listingview, name="listingview"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories/<str:category>", views.categories, name="categories")
]
