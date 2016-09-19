# Standard Library Imports
import base64
import hashlib
import zlib
import time
import json
import io
import os

# Package imports
from .support import get_info, get_setting, set_setting, logger, args

# Request packages imports
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.response import HTTPResponse

# Disable requests ssl warnings
disable_warnings()

# Set user agent that will be used
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
DEFAULTAGE = 3600

# Set the cache directory and create it if missing
CACHE_DIR = os.path.join(get_info("profile"), u"cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


class CaseInsensitiveDict(dict):
    """ A Case Insensitive dict"""
    def __init__(self, headers):
        super(CaseInsensitiveDict, self).__init__(headers)
        self.lowerkeymap = {key.lower(): key for key in headers.keys()}

    def __getitem__(self, key):
        key = self.lowerkeymap[key.lower()]
        return super(CaseInsensitiveDict, self).__getitem__(key)

    def __setitem__(self, key, value):
        self.lowerkeymap[key.lower()] = value
        super(CaseInsensitiveDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        key = self.lowerkeymap[key.lower()]
        super(CaseInsensitiveDict, self).__delitem__(key)

    def __contains__(self, key):
        return key.lower() in self.lowerkeymap


def session(max_age=None, disable_cache=False):
    """
    Create request session with support for http caching

    Parameters
    ----------
    max_age : int, optional(default=3600)
        Max age that the cache can be before it becomes stale.

    disable_cache : bool, optional(default=False)
        If true the cache system will be bypassed (disabled).
    """

    # Create session object
    _session = requests.session()

    # Add some extra headers
    _session.headers["Accept-language"] = "en-gb,en-us,en"
    _session.headers["User-agent"] = USERAGENT

    # Create a HTTPAdapter to be used in requests
    if disable_cache is False and get_setting("disable-cache") is False:
        # Add max age custom header
        if u"refresh" in args:
            _session.headers["x-max-age"] = "0"
        elif max_age is None:
            _session.headers["x-max-age"] = str(DEFAULTAGE)
        else:
            _session.headers["x-max-age"] = str(max_age)

        # Create Adapter
        adapter = CacheAdapter()
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)

    # Return the session object
    return _session


class CacheAdapter(HTTPAdapter):
    __cache = None

    def __del__(self):
        """
        Cleanup method to remove stale caches to save on disk space
        Executes every 14 days (2 weeks)
        """

        # Fetch time of last cleanup operation
        next_time = get_setting("_next_cleanup")
        try:
            next_time = float(next_time)
        except ValueError:
            next_time = 0

        # Cleanup if lasttime + 28 days is still less than current time
        current_time = time.time()
        if next_time < current_time:
            logger.debug("Initiating Cache Cleanup...")

            # Loop each file within cache directory
            for url_hash in os.listdir(CACHE_DIR):
                cache = CacheHandler(url_hash, 60 * 24 * 14)
                if cache.file_fresh() is False:
                    cache.delete()

            # Save current_time of cleanup for later use
            set_setting("_next_cleanup", unicode(current_time + 1209600))

    def send(self, request, **kwargs):
        """
        Use the request information to check if it exists in the cache
        and return cached response if so. Else forward on the said request
        """

        # Local vars
        method = request.method
        url = request.url

        # Reset cache variable for the next request to start a fresh
        if self.__cache:
            self.__cache.close()
            self.__cache = None

        logger.debug("%s Requesting Url: %s", method, url)
        # Check cache only for get requests
        if method == "GET":
            # Fetch max age from request header
            max_age = int(request.headers.pop("x-max-age", DEFAULTAGE))

            # Fetch the cache if it exists
            url_hash = self.encode_url(url)
            self.__cache = cache = CacheHandler(url_hash, max_age)

            # Check if cache exists first
            if cache.exists():
                # Now check if that cache is fresh
                if cache.fresh():
                    # Sense cache is fresh we can build a cached response and return it
                    logger.debug("Cache is fresh, returning cached response")
                    cached_response = self.prepare_cached_response(cache.response)
                    return self.build_response(request, cached_response, from_cache=True)
                else:
                    # Set cache headers to allow for 304 Not Modified response
                    logger.debug("Cache is stale, checking for conditional headers")
                    headers = cache.conditional_headers
                    if headers:
                        request.headers.update(headers)

        # Forward the request on to the server
        kwargs["verify"] = False
        return super(CacheAdapter, self).send(request, **kwargs)

    def build_response(self, request, response, from_cache=False):
        """ Cache the response and return cached response """
        if from_cache is False and self.__cache and request.method == "GET":
            status = response.status
            cache = self.__cache

            # Update cache timestamp if server returns a 304 Not Modified Response
            if status == 304:
                cache.reset_timestamp()
                logger.debug("Server return 304 Not Modified response, using cached response")

                # Read a possible response body and release the connection.
                response.read(decode_content=False)
                response.release_conn()

                # Set response to cached response
                response = self.prepare_cached_response(cache.response)

            # Cache any cachable response
            elif status in (200, 203, 300, 301):
                if status == 301:
                    logger.debug("Caching 301 Moved Permanently response")
                else:
                    logger.debug("Caching request response")

                # Save response to cache and return it as a cached response
                self.update_cache(cache, response)
                response = self.prepare_cached_response(cache.response)

        # Return response
        return super(CacheAdapter, self).build_response(request, response)

    @staticmethod
    def encode_url(url):
        """ Return url as a sha1 encoded hash """
        if "#" in url:
            url = url[:url.find("#")]
        return hashlib.sha1(url).hexdigest()

    @staticmethod
    def prepare_cached_response(response):
        """ Prepare the cached response so that requests can handle it """
        body = io.BytesIO(response.pop("body"))
        return HTTPResponse(body=body, preload_content=False, **response)

    @staticmethod
    def update_cache(cache, response):
        """ Update the cache with the new server response """

        # Fetch the body of the response
        if response.chunked:
            body = "".join([chunk for chunk in response.stream(decode_content=False)])
        else:
            body = response.read(decode_content=False)

        # Now update the cache with the appropriate data
        cache.update(body=body, headers=response.headers, status=response.status,
                     reason=response.reason, version=response.version,
                     strict=response.strict)


class CacheHandler(object):
    """
    Cache Handler to manage the on disk cache

    Parameters
    ----------
    url_hash : str
        SHA1 hash of the url from the request to be cached.

    max_age : int, optional(default=3600)
        Max age that the cache can be before it becomes stale.
    """

    def __init__(self, url_hash, max_age=None):
        logger.debug("SHA1 Hash => %s", url_hash)
        if max_age is None:
            max_age = DEFAULTAGE

        self.cache_file = os.path.join(CACHE_DIR, url_hash)
        self.__exists = os.path.exists(self.cache_file)
        self.__timestamp = None
        self.__response = None
        self.max_age = max_age

    def exists(self):
        """ Return True if cache exists else False """
        return self.__exists and self.response is not None

    def fresh(self):
        """ Return True if cache is fresh else False """
        response = self.response

        # Check that the cache response exists first
        if response is None:
            return False

        # Check that the response is of status 301 or that the cache is not older than the max age
        elif response.get("status") == 301 or self.max_age == -1 or self.file_fresh():
            return True

        # Just return false to indecate that the cache is not fresh
        else:
            return False

    def file_fresh(self):
        return (time.time() - self.timestamp) < self.max_age

    def delete(self):
        """ Delete cache from disk"""
        self.close()
        try:
            logger.debug("Removing cache: %s", self.cache_file)
            os.remove(self.cache_file)
        except OSError:
            logger.debug("Cache Error: Unable to delete cache from disk")

    def close(self):
        """ Reset instance variables and loaded response"""
        self.__timestamp = None
        self.__response = None
        self.__exists = False

    def reset_timestamp(self):
        """ Reset the last modified timestamp """
        os.utime(self.cache_file, None)
        self.__timestamp = time.time()

    @property
    def timestamp(self):
        """ Return the last modified timestamp of the cache file """
        if self.__timestamp is not None:
            return self.__timestamp
        else:
            self.__timestamp = timestamp = os.stat(self.cache_file).st_mtime
            return timestamp

    @property
    def conditional_headers(self):
        """ Return a dict of conditional headers from cache """

        # Fetch Cached headers
        response = self.response
        if not response:
            return None

        # Fetch response headers
        headers = response["headers"]
        new_headers = {}

        # Check for conditional headers
        if "Etag" in headers:
            logger.debug("Found conditional header: ETag = %s", headers["ETag"])
            new_headers["If-None-Match"] = headers["ETag"]

        if "Last-modified" in headers:
            logger.debug("Found conditional header: Last-Modified = %s", headers["Last-modified"])
            new_headers["If-Modified-Since"] = headers["Last-Modified"]

        # Return the conditional headers if any
        if new_headers:
            return new_headers

    @property
    def response(self):
        """ Return the cache response that is stored on disk """
        if self.__response is not None:
            return self.__response

        # Skip if cache dont actually exists
        if not self.__exists:
            return None

        try:
            # Atempt to read in a raw cache data
            with open(self.cache_file, "rb") as stream:
                json_data = json.load(stream)

            # Convert content body form ascii to binary
            json_data["body"] = base64.b64decode(str(json_data["body"]))

        except (IOError, OSError) as e:
            logger.debug("Cache Error: Failed to read cached response, %s", str(e))
            self.delete()
            return None

        except (ValueError, TypeError) as e:
            logger.debug("Cache Error: Failed to deserialize content body, %s", str(e))
            self.delete()
            return None

        except zlib.error as e:
            logger.debug("Cache Error: Failed to decompress content body, %s", str(e))
            self.delete()
            return None

        else:
            # Convert header dict into a case insensitive dict
            json_data["headers"] = CaseInsensitiveDict(json_data["headers"])

        # If we can get this far that every thing must be good
        self.__response = json_data
        return json_data

    def update(self, body, headers, status, reason, version, strict):
        # Convert headers into a Case Insensitive Dict
        headers = CaseInsensitiveDict(headers)

        # Remove Transfer-Encoding from header if exists
        if "Transfer-Encoding" in headers:
            logger.debug("Removing header: Transfer-Encoding = %s", headers["Transfer-encoding"])
            del headers["Transfer-encoding"]

        # Create response data structure
        response = {"body": body,
                    "headers": headers,
                    "status": status,
                    "version": version,
                    "reason": reason,
                    "strict": strict}

        # Update the cache response data store
        self.__response = response.copy()

        try:
            # Compress content body is not already compressed
            if "Content-Encoding" not in headers:
                body = zlib.compress(body, 1)
                headers["Content-Encoding"] = "deflate"

            # Convert compressed binary data to ascii
            response["body"] = base64.b64encode(body)

            # Save the response to disk using json Serialization
            with open(self.cache_file, "wb") as stream:
                json.dump(response, stream, indent=4, separators=(",", ":"))

        except zlib.error:
            logger.debug("Cache Error: Failed to compress content body")
            self.delete()
            raise

        except (ValueError, TypeError):
            logger.debug("Cache Error: Failed to base64 encode the content body, %s")
            self.delete()
            raise

        except (IOError, OSError):
            logger.debug("Cache Error: Failed to Save json serialized response to disk")
            self.delete()
            raise

        else:
            self.__exists = True
