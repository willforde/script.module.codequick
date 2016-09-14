# Standard Library Imports
import hashlib
import httplib
import base64
import time
import json
import zlib
import os
import io

# Package imports
from .support import get_info, get_setting, set_setting, logger, args

# Set user agent that will be used
USERAGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
DEFAULTAGE = 3600


class CaseInsensitiveDict(dict):
    """ A Case Insensitive dict"""
    def __init__(self, headers):
        super(CaseInsensitiveDict, self).__init__()
        for key, value in headers.iteritems():
            self[key.lower()] = value

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())

    def __delitem__(self, key):
        super(CaseInsensitiveDict, self).__delitem__(key.lower())

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(key.lower())


def session_common(session_cls):
    def decorator(func):
        def wrapper(max_age=None, disable_cache=False):
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
            _session = session_cls()

            # Add some extra headers
            _session.headers["Accept-language"] = "en-gb,en-us,en"
            _session.headers["User-agent"] = USERAGENT

            # Create a HTTPAdapter to be used in requests
            if disable_cache is False and get_setting("disable-cache") is False:
                # Add max age custom header
                if u"refresh" in args:
                    _session.headers["X-max-age"] = "0"
                elif max_age is None:
                    _session.headers["X-max-age"] = str(DEFAULTAGE)
                else:
                    _session.headers["X-max-age"] = str(max_age)

                # Create Adapter
                func(_session)

            # Return the session object
            return _session
        return wrapper
    return decorator


