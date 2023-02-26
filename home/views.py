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

        # Authenticating with OAuth2 in Requests
        from requests_oauthlib import OAuth2Session

        # Inlcude your data
        client_id = "c5y6V0rxqAKFWeakxkIvQLTGPj6NmaRyUfBmt6J8"
        client_secret = "MhHHQyo25qMITKzp7AsvtZMg2EbDYKKOyeudcGRgIO1IKabtbzUx5yekPMwtuLXHXv9ZC1DbqSBSTW13ed2RUK6NNz9DFDhKT58eOKiqZDEaG5EanVLV8uUqw7ovc1Oy"
        redirect_uri = "http:127.0.0.1:8000/insights"

        # Create a session object
        oauth = OAuth2Session(client_id, redirect_uri = redirect_uri)

        # Fetch a token
        token_url = settings.INSIGHTS_API_URL + 'oauth/accesstokens'
        token = oauth.fetch_token(token_url, client_secret = client_secret)

        # Get your authenticated response
        resp = oauth.get("URL to the resource")

        print(resp)


        organization = request.POST.get('organization')
        technical_founder = request.POST.get('technical_founder')
        agency = request.POST.get('agency')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('user_name')
        type = request.POST.get('type')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Submit data to API endpoint
        api_endpoint = settings.INSIGHTS_API_URL + 'coreuser'
        print(api_endpoint)
        data = {
            'organization_name': organization,
            'technical_founder': technical_founder,
            'user_type': type,
            'agency': agency,
            'first_name': first_name,
            'last_name': last_name,
            'username': user_name,
            'password': password,
            'email': email,
        }
        response = requests.post(api_endpoint, data=data)

        if response.status_code == 200:
            return render(request, 'registration_success.html', headers={'Authorization': 'access_token myToken'})
        else:
            error_message = 'Failed to register. Error code: {}'.format(response.status_code)
            return render(request, 'home/register_dev.html', {'error_message': error_message})
    else:
        return render(request, 'home/register_dev.html')
