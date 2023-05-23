from django.shortcuts import render, HttpResponse
from home.models import Contact

# Create your views here.
def home(request):
    context = {"name": "Nasir", "title": "Portfolio"}
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def projects(request):
    return render(request, "projects.html")


def contact(request):
    if request.method=="POST":
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        desc = request.POST['desc']
        
        ins = Contact(name=name , email=email , phone_number=phone_number, desc=desc)
        ins.save()
        print("database updated")
    return render(request, "contact.html")


def blog(request):
    return render(request, "blog.html")
