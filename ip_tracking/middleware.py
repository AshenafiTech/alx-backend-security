q                                                               
from django.http import HttpResponseForbidden
from .models import BlockedIP

class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden('Forbidden: Your IP is blocked.')
        return self.get_response(request)
