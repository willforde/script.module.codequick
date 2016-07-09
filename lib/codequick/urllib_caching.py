# Standard Library Imports
import os
import re
import zlib
import time
import base64
import urllib
import urllib2
import httplib
import hashlib
import urlparse
import StringIO
import functools
import htmlentitydefs
import json

# Package imports
from .api import refresh, logger


def _full_cache_dir(cache_dir):
    """ Return cache directory with sub directory added """
    return os.path.join(cache_dir, u"cache-basic")


def cache_session(cache_dir, max_age=0):
    """
    Create request session with support for http caching

    cache_dir : string or unicode --- Directory where to store the cache files
    [max_age] : integer --- Max age that the cache can be before it becomes stale (default 0)
    [max_retries] : integer --- Max amount of retries before request gives up and raises an error (default 0)
    """

    # Create session object
    session = Session()

    # Add max age to header
    session.headers["X-Max-Age"] = max_age

    # Create a HTTPAdapter Object to be used in requests
    cache_dir = _full_cache_dir(cache_dir)
    adapter = CacheAdapter(cache_dir, max_age)

    # Mount The new adapter to the current request session
    session.mount(adapter)
    return session


class RequestRes(object):
    def __init__(self, response):
        self.status_code = response.getcode()
        self.headers = headers = response.info()
        self.reason = response.msg
        content = response.read()
        response.close()
        self.encoding = None
        self.__text = None
        self.url = response.geturl()

        # Check if Response need to be decoded, else return raw response
        charset = headers.getparam("charset") or headers.getparam("encoding")
        if charset:
            self.encoding = charset
        content_encoding = headers.get(u"content-encoding")

        # If content is compressed then decompress and decode into unicode
        try:
            print
            "# len compressed", len(content)
            if content_encoding and "gzip" in content_encoding:
                content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
            elif content_encoding and "deflate" in content_encoding:
                content = zlib.decompress(content)

        except zlib.error as e:
            print
            "error: %s" % e

        else:
            print
            "# len uncompressed", len(content)
            self.content = content

    @property
    def text(self):
        if self.__text:
            return self.__text
        else:
            # Convert html to unicode
            try:
                unicode_data = unicode(self.content, self.encoding if self.encoding else "utf8")
            except UnicodeError:
                unicode_data = unicode(self.content, "iso-8859-1")

            # Unescape the content if requested
            return self._unescape(unicode_data)

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

    def json(self, **kwargs):
        return json.loads(self.content, encoding=self.encoding, **kwargs)

    @property
    def elapsed(self):
        return 0.0

    def close(self):
        pass


class Session(object):
    def __init__(self):
        self.handleList = []
        self.headers = {}
        self.__opener = None

    def mount(self, adapter):
        self.handleList.append(adapter)

    def request(self, method, url, params=None, data=None, headers=None, timeout=None):
        if params:
            params = urllib.urlencode(params)
            url_parts = urlparse.urlsplit(url)
            url = urlparse.urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, params, url_parts.fragment))

        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)

        if self.__opener:
            opener = self.__opener
        else:
            self.__opener = opener = urllib2.build_opener(*self.handleList)

        if method.lower() == "get":
            request = urllib2.Request(url)  # , headers if headers else {)
            response = opener.open(request, timeout=timeout)
            return RequestRes(response)
        elif method.lower() == "post":
            request = urllib2.Request(url, data, req_headers if req_headers else None)
            response = opener.open(request, timeout=timeout)
            return RequestRes(response)

    def get(self, url, params=None, **kwargs):
        return self.request("get", url, params, **kwargs)

    def post(self, url, data, **kwargs):
        return self.request("post", url, data=data, **kwargs)


class CacheAdapter(urllib2.BaseHandler):
    def __init__(self, cache_dir, max_age):
        self._cache_dir = cache_dir
        self._max_age = max_age
        self.from_cache = False
        self._cache = None
        self._before = None

    @staticmethod
    def http_request(request):
        """ Add Accept-Encoding & User-Agent Headers """
        request.add_header("Accept-encoding", "gzip, deflate")
        request.add_header("Accept-language", "en-gb,en-us,en")
        return request

    def default_open(self, request):
        max_age = 0 if refresh is True else int(request.headers.pop("X-Max-Age", self._max_age))
        self.from_cache = False

        url = request.get_full_url()
        method = request.get_method()
        if method == "GET":
            # Initialize Cache Handler
            hash_file = self._encode_url(url)
            self._cache = cache = CacheHandler(self._cache_dir, hash_file, preload_content=True)
            if cache.exists():
                if cache.fresh(max_age):
                    # Build the request response and return
                    self.from_cache = True
                    return cache.response(url)
                else:
                    # Set cache headers to allow for 304 Not Modified response
                    for key, value in cache.conditional_headers.iteritems():
                        request.add_header(key, value)

        if self.from_cache is False:
            logger.debug("%s Requesting Url: %s", method, url)
            self._before = time.time()

    @staticmethod
    def _encode_url(url):
        """ Return url as a sha1 encoded hash """
        if "#" in url:
            url = url[:url.find("#")]
        return hashlib.sha1(url).hexdigest()

    def http_response(self, request, response):
        if self.from_cache:
            return response
        elif request.get_method() == "GET":
            logger.debug("HTTP Request took %s seconds to complete", time.time() - self._before)
            # Create cache object if for some reason it was not already created
            if self._cache is None:
                hash_file = self._encode_url(request.get_full_url())
                self._cache = CacheHandler(self._cache_dir, hash_file, preload_content=False)

            # Check for a 304 Not Modified Response and use cache if true
            if response.code == 304:
                # Refresh the cache as it's still fresh
                self._cache.update_cache()

                # Set response to cached response
                return self._cache.response(request.get_full_url())

            # Always cache a 301 Moved Permanently response
            elif response.code == 301:
                # Cache the response
                self._cache.cache_response(response)

            # Cache any cachable response
            elif response.code in (200, 203, 300):
                self._cache.cache_response(response)
                return self._cache.response(request.get_full_url())

        # Return Response
        return response

    # Redirect HTTPS Requests and Responses to HTTP
    https_request = http_request
    https_response = http_response


