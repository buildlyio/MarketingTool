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

    COMPLETIONS_MODEL = "text-davinci-003"
    EMBEDDING_MODEL = "text-embedding-ada-002"

    openai.api_key = settings.OPENAI_API_KEY
     # Set up the OpenAI API request
    if request.method == 'POST':
        context = "Answer the question as truthfully as possible, and if you're unsure of the answer, say 'Sorry, I don't know'."
        context = prompt = """Answer the question as truthfully as possible using the provided text, and if the answer is not contained within the text below, say "I don't know"

            Context:
            Buildly helps teams create applications faster by eliminating slow setup steps and lowering the number of iterations 
            in development.  Our proprietary AI translates requirements into a technical documents and prototypes to help teams 
            start building a product faster.   The Insights management and reporting tool, makes it easy to work with remote and 
            in-house teams with single platform communication tools and faster release timelines.
            Buildly Insights can also help document your business and product ideas and securely share it with their party outsource 
            providers, investors and more with Buildly Insights.  Insights helps product teams and software developers work better 
            and faster together by translating business requirements into technical documentation, budgets, staffing and 
            architectural requirements and then uses trained AI and learning models to plan and predict release schedules.  

            The Buildly core is an open source API and Gateway + management layer that enables developers to build distributed 
            and cloud native applications without any strings, but also provides the designers and 
            frontend developers with an easy to use single point of entry for storing data and logic, as well connecting to third party tools.

            Buildly Inc. and its founders own the technology and control the software licenses, but it being open source also 
            allows forks and ownership of downstream repos by the companies or users doing the forking to within the limits of the licenses.  
            However, we also believe that the current OSI and open source licenses do not do enough to protect the rights and usage for
            SaaS companies like Buildly and our working on a new community source option that is more friendly to SaaS and hosted service 
            companies and will allow monetization of open source in a new way.

            Both the marketplace and the release management tools depend on companies having a development team (usually remote) 
            that understand good software architecture, microservices and cloud infrastructure to some level.  We have developed a 
            partner marketplace place with 20+ partner development agencies from all over the world.  These companies bring customers to 
            our platform, and we as well bring customers to them.  They are certified Buildly developer teams and work well with enterprise, 
            startup or open source project teams to migrate existing projects to cloud native approaches or build new projects with the 
            Buildly architecture.  They also bring customers on the hosted platform for release management, products tools, versioning 
            and marketplace add-ons to speed up the process and develop standardized processes.

            The Buildly Foundry combine tools, advisors and Development Team partners to help underserved communities get 
            innovative and build products for deployment on cloud native architectures as well as to our marketplace

            The Foundry includes the easy to use Open Cloud Kit to get you started fast with the Buildly Core, process and deployment 
            tools as well as multiple, recommended open source projects to help teams manage the chaos deploying an application
            Free 3 months of use of our hosted process and release tools so you and your team are always on the same page, and 
            ongoing discount for graduates. A network of trained and certified development partners
            Experienced and well trained Field CTOs to fill the gap while finding your technical co-founder free for the first 3 months.

            All this allows you to focus on the vision and stop worrying about the technical problems

            https://www.buildly.io

            http://www.github.com/buildlyio

            https://twitter.com/buildly_io

            https://www.youtube.com/channel/UCgVZzoAyC_VHASqhqc0dJXw

            http://www.instagram.com/buildly_io

            http://www.instagram.com/buildly_io

            http://www.facebook.com/buildlyio

            http://www.linkedin.com/company/buildlyio    
            """
        prompt = context + request.POST.get('prompt', '')
        print(prompt)
        response = openai.Completion.create(
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0,
            model=COMPLETIONS_MODEL
        )
        print(response.choices[0].text)
        return JsonResponse({'response': response.choices[0].text})
    else:
        # If the request is not a POST request, or the message parameter is missing, just render the chat.html template
        return render(request, 'chat.html')
openai.api_base = "https://api.openai.com/v1"
