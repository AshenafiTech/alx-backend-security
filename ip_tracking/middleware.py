
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
import geoip2.database
import os

GEOIP_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'GeoLite2-City.mmdb')

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        country = None
        city = None

        # Check cache for geolocation
        geo_cache_key = f'geoip_{ip}'
        geo = cache.get(geo_cache_key)
        if geo:
            country, city = geo.get('country'), geo.get('city')
        else:
            if os.path.exists(GEOIP_DB_PATH):
                try:
                    with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
                        response = reader.city(ip)
                        country = response.country.name
                        city = response.city.name
                        cache.set(geo_cache_key, {'country': country, 'city': city}, 60*60*24)
                except Exception:
                    pass

        # Log the request
        RequestLog.objects.create(ip_address=ip, path=path, country=country, city=city)

        # Block if IP is blacklisted
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden('Forbidden: Your IP is blocked.')
        return self.get_response(request)

