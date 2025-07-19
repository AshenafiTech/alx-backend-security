
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseForbidden
from django_ratelimit.decorators import ratelimit
from django.shortcuts import render

@ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            return HttpResponseForbidden('Too many login attempts. Please try again later.')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('Login successful!')
        else:
            return HttpResponse('Invalid credentials.', status=401)
    return render(request, 'login.html')
