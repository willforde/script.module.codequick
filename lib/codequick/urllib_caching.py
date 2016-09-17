# Standard Library Imports
import htmlentitydefs
import urlparse
import httplib
import urllib2
import urllib
import json
import zlib
import re
import io

# Package imports
from .support import logger
from .http_caching import CacheAdapterCommon, session_common


class Session(object):
    """
    Provides cookie persistence, connection-pooling, and configuration.

    Note
    ----
    This is a emulated session object that is a simple copy of the requests session object

    Attributes
    ----------
    headers : dict
        A dictionary of headers to be sent on each Request sent from this Session.

    params : dict
        Dictionary of querystring data to attach to each Request.
    """

    def __init__(self):
        self.__handleList = []
        self.__opener = None
        self.headers = {}
        self.params = {}

    def mount(self, adapter):
        """ Registers a connection adapter """
        self.__handleList.append(adapter)

    def request(self, method, url, params=None, data=None, headers=None, timeout=None):
        """
        Constructs a Request, prepares it and sends it. Returns Response object.

        Parameters
        ----------
        method : str
            The type of http request to make.

        url : bytestring
            The url of the requested resource.

        params : dict, optional
            A dict of key, value pairs to add to the url as a query.

        data : dict or bytestring, optional
            Data to send to the server when using a post request.

        headers : dict, optional
            Headers to send with the request.

        timeout : int, optional
            Timeout in seconds to wait for a slow connection to respond.
        """
        # Add session and request params to http request
        if self.params or params:
            if self.params and params:
                _params = self.params.copy()
                _params.update(params)
                params = _params
            elif self.params:
                params = self.params

            params = urllib.urlencode(params)
            url_parts = urlparse.urlsplit(url)
            url = urlparse.urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, params, url_parts.fragment))

        # Add session and request headers to http request
        if self.headers and headers:
            _headers = self.headers.copy()
            _headers.update(headers)
            headers = _headers
        elif self.headers:
            headers = self.headers

        # Fetch the request opener
        if self.__opener:
            opener = self.__opener
        else:
            # Build and set a new urllib2 opener
            self.__opener = opener = urllib2.build_opener(*self.__handleList)

        # Make a http get request
        if method.lower() == "get":
            request = urllib2.Request(url, headers=headers)
            response = opener.open(request, timeout=timeout)
            return Response(request, response)

        # Make a http post request
        elif method.lower() == "post":
            request = urllib2.Request(url, data=data, headers=headers)
            response = opener.open(request, timeout=timeout)
            return Response(request, response)

    def get(self, url, **kwargs):
        """ Sends a GET request. Returns Response object.

        Parameters
        ----------
        url : bytestring
            The url of the requested resource.

        kwargs : optional
            Optional arguments that request takes.
        """
        return self.request("get", url, **kwargs)

    def post(self, url, **kwargs):
        """ Sends a POST request. Returns Response object.

        Parameters
        ----------
        url : bytestring
            The url of the requested resource.

        kwargs : optional
            Optional arguments that request takes.
        """
        return self.request("post", url, **kwargs)


@session_common(Session)
def session(session_obj):
    """ Create urllib Adapter """
    adapter = CacheAdapter()
    session_obj.mount(adapter)