class CacheHandler(object):
    """
    Cache Handler to handle the cache thats stored on disk

    cache_dir : string or unicode --- Directory where to store the cache files
    max_age : integer --- Max age that the cache can be before it becomes stale (default 0)
    hash : string or unicode --- sha256 hash of the url of the request to be cached
    """

    def __init__(self, cache_dir, hash_file, preload_content=False):
        # Construct the full path to cache
        self._cache_path = os.path.join(cache_dir, hash_file)
        self._response = None

        # Check if there is a cache for giving url
        if not os.path.exists(self._cache_path):
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

        # Cache must exist then deserialize the cache
        elif preload_content is True:
            self.load()

    def load(self):
        """ Load the content of cache into memory """
        self._response = self.deserialize()

    def delete(self):
        """ Delete cache on disk"""
        try:
            os.remove(self._cache_path)
        except OSError:
            logger.debug("Cache Error: Unable to delete cache from disk")
        self.close()

    @property
    def response(self):
        """ Return the cache response as a urllib3 HTTPResponse """
        if "timestamp" in self._response:
            del self._response["timestamp"]
        return functools.partial(HTTPResponse, self._response["body"], self._response["headers"],
                                 self._response["status"], self._response["reason"])

    @property
    def conditional_headers(self):
        """ Return a dict of conditional headers from cache """

        # Fetch Cached headers
        headers = self._response["headers"]
        new_headers = {}

        # Check for conditional headers
        if "etag" in headers:
            new_headers["If-None-Match"] = headers["etag"]
        if "last-modified" in headers:
            new_headers["If-Modified-Since"] = headers["last-modified"]
        return new_headers

    def deserialize(self):
        """ Return a deserialize version of the cache from disk """

        try:
            # Fetch raw cache data
            with open(self._cache_path, "rb") as stream:
                raw_data = stream.read()
        except (IOError, OSError):
            self.delete()
            return None
        else:
            if not raw_data:
                self.delete()
                return None

        try:
            # Deserialize and decode the raw data
            uncompressed = zlib.decompress(raw_data)
            cached = json.loads(uncompressed)
            cached["body"] = base64.b64decode(str(cached["body"]))
            cached["headers"] = httplib.HTTPMessage(StringIO.StringIO(base64.b64decode(str(cached["headers"]))))
        except (ValueError, TypeError):
            self.delete()
            return None
        except zlib.error:
            self.delete()
            return None
        else:
            return cached

    def exists(self):
        """ Return True if cache exists else False """
        return self._response is not None

    def fresh(self, max_age):
        """ Return True if cache is fresh else False """
        if max_age == 0:
            return False
        elif max_age < 0:
            return True
        elif self._response["status"] == 301:
            return True
        elif (time.time() - self._response.get("timestamp", 0)) < max_age * 60:
            return True
        else:
            return False

    def update_cache(self, response=None):
        """
        Serialize the response and save to disk

        [response] : dict --- Dict containging server response data (default None)

        NOTE
        If no response is giving then the currently stored response is used
        """

        # Fetch response if not giving one
        if response is None:
            response = self._response.copy()

        # Set the timestamp of the response
        response["timestamp"] = time.time()

        # Serialize the response content to insure that json can do it's job
        response["body"] = base64.b64encode(response["body"])
        response["headers"] = base64.b64encode(str(response["headers"]))

        # Serialize the whole response
        try:
            json_serial = json.dumps(response, ensure_ascii=True, indent=4, separators=(",", ":"))
        except TypeError:
            logger.debug("Cache Error: Failed to serialize the response using json")
            return None

        # Compress the json Serialized response
        try:
            compressed = zlib.compress(json_serial, 1)
        except zlib.error:
            logger.debug("Cache Error: Failed to compress serialized response")
            return None

        # Save serialized response to disk
        try:
            with open(self._cache_path, "wb") as stream:
                stream.write(compressed)
        except (IOError, OSError):
            logger.debug("Cache Error: Failed to Save serialized response to disk")
            self.delete()
            return None

    def cache_response(self, response, body=None):
        """
        Create data structure and Cache the response

        response : urllib3 response object --- A urllib3 response that was returned from the server
        [body] : string --- Separated response body to use, uses body from response if body is not giving (default None)
        """
        if body is None:
            body = response.read()
        headers = response.info()

        # Remove Transfer-Encoding from header if response was a chunked response
        if "transfer-encoding" in headers:
            del headers["transfer-encoding"]

        # Create response data structure
        data = {"body": body,
                "headers": headers,
                "reason": response.msg,
                "status": response.code}

        # Update cache with response data
        self._response = data.copy()
        self.update_cache(data)

    def close(self):
        """ Reset instance variables and loaded response"""
        self._response = None


class HTTPResponse(urllib2.addinfourl):
    def __init__(self, body=None, headers=None, status=None, reason=None, url=None):
        self.msg = reason
        urllib2.addinfourl.__init__(self, StringIO.StringIO(body), headers, url, status)
