# Standard Library Imports
import io
import os
import zlib
import time
import json
import base64
import hashlib

# Requests Related Imports
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.response import HTTPResponse
from requests.packages.urllib3 import disable_warnings
from requests.structures import CaseInsensitiveDict

# Package imports
from .api import addonData, refresh, logger


def _full_cache_dir(cache_dir):
    """ Return cache directory with sub directory added """
    return os.path.join(cache_dir, u"cache")


def cache_session(cache_dir, max_age=0, max_retries=0):
    """
    Create request session with support for http caching

    cache_dir : string or unicode --- Directory where to store the cache files
    [max_age] : integer --- Max age that the cache can be before it becomes stale (default 0)
    [max_retries] : integer --- Max amount of retries before request gives up and raises an error (default 0)
    """

    # Create session object
    session = requests.session()
    disable_warnings()

    # Add max age to header
    session.headers["X-Max-Age"] = max_age

    # Create a HTTPAdapter Object to be used in requests
    cache_dir = _full_cache_dir(cache_dir)
    adapter = CacheAdapter(cache_dir, max_age, max_retries=max_retries)

    # Mount The new adapter to the current request session
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class CacheAdapter(HTTPAdapter):
    """
    Requests adapter used to intercept the request and responses from the requests module

    cache_dir : string or unicode --- Directory where to store the cache files
    max_age : integer --- Max age that the cache can be before it becomes stale
    *args, **kwargs --- Any or all keywords that are accepted by requests.adapters.HTTPAdapter
    """

    def __del__(self):
        """
        Cleanup method to remove stale caches to save on disk space
        Executes every 14 days (2 weeks)
        """

        # Fetch time of last cleanup operation
        last_time = addonData.get_setting("_lastcleanup")
        try:
            last_time = float(last_time) + 1209600  # Every 14 Days
        except ValueError:
            last_time = 0

        # Cleanup if lasttime + 28 days is still less than current time
        current_time = time.time()
        if last_time < current_time:
            logger.debug("Initiating Cache Cleanup...")

            # Loop each file within urlcache folder
            for hash_file in os.listdir(self._cache_dir):
                # Load Cache and check if stale
                cache = CacheHandler(self._cache_dir, hash_file, preload_content=True)
                if cache.exists() and cache.fresh(60 * 24 * 14) is False:
                    logger.debug("Removing cache: %s", hash_file)
                    cache.delete()

            # Save current_time of cleanup for later use
            addonData.set_setting(u"_lastcleanup", str(current_time))

    def __init__(self, cache_dir, max_age, *args, **kwargs):
        # Call Parent init method
        super(CacheAdapter, self).__init__(*args, **kwargs)

        # Set Instance Variables
        self._cache_dir = cache_dir
        self._max_age = max_age
        self._cache = None

    def send(self, request, **kwargs):
        """
        Use the request information to check if it exists in the cache
        and return cached response if so. Else forward on the said request
        """

        logger.debug("%s Requesting Url: %s", request.method, request.url)
        max_age = 0 if refresh is True else int(request.headers.pop("X-Max-Age", self._max_age))

        # Cache only handle's get requests
        if request.method == "GET":
            # Initialize Cache Handler
            hash_file = self._encode_url(request.url)
            self._cache = cache = CacheHandler(self._cache_dir, hash_file, preload_content=True)
            if cache.exists():
                if cache.fresh(max_age):
                    # Build the request response and return
                    logger.debug("Cache is fresh, using cached response")
                    return self.build_response(request, cache.response, from_cache=True)
                else:
                    # Set cache headers to allow for 304 Not Modified response
                    logger.debug("Cache is stale, setting conditional headers if any")
                    request.headers.update(cache.conditional_headers)

        # Forward on the request to be sent
        kwargs["verify"] = False
        before = time.time()
        response = super(CacheAdapter, self).send(request, **kwargs)
        logger.debug("HTTP Request took %s seconds to complete", time.time() - before)
        return response

    def build_response(self, request, response, from_cache=False):
        """ Build a requests response object """

        # Handle server responses
        if from_cache is False and request.method == "GET":
            # Create cache object if for some reason it was not already created
            if self._cache is None:
                hash_file = self._encode_url(request.url)
                self._cache = CacheHandler(self._cache_dir, hash_file, preload_content=False)

            # Check for a 304 Not Modified Response and use cache if true
            if response.status == 304:
                logger.debug("Server return 304 Not Modified response, using cached response")
                # Refresh the cache as it's still fresh
                self._cache.update_cache()

                # Read a possible response body and release the connection.
                response.read(decode_content=False)
                response.release_conn()

                # Set response to cached response
                response = self._cache.response

            # Always cache a 301 Moved Permanently response
            elif response.status == 301:
                # Cache the response
                self._cache.cache_response(response)

            # Cache any cachable response
            elif response.status in (200, 203, 300):
                # Wrap the response file with a wrapper that will cache the
                # response when the stream has been consumed.
                logger.debug("Caching request response")
                if response.chunked:
                    body = "".join([chunk for chunk in response.stream(decode_content=False)])
                else:
                    body = response.read(decode_content=False)
                self._cache.cache_response(response, body)
                response = self._cache.response

        # Return requests response object
        return super(CacheAdapter, self).build_response(request, response)

    @staticmethod
    def _encode_url(url):
        """ Return url as a sha1 encoded hash """
        if "#" in url:
            url = url[:url.find("#")]
        return hashlib.sha1(url).hexdigest()

    def close(self):
        """ Reset instance variables """
        super(CacheAdapter, self).close()
        if self._cache is not None:
            self._cache.close()
            self._cache = None