class Response(object):
    """ The Response object, which contains a server's response to an HTTP request. """

    def __init__(self, request, response):
        self.__headers = headers = response.info()
        self.__response = response
        self.__content = None
        self.__text = None

        # Fetch the charset encoding method used for the content
        charset = headers.getparam("charset") or headers.getparam("encoding")
        self.encoding = charset

        # Set some instance variables
        self.url = response.geturl()
        self.request = request

    @property
    def content(self):
        """ Content of the response, in bytes. """
        if self.__content is not None:
            return self.__content

        # Check if Response need to be decoded, else return raw response
        content_encoding = headers.get(u"content-encoding", u"")
        content = self.__response.read()

        try:
            # Decompress the content if content is gzip encoded
            if "gzip" in content_encoding:
                content = zlib.decompress(content, 16 + zlib.MAX_WBITS)

            # Decompress the content if content is compressed using deflate
            elif "deflate" in content_encoding:
                content = zlib.decompress(content)

        except zlib.error as e:
            logger.error("Failed to decompress content body: %s", str(e))
            raise

        else:
            self.__content = content
            return content

    @property
    def text(self):
        """
        Content of the response, in unicode.

        Note
        ----
        If Response.encoding is None, then UTF8 encoding will be used. If that faileds
        then iso-8859-1 (latin 1) will be used.

        Note
        ----
        The encoding of the response content is determined based solely on HTTP headers,
        following RFC 2616 to the letter. If you can take advantage of non-HTTP knowledge to make a
        better guess at the encoding, you should set r.encoding appropriately before accessing this property.
        """
        if self.__text:
            return self.__text
        else:
            # Convert from bytes to unicode
            try:
                unicode_data = unicode(self.content, self.encoding if self.encoding else "utf8")
            except UnicodeError:
                unicode_data = unicode(self.content, "iso-8859-1")

            # Unescape the content
            return self._unescape(unicode_data)

    @property
    def headers(self):
        """
        Case-insensitive Dictionary of Response Headers.

        Returns
        -------
        dict
        """
        return self.__headers

    @property
    def status_code(self):
        """ Integer Code of responded HTTP Status, e.g. 404 or 200.

        Returns
        -------
        int
        """
        return self.__response.getcode()

    @property
    def reason(self):
        """ Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".

        Returns
        -------
        str
        """
        return self.__response.msg

    @property
    def raw(self):
        """ File-like object representation of response (for advanced usage). """
        return self.__response

    def json(self, **kwargs):
        """ Returns the json-encoded content of a response, if any. """
        return json.loads(self.content, encoding=self.encoding, **kwargs)

    def close(self):
        """
        Releases the connection back to the pool. Once this method has been called the underlying
        raw object must not be accessed again.
        """
        self.__response.close()

    @staticmethod
    def _unescape(text):
        # Add None Valid HTML Entities
        htmlentitydefs.name2codepoint["apos"] = 0x0027

        def fixup(m):
            # Fetch Text from Group
            escaped_text = m.group(0)

            # Check if Character is A Character Reference or Named Entity
            if escaped_text[:2] == "&#":  # Character Reference
                try:
                    if escaped_text[:3] == "&#x":
                        return unichr(int(escaped_text[3:-1], 16))
                    else:
                        return unichr(int(escaped_text[2:-1]))
                except ValueError:
                    return escaped_text

            else:  # Named Entity
                try:
                    return unichr(htmlentitydefs.name2codepoint[escaped_text[1:-1]])
                except KeyError:
                    return escaped_text

        # Return Clean string using accepted encoding
        return re.sub("&#?\w+;", fixup, text)


class CacheAdapter(urllib2.BaseHandler, CacheAdapterCommon):
    # Class vars
    from_cache = False

    @staticmethod
    def get_url(request):
        """ Return the url of the request """
        return request.get_full_url()

    @staticmethod
    def get_method(request):
        """ Return of method of the request """
        return request.get_method()

    @staticmethod
    def get_status(response):
        """ Return the status code of the response """
        return response.code

    @staticmethod
    def http_request(request):
        """ Add some extra headers to request """
        request.add_header("accept-encoding", "gzip,deflate")
        return request

    @staticmethod
    def update_cache(cache, response):
        """ Update the cache with the new server response """

        # Fetch response headers
        headers = response.info()
        body = response.read()

        # Now update the cache with the appropriate data
        cache.update(body=body, headers=headers, status=response.code,
                     reason=response.msg)

    def default_open(self, request):
        """
        Use the request information to check if it exists in the cache
        and return cached response if so. Else forward on the said request
        """
        self.from_cache = False
        return self.check_cache(request)

    def http_response(self, request, response):
        """ Cache the response and return cached response """
        new_response = self.handle_response(request, response, from_cache=self.from_cache)
        self.from_cache = False
        return new_response

    def handle_304(self, cache, request, _):
        """ Refresh the cache sence the cache matches the server """
        return self.prepare_cached_response(cache.response, request)

    def prepare_cached_response(self, response, request, from_cache=False):
        """ Prepare the cached response so that urllib can handle it """
        self.from_cache = from_cache
        url = self.get_url(request)

        # Return the prepared cache response
        return HTTPResponse(response["body"], response["headers"], response["status"], response["reason"], url)

    # Redirect HTTPS Requests and Responses to HTTP
    https_request = http_request
    https_response = http_response


class HTTPResponse(urllib2.addinfourl):
    def __init__(self, body=None, headers=None, status=None, reason=None, url=None):
        # Convert headers to a httplib.HTTPMessage instance
        msg_headers = httplib.HTTPMessage(io.BytesIO(""))
        for key, value in headers.iteritems():
            msg_headers.addheader(key, value)

        # Farward on the the source class
        urllib2.addinfourl.__init__(self, io.BytesIO(body), msg_headers, url, status)
        self.msg = reason
