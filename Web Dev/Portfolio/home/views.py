from django.shortcuts import render, HttpResponse


# Create your views here.
def home(request):
    context = {"name": "Nasir", "title": "Portfolio"}
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def projects(request):
    return render(request, "projects.html")


def contact(request):
    return render(request, "contact.html")


def blog(request):
    return render(request, "blog.html")
