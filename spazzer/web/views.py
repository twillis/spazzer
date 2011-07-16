from webob import Response
from webob.exc import HTTPNotFound
from pyramid.chameleon_zpt import render_template
from urllib import quote as url_quote
from pyramid.view import view_config
import models
from ..collection import model as collections_models
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


@view_config(context=models.CollectionModel, name="search",
             renderer="templates/search.pt")
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
        criteria = None

    return {
        "artists": render_artists(artists,
                                  request,
                                  context),
        "albums": render_albums(context,
                                request,
                                albums or [],
                                show_artist=True),
        "tracks": render_tracks(tracks,
                                request,
                                show_artist=True),
        "criteria": criteria}


@view_config(context=models.SiteModel, renderer="templates/browse.pt")
def home(context, request):
    return browse(context["collection"], request)


@view_config(context=models.CollectionModel, renderer="templates/browse.pt")
def browse(context, request):
    return {"items": "",
            "title": "Browse",
            "index": FILTER_INDEX,
            "keys": keys,
            "context": context,
            "request": request}

@view_config(context=models.AdminModel, renderer="templates/manage.pt")
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


@view_config(context=models.CollectionModel, name="data")
def view_artist(context, request):
    request.url_quote = url_quote
    items = context.list_items(request)
    return Response(render_artists(items, request, context))

@view_config(context=models.CollectionModel, name="detail")
def view_albums(context, request):
    return Response(render_albums(context, request))


def compare_album_years(a, b):
    if a.year > b.year:
        return 1
    elif a.year == b.year:
        return 0
    else:
        return -1


def render_albums(context,
                  request,
                  albums=None,
                  show_artist=False,
                  artist_context=None):

    request.url_quote = quote
    if albums is None:
        key = request.params.get("artist")
        try:
            artist = context[key]
        except KeyError, key:
            raise HTTPNotFound()

        albums = artist.get_albums()
        #pull out duplicates that are due to multiple years on same album
        aidx = dict()
        for a in albums:
            if a.name.lower() not in aidx:
                aidx[a.name.lower()] = a

        albums = aidx.values()
        albums.sort(compare_album_years)
    else:
        artist = None

    return render_template("templates/detail.pt",
                           albums=albums,
                           request=request,
                           context=context,
                           artist=artist,
                           ftt=f_track_title,
                           fat=f_album_title(show_artist),
                           artist_context=artist)


@view_config(context=models.DownloadModel)
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
    response = Response(content_type="binary/octet-stream")
    response.headers.add("Content-Disposition",
                         "attachment; filename=%s; size=%d" % (
            filename, filesize))

    response.body = filebuf.read()
    return response


def render_artists(items, request, context):
    request.url_quote = quote
    return render_template("templates/artist.pt",
                           items=items,
                           request=request, context=context)


def render_tracks(items, request, show_artist=False):
    """
    render functions assemble pieces from the context
    """
    request.url_quote = quote

    return render_template("templates/tracks.pt",
                           tracks=items,
                           request=request,
                           ftt=f_track_title(show_artist))


def f_album_title(show_artist=True):
    _show = show_artist

    def _x(album):
        if _show:
            return "%s - %s by %s" % (album.name or "(Unknown)",
                                      album.year or "(Unknown)",
                                      album.artist)
        else:
            return "%s - %s" % (album.name or "(Unknown)",
                                      album.year or "(Unknown)")

    return _x


def f_track_title(show_artist=False):
    _show = show_artist

    def _x(track):
        track_title = track.title or u'(Unknown)'
        if _show:
            return u"%s by %s" % (track_title,
                                  track.artist or u'(Unknown)')
        else:
            return track_title
    return _x
