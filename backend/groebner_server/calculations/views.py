from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")

def submit_calculation(request):
    print('got calc request')
    if request.method == 'POST' and request.content_type == 'application/json': #probably received a calculation to be done
        print('test')
    return HttpResponse("Hello, world.")
