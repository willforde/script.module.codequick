########
Tutorial
########
Here we will document the creation of an "add-on".
In this instance, “plugin.video.metalvideo”. This will be a simplified version of the full add-on
that can be found over at https://github.com/willforde/plugin.video.metalvideo

First of all, import the required “Codequick” components.

    * :class:`Route<codequick.route.Route>` will be used to list folder"items.
    * :class:`Resolver<codequick.resolver.Resolver>` will be used to resolve video URLs.
    * :class:`Listitem<codequick.listing.Listitem>` is used to create "items" within Kodi.
    * :mod:`utils<codequick.utils>` is a module, containing some useful functions.
    * :func:`run<codequick.run>` is the function that controls the execution of the add-on.

.. code-block:: python

    from codequick import Route, Resolver, Listitem, utils, run


Next we will import "urlquick", which is a "light-weight" HTTP client with a "requests" like interface,
featuring caching support.

.. code-block:: python

    import urlquick

Now, we will use :func:`utils.urljoin_partial<codequick.utils.urljoin_partial>` to create a URL constructor
with the "base" URL of the site. This is use to convert relative URLs to absolute URLs.
Normally HTML is full of relative URLs and this makes it easier to work with them,
guaranteeing that you will always have an absolute URL to use.

.. code-block:: python

    # Base url constructor
    url_constructor = utils.urljoin_partial("http://metalvideo.com")

Next we will create the "Root" function which will be the starting point for the add-on.
It is very important that the "Root" function is called "root". This function will first have to be registered
as a "callback" function. Since this is a function that will return "listitems", this will be registered as a
:class:`Route<codequick.route.Route>` callback. It is expected that a :class:`Route<codequick.route.Route>`
callback should return a "generator" or "list", of :class:`codequick.Listitem<codequick.listing.Listitem>` objects.
The first argument that will be passed to a :class:`Route<codequick.route.Route>` callback, will always be the
:class:`Route<codequick.route.Route>` instance.

This "callback" will parse the list of the “Music Video Categories” available on: http://metalvideo.com,
This will return a "generator" of "listitems" linking to a sub-directory of videos within that category.
Parsing of the HTML source will be done using "HTMLement" which is integrated into the "urlquick" request response.


.. seealso:: http://urlquick.readthedocs.io/en/stable/#urlquick.Response.parse

             http://python-htmlement.readthedocs.io/en/stable/

.. code-block:: python

    @Route.register
    def root(plugin):
        # Request the online resource
        url = url_constructor("/mobile/category.html")
        resp = urlquick.get(url, headers={"Cookie": "COOKIE_DEVICE=mobile"})

        # Filter source down to required section by giving the name and
        # attributes of the element containing the required data.
        # It's a lot faster, to limit the parser to required section.
        root_elem = resp.parse(u"ul", attrs={"id": "category_listing"})

        # Parse each category
        for elem in root_elem.iterfind("li"):
            item = Listitem()

            # Find the 'a' element containing the label & url info
            a_tag = elem.find("a")

            # Find the video count 'span' tag
            vidcount = elem.find("span").text

            # Set label with video count added.
            item.label = "%s (%s)" % (a_tag.text, vidcount)

            # This will set the callback that will be called when listitem is activated.
            # 'video_list' is the route callback function that we will create later.
            # The 'url' argument is the url of the category that will be passed
            # to the 'video_list' callback.
            item.set_callback(video_list, url=a_tag.get("href"))

            # Return the listitem as a generator.
            yield item

Now, we can create the "video parser" callback that will return "playable" listitems. Since this is another
function that will return listitems, it will be registered as a :class:`Route<codequick.route.Route>` callback.

.. code-block:: python

    @Route.register
    def video_list(plugin, url):
        # Request the online resource.
        url = url_constructor(url)
        resp = urlquick.get(url)
        root_elem = resp.parse("div", attrs={"id": "browse_main"})

        # Parse each video
        for elem in root_elem.iterfind(u".//div[@class='video_i']"):
            item = Listitem()

            # Set the thumbnail image of the video.
            item.art["thumb"] = elem.find(".//img").get("src")

            # Extract url from first 'a' element and remove it from source tree.
            # This makes it easier to extract 'artist' and 'song' names later.
            a_tag = elem.find("a")
            url = a_tag.get("href")
            elem.remove(a_tag)

            # Set title as 'artist - song'.
            span_tags = tuple(node.text for node in elem.findall(".//span"))
            item.label = "%s - %s" % span_tags
            item.info["artist"] = [span_tags[0]]

            # 'play_video' is the resolver callback function that we will create later.
            # The 'url' argument is the url of the video that will be passed
            # to the 'play_video' resolver callback.
            item.set_callback(play_video, url=url)

            # Return the listitem as a generator.
            yield item

        # Extract the next page url if one exists.
        next_tag = root_elem.findall(".//div[@class='pagination']/a")
        if next_tag and next_tag[-1].text.startswith("next"):
            # This will return a listitem, that will link back to this
            # callback function with the url of the next page of content.
            yield Listitem.next_page(url=next_tag[-1].get("href"))

Finally we need to create the :class:`Resolver<codequick.resolver.Resolver>` "callback", and register it as so.
This callback is expected to return a playable video URL. The first argument that will be passed to a
:class:`Resolver<codequick.resolver.Resolver>` callback, will always be a
:class:`Resolver<codequick.resolver.Resolver>` instance.

.. code-block:: python

    @Resolver.register
    def play_video(plugin, url):
        # Sence http://metalvideo.com uses enbeaded youtube videos,
        # we can use 'plugin.extract_source' to extract the video url.
        url = url_constructor(url)
        return plugin.extract_source(url)

:func:`plugin.extract_source<codequick.resolver.Resolver.extract_source>` uses "YouTube.DL" to extract the
video URL. Since it uses YouTube.DL, it will work with way-more than just youtube.

.. seealso:: https://rg3.github.io/youtube-dl/supportedsites.html

So to finish, we need to initiate the "codequick" startup process.
This will call the "callback functions" automatically for you.

.. code-block:: python

    if __name__ == "__main__":
        run()
