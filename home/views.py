from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import ContactMailForm
import requests
from django.urls import reverse
from django.conf import settings

def contactView(request):
    if request.method == "GET":
        form = ContactMailForm()
    else:
        form = ContactMailForm(request.POST)
        if form.is_valid():
            try:
                name = form.cleaned_data["name"]
                email = form.cleaned_data["email"]
                message = form.cleaned_data['message']
                form.save()
                # needs crednetials before it will work
                #send_mail(name, message, email, ["admin@buildly.io"])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("success")
    return render(request, "home/contact.html", {"form": form})

def successView(request):
    return render(request, "home/success.html")


def register(request):
    if request.method == 'POST':
        organization_name = request.POST.get('organization_name')
        technical_founder = request.POST.get('technical_founder')
        agency = request.POST.get('agency')

        # Submit data to API endpoint
        api_endpoint = settings.API_URL + '/register/'
        data = {
            'organization_name': organization_name,
            'technical_founder': technical_founder,
            'agency': agency
        }
        response = requests.post(api_endpoint, data=data)

        if response.status_code == 200:
            return render(request, 'registration_success.html')
        else:
            error_message = 'Failed to register. Error code: {}'.format(response.status_code)
            return render(request, 'register.html', {'error_message': error_message})
    else:
        return render(request, 'register.html')
