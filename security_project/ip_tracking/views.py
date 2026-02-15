from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return HttpResponse("Welcome to the IP Tracking Demo! Check the admin panel to see logged IPs.")

def test_page(request):
    return HttpResponse("This is a test page. Your visit has been logged!")