class CacheAdapterCommon(object):
    # Class vars
    __cache_dir = None
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
            for url_hash in os.listdir(self.cache_dir):
                cache = CacheHandler(self.cache_dir, url_hash, 60 * 24 * 14)
                if cache.file_fresh() is False:
                    cache.delete()

            # Save current_time of cleanup for later use
            set_setting("_next_cleanup", unicode(current_time + 1209600))

    def check_cache(self, request):
        """ Check if the cache contents is fresh and return the cache if so """

        # Local vars
        method = self.get_method(request)
        url = self.get_url(request)

        # Reset cache variable for the next request to start a fresh
        if self.__cache:
            self.__cache.close()
            self.__cache = None

        logger.debug("%s Requesting Url: %s", method, url)
        # Check cache only for get requests
        if method == "GET":
            # Fetch max age from request header
            max_age = int(request.headers.pop("X-max-age", DEFAULTAGE))

            # Fetch the cache if it exists
            self.__cache = cache = self.get_cache(url, max_age)

            # Check if cache exists first
            if cache.exists():
                # Now check if that cache is fresh
                if cache.fresh():
                    # Sense cache is fresh we can build a cached response and return it
                    logger.debug("Cache is fresh, using cached response")
                    return self.prepare_cached_response(cache.response, request, from_cache=True)
                else:
                    # Set cache headers to allow for 304 Not Modified response
                    logger.debug("Cache is stale, checking for conditional headers")
                    headers = cache.conditional_headers
                    if headers:
                        request.headers.update(headers)

    def handle_response(self, request, response, from_cache=False):
        """ Cache the response and return cached response """
        if from_cache is False and self.__cache and self.get_method(request) == "GET":
            status = self.get_status(response)
            cache = self.__cache

            # Update cache timestamp if server returns a 304 Not Modified Response
            if status == 304:
                cache.reset_timestamp()
                logger.debug("Server return 304 Not Modified response, using cached response")
                response = self.handle_304(cache, request, response)

            # Cache any cachable response
            elif status in (200, 203, 300, 301):
                if status == 301:
                    logger.debug("Caching 301 Moved Permanently response")
                else:
                    logger.debug("Caching request response")

                # Save response to cache and return it as a cached response
                self.update_cache(cache, response)
                response = self.prepare_cached_response(cache.response, request)

        # Return unmodified response
        return response

    def get_cache(self, url, max_age=None):
        """ Initialize cache handler and return it """
        url_hash = self.encode_url(url)
        return CacheHandler(self.cache_dir, url_hash, max_age)

    @staticmethod
    def encode_url(url):
        """ Return url as a sha1 encoded hash """
        if "#" in url:
            url = url[:url.find("#")]
        return hashlib.sha1(url).hexdigest()

    @property
    def cache_dir(self):
        """ Return cache directory and create if missing """
        if self.__cache_dir is not None:
            return self.__cache_dir
        else:
            self.__cache_dir = cache_dir = os.path.join(get_info("profile"), self.cache_dir_name)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            return cache_dir


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

    def __init__(self, cache_dir, url_hash, max_age=None):
        logger.debug("SHA1 Hash => %s", url_hash)
        if max_age is None:
            max_age = DEFAULTAGE

        self.cache_path = os.path.join(cache_dir, url_hash)
        self.__exists = os.path.exists(self.cache_path)
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
        logger.debug("Removing cache: %s", url_hash)
        self.close()
        try:
            os.remove(self.cache_path)
        except OSError:
            logger.debug("Cache Error: Unable to delete cache from disk")

    def close(self):
        """ Reset instance variables and loaded response"""
        self.__timestamp = None
        self.__response = None
        self.__exists = False

    def reset_timestamp(self):
        """ Reset the last modified timestamp """
        os.utime(self.cache_path, None)
        self.__timestamp = time.time()

    @property
    def timestamp(self):
        """ Return the last modified timestamp of the cache file """
        if self.__timestamp is not None:
            return self.__timestamp
        else:
            self.__timestamp = timestamp = os.stat(self.cache_path).st_mtime
            return timestamp

    @property
    def response(self):
        """ Return the cache response that is stored on disk """
        if self.__response is not None:
            return self.__response
        else:
            # Skip if cache dont actually exists
            if not self.__exists:
                return None

            try:
                # Atempt to read in a raw cache data
                with open(self.cache_path, "rb") as stream:
                    raw_data = stream.read()
                    if not raw_data:
                        raise IOError("Content of %s is empty", self.cache_path)

            except (IOError, OSError) as e:
                logger.debug("Cache read failed: %s", str(e))
                self.delete()
                return None

            try:
                # Deserialize and decode the raw data
                uncompressed = zlib.decompress(raw_data)
                cached = json.loads(uncompressed)
                cached["body"] = base64.b64decode(str(cached["body"]))
                cached["headers"] = CaseInsensitiveDict(cached["headers"])

            except zlib.error as e:
                logger.debug("Cache decompress failed: %s", str(e))
                self.delete()
                return None

            except (ValueError, TypeError) as e:
                logger.debug("Cache deserialize failed: %s", str(e))
                self.delete()
                return None

            # If we can get this far that every thing must be good
            self.__response = cached
            return cached

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

    def update(self, body, headers, status, reason, version=None, strict=None):
        # Convert headers into a case insensitive dict
        headers = CaseInsensitiveDict(headers)

        # Remove Transfer-Encoding from header if response was a chunked response
        if "Transfer-encoding" in headers:
            del headers["Transfer-encoding"]

        # Remove Content encoding header as the content will be decoded if it was encoded
        if "Content-encoding" in headers:
            del headers["Content-encoding"]

        # Create response data structure
        response = {"body": body,
                    "headers": headers,
                    "status": status,
                    "version": version,
                    "reason": reason,
                    "strict": strict}

        # Update the cache response data store
        self.__response = response.copy()

        # Serialize the response content to insure that json can do it's job
        response["body"] = base64.b64encode(response["body"])

        # Serialize the whole response
        try:
            json_serial = json.dumps(response, ensure_ascii=True)
        except TypeError:
            logger.debug("Cache Error: Failed to serialize the response using json")
            raise

        # Compress the json Serialized response
        try:
            compressed = zlib.compress(json_serial, 1)
        except zlib.error:
            logger.debug("Cache Error: Failed to compress serialized response")
            raise

        # Save serialized response to disk
        try:
            with open(self.cache_path, "wb") as stream:
                stream.write(compressed)
        except (IOError, OSError):
            logger.debug("Cache Error: Failed to Save serialized response to disk")
            self.delete()
            raise
        else:
            self.__exists = True
