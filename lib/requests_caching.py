# Standard Library Imports
from functools import partial
import io

# Requests Imports
import requests
from requests.adapters import HTTPAdapter
# noinspection PyUnresolvedReferences
from requests.packages.urllib3 import disable_warnings
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.response import HTTPResponse

# Package imports
from urlquick import CacheAdapter as BaseCacheAdapter

# Disable requests ssl warnings
disable_warnings()


class Session(requests.Session):
    """Patched session class that add's CacheAdapter."""
    def __init__(self):
        super(Session, self).__init__()
        self.mount('https://', CacheAdapter())
        self.mount('http://', CacheAdapter())


class CacheAdapter(HTTPAdapter, BaseCacheAdapter):
    @staticmethod
    def callback(response):
        """
        Callback object used by BaseCacheAdapter.handle_response to access
        response data and keep compatibility with urlquick.

        :param urllib3.response.HTTPResponse response:
        :return: Tuple of response data. body, headers ...
        :rtype: tuple
        """
        # Fetch the body of the response
        if response.chunked:
            body = b"".join([chunk for chunk in response.stream(decode_content=False)])
        else:
            body = response.read(decode_content=False)

        # Release connection so it can be reused
        response.release_conn()
        return response.headers, body, response.status, response.reason, response.version, response.strict

    @staticmethod
    def prepare_response(resp):
        """
        Prepare the cached response so that requests can handle it.

        :param urlquick.CacheResponse resp: Cached response.
        :returns: A urllib3 response object.
        :rtype: urllib3.response.HTTPResponse
        """
        body = io.BytesIO(resp.body)
        return HTTPResponse(body=body, headers=resp.headers, status=resp.status, version=resp.version,
                            reason=resp.reason, strict=resp.status, preload_content=False)

    def send(self, request, **kwargs):
        """
        Use the request information to check if it exists in the cache
        and return cached response if so. Else forward on the request.

        :param requests.PreparedRequest request: Requests request object
        :returns: A requests response object.
        :rtype: requests.Response
        """
        # Check if reuest is cached and fresh
        cache_resp = self.cache_check(request.method, request.url, request.body, request.headers)
        if cache_resp:
            response = self.prepare_response(cache_resp)
            return super(CacheAdapter, self).build_response(request, response)
        else:
            # Forward the request to the server
            kwargs["verify"] = False
            return super(CacheAdapter, self).send(request, **kwargs)

    def build_response(self, request, response):
        """
        Build a requests response object.

        :param requests.PreparedRequest request: Requests request object
        :param urllib3.response import HTTPResponse response: Request response object.
        :returns: A requests response object.
        :rtype: requests.Response
        """
        callback = partial(self.callback, response)
        cache_resp = self.handle_response(request.method, response.status, callback)
        if cache_resp:
            response = self.prepare_response(cache_resp)

        # Send the urllib3 response to requests, for requests to build it's response
        return super(CacheAdapter, self).build_response(request, response)


# Monkey patch requests session class with custom session class
requests.Session = requests.sessions.Session = Session
