from webob import Response
from webob.exc import HTTPNotFound
from repoze.bfg.chameleon_zpt import render_template
from urllib import quote as url_quote


def quote(s):
    return url_quote(s.encode("utf-8"))

ALPHABET_SEQ = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                 "K", "L", "M", "N", "O", "P", "Q", "U", "R", "S",
                 "T", "U", "V", "W", "X", "Y", "Z")
idx = [(c, "data/?start=%s" % c) for c in ALPHABET_SEQ]
FILTER_INDEX = {}

EXTRA_INDEX = {"[ALL]": "data/?start=",
                "[#]": "data/?start=__num__"}
FILTER_INDEX.update(idx)
keys = FILTER_INDEX.keys()
keys.sort()
FILTER_INDEX.update(EXTRA_INDEX)
FILTER_INDEX.update(idx)

keys.reverse()
keys.append("[ALL]")
keys.reverse()
keys.append("[#]")


def search(context, request):
    request.url_quote = url_quote
    if "POST" in request.params:
        criteria = request.POST.get("criteria")
        artists = context.search_artists(criteria)
        albums = context.search_albums(criteria)
        tracks = context.search_tracks(criteria)
    else:
        artists = []
        albums = []
        tracks = []

    return {
        "artists": render_artists(artists, request, context),
        "albums": render_albums(context, request, albums or []),
        "tracks": render_tracks(tracks, request, show_artist = True)}


def browse(context, request):
    return {"items": "", "title": "list", "index": FILTER_INDEX, "keys": keys}


def view_manage(context, request):
    if "POST" in request.params:
        if "DELETE" in request.params:
            context.remove_mount(request.POST.get("mount"))
            msg = None
        elif "SCAN" in request.params:
            result, msg = context.start_scan()
        else:
            result, msg = context.add_mount(request.POST.get("mount"))
    else:
        msg = None

    mounts = context.get_mounts()
    return {"mounts": mounts, "message": msg}


def view_artist(context, request):
    request.url_quote = url_quote
    items = context.list_items(request)
    return Response(render_artists(items, request, context))


def view_albums(context, request):
    return Response(render_albums(context, request))


def render_albums(context, request, albums = None):
    request.url_quote = quote
    if albums is None:
        key = request.params.get("artist")
        try:
            artist = context[key]
        except KeyError, key:
            raise HTTPNotFound()
        albums = artist.get_albums()
    else:
        artist = None

    return render_template("templates/detail.pt",
                           albums = albums,
                           request = request,
                           context = context,
                           artist = artist,
                           ftt = f_track_title)


def serve(context, request):
    """
    get's the file data from the context and dispatches off
    to the request builder
    """
    result = context.get_file(request)
    if result:
        buf, length, fname = result
        try:
            return _serve(buf, length, fname)
        finally:
            buf.close()
    else:
        return HTTPNotFound()


def _serve(filebuf, filename, filesize):
    """
    request builder for serving files
    """
    response = Response(content_type ="binary/octet-stream")
    response.headers.add("Content-Disposition",
                         "attachment; filename=%s; size=%d" % (
            filename, filesize))

    response.body = filebuf.read()
    return response


def render_artists(items, request, context):
    request.url_quote = quote
    return render_template("templates/artist.pt",
                           items = items,
                           request = request, context = context)


def render_tracks(items, request, show_artist = False):
    """
    render functions assemble pieces from the context
    """
    request.url_quote = quote

    return render_template("templates/tracks.pt",
                           tracks = items,
                           request = request,
                           ftt = f_track_title(show_artist))


def f_track_title(show_artist = False):
    _show = show_artist

    def _x(track):
        track_title = track.title or u'(Unknown)'
        if _show:
            if track.artist:
                return u"%s by %s" % (track_title,
                                      track.artist or u'(Unknown)')
            else:
                return u"%s by %s" % (track_title, u'(Unknown)')
        else:
            return track_title

    return _x
