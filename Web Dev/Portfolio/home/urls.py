from django.contrib import admin
from django.urls import path, include
from home import views

#Django admin header customisations
admin.site.site_header = "Admin Management Page"
admin.site.site_title = "Admin Portal"
urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('projects', views.projects, name='projects'),
    path('contact', views.contact, name='contact'),
    path('blog', views.blog, name='blog')
]
