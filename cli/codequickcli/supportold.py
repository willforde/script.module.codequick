# Standard Library Imports
import unicodedata
import hashlib
import logging
import sys
import os
import re


data_pipe = None

# Region settings. Used by xbmc.getRegion
region_settings = {"datelong": "%A, %d %B %Y", "dateshort": "%d/%m/%Y",
                   "time": "%H:%M:%S", "meridiem": "PM", "speedunit": "km/h"}

# Dict of supported media types that kodi is able to play. Used by xbmc.getSupportedMedia
supported_media = {"video": ".m4v|.3g2|.3gp|.nsv|.tp|.ts|.ty|.strm|.pls|.rm|.rmvb|.mpd|.m3u|.m3u8|.ifo|.mov|.qt|.divx"
                            "|.xvid|.bivx|.vob|.nrg|.img|.iso|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg"
                            "|.mp4|.mkv|.mk3d|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.rar|.001|.wpl|.zip|.vdr|.dvr"
                            "-ms|.xsp|.mts|.m2t|.m2ts|.evo|.ogv|.sdp|.avs|.rec|.url|.pxml|.vc1|.h264|.rcv|.rss|.mpls"
                            "|.webm|.bdmv|.wtv|.pvr|.disc",
                   "music": ".nsv|.m4a|.flac|.aac|.strm|.pls|.rm|.rma|.mpa|.wav|.wma|.ogg|.mp3|.mp2|.m3u|.gdm|.imf"
                            "|.m15|.sfx|.uni|.ac3|.dts|.cue|.aif|.aiff|.wpl|.ape|.mac|.mpc|.mp+|.mpp|.shn|.zip|.rar"
                            "|.wv|.dsp|.xsp|.xwav|.waa|.wvs|.wam|.gcm|.idsp|.mpdsp|.mss|.spt|.rsd|.sap|.cmc|.cmr|.dmc"
                            "|.mpt|.mpd|.rmt|.tmc|.tm8|.tm2|.oga|.url|.pxml|.tta|.rss|.wtv|.mka|.tak|.opus|.dff|.dsf"
                            "|.cdda",
                   "picture": ".png|.jpg|.jpeg|.bmp|.gif|.ico|.tif|.tiff|.tga|.pcx|.cbz|.zip|.cbr|.rar|.rss|.webp"
                              "|.jp2|.apng"}

# Kodi paths mapping. Used by xbmc.translatePath
path_map = {"home": KODI_PROFILE_PATH,
            "temp": KODI_TEMP_PATH,
            "profile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "masterprofile": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "userdata": os.path.join(KODI_PROFILE_PATH, "userdata"),
            "subtitles": KODI_TEMP_PATH,
            "database": os.path.join(KODI_PROFILE_PATH, "userdata", "Database"),
            "thumbnails": os.path.join(KODI_PROFILE_PATH, "userdata", "Thumbnails"),
            "musicplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "music"),
            "videoplaylists": os.path.join(KODI_PROFILE_PATH, "userdata", "playlists", "video"),
            "recordings": KODI_TEMP_PATH,
            "screenshots": KODI_TEMP_PATH,
            "cdrips": KODI_TEMP_PATH,
            "xbmc": KODI_INSTALL_PATH,
            "logpath": os.path.join(KODI_TEMP_PATH, "kodi.log"),
            "skin": KODI_TEMP_PATH}

# Data store for addon. Use in xbmcplugin and xbmcgui
plugin_data = {"succeeded": False, "updatelisting": False, "resolved": None, "contenttype": None,  "category": None,
               "sortmethods": [], "playlist": [], "listitem": []}


def handle_prompt(prompt):
    if data_pipe:
        data_pipe.send({"prompt": prompt})
        return data_pipe.recv()
    else:
        return input(prompt)
