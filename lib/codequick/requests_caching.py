# Standard Library Imports
import io

# Requests Imports
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.response import HTTPResponse

# Package imports
from .http_caching import CacheAdapterCommon, session_common

# Disable requests ssl warnings
disable_warnings()


@session_common(requests.session)
def session(session_obj):
    """ Create requests HTTPAdapter """
    adapter = CacheAdapter()
    session_obj.mount("http://", adapter)
    session_obj.mount("https://", adapter)


class CacheAdapter(HTTPAdapter, CacheAdapterCommon):
    # Class vars
    cache_dir_name = u"cache_requests"

    def __init__(self, *args, **kwargs):
        # Call Parent init method
        super(CacheAdapter, self).__init__(*args, **kwargs)

    @staticmethod
    def get_url(request):
        """ Return the url of the request """
        return request.url

    @staticmethod
    def get_method(request):
        """ Return of method of the request """
        return request.method

    @staticmethod
    def get_status(response):
        """ Return the status code of the response """
        return response.status

    @staticmethod
    def update_cache(cache, response):
        """ Update the __cache with the new server response """

        # Fetch the body of the response
        if response.chunked:
            body = "".join([chunk for chunk in response.stream(decode_content=True)])
        else:
            body = response.read(decode_content=True)

        # Now update the __cache with the appropriate data
        cache.update(body=body, headers=response.headers, status=response.status, reason=response.reason,
                     version=response.version, strict=response.strict)

    def send(self, request, **kwargs):
        """
        Use the request information to check if it exists in the __cache
        and return cached response if so. Else forward on the said request
        """

        # Check if reuest is cached and also fresh
        cache_resp = self.check_cache(request)

        if cache_resp:
            # We have a cached response so use it
            return cache_resp
        else:
            # Forward the request on to the server
            kwargs["verify"] = False
            return super(CacheAdapter, self).send(request, **kwargs)

    def build_response(self, request, response, from_cache=False):
        """ Build a requests response object """
        new_response = self.handle_response(request, response, from_cache=from_cache)
        return super(CacheAdapter, self).build_response(request, new_response if new_response else response)

    def handle_304(self, cache, request, response):
        """ Refresh the __cache sence the __cache matches the server """

        # Read a possible response body and release the connection.
        response.read(decode_content=False)
        response.release_conn()

        # Set response to cached response
        return self.prepare_cached_response(cache.response, request)

    def prepare_cached_response(self, response, request=None, from_cache=False):
        """ Prepare the cached response so that requests can handle it """
        body = io.BytesIO(response.pop("body"))
        cached_response = HTTPResponse(body=body, preload_content=False, **response)
        if from_cache:
            return self.build_response(request, cached_response, from_cache=True)
        else:
            return cached_response
