from django.shortcuts import render

def index(request):
    return render(request, 'documentation/index.html')

def api_routes(request):
    return render(request, 'documentation/api_routes.html')

def models_doc(request):
    return render(request, 'documentation/models.html')

def frontend_guidelines(request):
    return render(request, 'documentation/frontend_guidelines.html')