class CacheHandler(object):
    """
    Cache Handler to handle the cache thats stored on disk

    cache_dir : string or unicode --- Directory where to store the cache files
    hash : string or unicode --- sha256 hash of the url of the request to be cached
    """

    def __init__(self, cache_dir, hash_file, preload_content=True):
        # Construct the full path to cache
        logger.debug("Hash => %s", hash_file)
        self._cache_path = os.path.join(cache_dir, hash_file)
        self._response = None

        # Check if there is a cache for giving url
        if not os.path.exists(self._cache_path):
            logger.debug("Cache Not Found")
            if not os.path.exists(cache_dir):
                logger.debug("Creating Cache Directory")
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
        body = io.BytesIO(self._response.pop("body"))
        return HTTPResponse(body=body, preload_content=False, **self._response)

    @property
    def conditional_headers(self):
        """ Return a dict of conditional headers from cache """

        # Fetch Cached headers
        headers = CaseInsensitiveDict(self._response["headers"])
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
            logger.debug("Cache Error: Failed to read cache from disk")
            self.delete()
            return None
        else:
            if not raw_data:
                logger.debug("Cache Error: Cache was empty")
                self.delete()
                return None

        try:
            # Deserialize and decode the raw data
            uncompressed = zlib.decompress(raw_data)
            cached = json.loads(uncompressed)
            cached["body"] = base64.b64decode(str(cached["body"]))
            cached["headers"] = {key: unicode(base64.b64decode(str(value))) for key, value in
                                 cached["headers"].iteritems()}
        except (ValueError, TypeError):
            logger.debug("Cache Error: Failed to deserialize the contents of the cache")
            self.delete()
            return None
        except zlib.error:
            logger.debug("Cache Error: Failed to Decompress Stored Cache")
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
        response["headers"] = {key: base64.b64encode(str(value)) for key, value in response["headers"].iteritems()}

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
            body = response.read(decode_content=False)
        headers = response.headers

        # Remove Transfer-Encoding from header if response was a chunked response
        if "transfer-encoding" in headers:
            del headers["transfer-encoding"]

        # Create response data structure
        data = {"body": body,
                "headers": headers,
                "status": response.status,
                "version": response.version,
                "reason": response.reason,
                "strict": response.strict,
                "decode_content": response.decode_content}

        # Update cache with response data
        self._response = data.copy()
        self.update_cache(data)

    def close(self):
        """ Reset instance variables and loaded response"""
        self._response = None
