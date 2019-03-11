"""
mode 0 = single url
mode 1 = multiple urls
mode 2 = no video
mode 3 = raises error
mode 4 = warning message
"""
import time
mode = 0
callback_errors = object


class VideoInfo(object):
    def __int__(self):
        self.title = ''
        self.description = ''
        self.thumbnail = ''
        self.webpage = ''
        self._streams = None
        self.sourceName = ''
        self.info = None
        self._selection = None
        self.downloadID = str(time.time())

    def hasMultipleStreams(self):
        return mode == 1

    def streamURL(self):
        return "video.mkv"

    def streams(self):
        class Extractor(object):
            def title(self):
                return "Youtube"

        return [{"ytdl_format": {"extractor": Extractor()}, "title": "Video title"}]

    def selectStream(self, idx):
        pass

    def __nonzero__(self):  # py2
        return mode != 2

    def __bool__(self):  # py3
        return mode != 2


def getVideoInfo(url, quality=None, resolve_redirects=False):
    if mode == 3:
        callback_errors("ERROR: I was told to raise an error")
    else:
        if mode == 4:
            callback_errors("WARNING: I was told to raise a warning message")
        return VideoInfo()


def setOutputCallback(callback):
    global callback_errors
    callback_errors = callback


def overrideParam(key, val):
    pass
