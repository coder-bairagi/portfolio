from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    # Get Requests
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    
    # Projects URL
    path('projects', views.projects, name='projects'),
    # Movie recommendation system
    path('projects/movie-recommendation-system', views.mrs_index, name='mrs.index'),
    path('projects/movie-recommendation-system/<str:movie_name>', views.get_movie_details, name='get_movie_details'),
    # Olympic data analysis
    path('projects/olympic-data-analysis', views.oda_index, name='oda.index'),
    # Property price prediction
    path('projects/property-price-prediction', views.ppp_index, name='ppp.index'),

    # Post Requests
    path('get_recommendations/', views.get_recommendations, name='get_recommendations'),
    path('get_price/', views.get_price, name='get_price'),
    path('send_email/', views.send_email, name='send_email'),
]