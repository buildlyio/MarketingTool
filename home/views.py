from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import ContactMailForm
import requests
from django.urls import reverse
from django.conf import settings
import openai


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

# views.py
from django.shortcuts import render



def register(request):
    if request.method == 'POST':

        # Authenticating with OAuth2 in Requests
        from requests_oauthlib import OAuth2Session

        # Inlcude your data
        client_id = "c5y6V0rxqAKFWeakxkIvQLTGPj6NmaRyUfBmt6J8"
        client_secret = "MhHHQyo25qMITKzp7AsvtZMg2EbDYKKOyeudcGRgIO1IKabtbzUx5yekPMwtuLXHXv9ZC1DbqSBSTW13ed2RUK6NNz9DFDhKT58eOKiqZDEaG5EanVLV8uUqw7ovc1Oy"
        redirect_uri = settings.BASE_URL + "insights"

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
        head = {'Authorization': 'token {}'.format(token)}
        response = requests.post(api_endpoint, data=data, headers=head)

        if response.status_code == 200:
            return render(request, 'registration_success.html')
        else:
            error_message = 'Failed to register. Error code: {}'.format(response.status_code)
            return render(request, 'home/register_dev.html', {'error_message': error_message})
    else:
        return render(request, 'home/register_dev.html')

from django.shortcuts import render, redirect
from django.conf import settings
from web3 import Web3

def display_contract(request, contract_id):
    # Retrieve the contract from the database
    contract = Contract.objects.get(id=contract_id)
    # Generate a unique filename for the contract
    filename = f"contract_{contract.id}.pdf"
    # Save the contract to a temporary file
    with open(filename, 'wb') as f:
        f.write(contract.pdf.read())
    # Connect to the Ethereum blockchain
    w3 = Web3(Web3.HTTPProvider(settings.ETHEREUM_NODE_URL))
    # Get the contract ABI and address
    abi = settings.CONTRACT_ABI
    address = settings.CONTRACT_ADDRESS
    # Create a contract instance
    contract_instance = w3.eth.contract(address=address, abi=abi)
    # Encode the contract file as base64
    with open(filename, 'rb') as f:
        contract_data = base64.b64encode(f.read()).decode('utf-8')
    # Sign the contract with the second party's private key
    signature = sign_document(contract_data, request.user.private_key)
    # Upload the contract to the blockchain
    tx_hash = contract_instance.functions.upload_contract(contract_data, signature).transact({'from': request.user.eth_address})
    # Wait for the transaction to be mined
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # Get the blockchain address of the uploaded contract
    blockchain_address = contract_instance.functions.get_contract_address(contract_data).call()
    # Render the template with the PDF contract and blockchain address
    return render(request, 'smartcontract.html', {'pdf_url': f"/media/{contract.pdf}", 'contract_id': contract_id, 'blockchain_address': blockchain_address})

# views.py
from django.shortcuts import render

def chat_view(request):
    context = {}
    return render(request, 'chat.html', context)


import requests
from django.shortcuts import render
from django.http import JsonResponse

def chatbot(request):
    openai.api_key = settings.OPENAI_API_KEY
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            # Set up the OpenAI API request
            url = 'https://api.openai.com/v1/engines/davinci-codex/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai.api_key}' # Replace with your actual OpenAI API key
            }
            data = {
                'prompt': message,
                'max_tokens': 50,
                'n': 1,
                'stop': '\n'
            }

            # Send the request to OpenAI's API
            response = requests.post(url, headers=headers, json=data)

            # Get the AI's response from the API's JSON response
            ai_response = response.json()['choices'][0]['text']

            # Return the AI's response as a JSON object to the client
            return JsonResponse({'response': ai_response})
    
    # If the request is not a POST request, or the message parameter is missing, just render the chat.html template
    return render(request, 'chat.html')
