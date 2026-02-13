from django.shortcuts import render
from django.http import HttpResponse

def kkk(request):
    return HttpResponse("This is app1")

def home(request):
    return render(request, 'home.html') 
