"""
views for application
"""
from webob import Response
from webob.exc import HTTPNotFound
from urllib import quote as url_quote
from pyramid.view import view_config
from pyramid.compat import json
import models
import mimetypes

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

def get_search_results(context, request):
    request.url_quote = quote
    criteria = request.params.get("criteria")
    if criteria:
        artists = context.search_artists(criteria)
        albums = context.search_albums(criteria)
        tracks = context.search_tracks(criteria)
        return dict(artists=artists, albums=albums, tracks=tracks, criteria=criteria)
    else:
        return dict(artists=[], albums=[], tracks=[], criteria=criteria)
@view_config(context=models.CollectionModel, name="search",
             renderer="search.mako", route_name="api")
def search(context, request):
    sr = get_search_results(context, request)
    artists, albums, tracks, criteria = sr["artists"], sr["albums"], sr["tracks"], sr["criteria"]
    return dict(results=json.dumps({
        "artists": render_artists(artists,
                                  request,
                                  context),
        "albums": render_albums(context,
                                request,
                                albums or [],
                                show_artist=True)["items"],
        "tracks": render_tracks(tracks,
                                request,
                                show_artist=True),
        "criteria": criteria}), criteria=criteria)


@view_config(context=models.CollectionModel, name="search_json",
             renderer="json", route_name="api")
def search_json(context, request):
    sr = get_search_results(context, request)
    artists, albums, tracks, criteria = sr["artists"], sr["albums"], sr["tracks"], sr["criteria"]
    return {
        "artists": render_artists(artists,
                                  request,
                                  context),
        "albums": render_albums(context,
                                request,
                                albums or [],
                                show_artist=True)["items"],
        "tracks": render_tracks(tracks,
                                request,
                                show_artist=True),
        "criteria": criteria}

@view_config(context=models.SiteModel, renderer="browse.mako", route_name="api")
def home(context, request):
    return browse(context["collection"], request)


@view_config(context=models.CollectionModel, renderer="browse.mako", route_name="api")
def browse(context, request):
    return {"items": "",
            "title": "Browse",
            "index": FILTER_INDEX,
            "keys": keys,
            "get_url": context.get_url}


@view_config(context=models.AdminModel, renderer="manage.mako", route_name="api")
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


@view_config(context=models.CollectionModel, name="data", renderer="json", route_name="api")
def view_artist(context, request):
    request.url_quote = quote
    items = context.list_items(request)
    return dict(items=render_artists(items, request, context))


@view_config(context=models.CollectionModel, name="detail", renderer="json", route_name="api")
def view_albums(context, request):
    return render_albums(context, request)


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

    fat = f_album_title(show_artist)
    ftt = f_track_title

    result = dict(items=[], artist_context=artist.name if artist else "")
    for album in albums:
        item = dict(title=fat(album),
                    name=album.name,
                    year=album.year,
                    download_url="%s/api/download/?artist=%s&;album=%s" % \
                        (request.application_url,
                         quote(artist.name if artist else ""),
                         quote(album.name)),
                    tracks=[]
                        )
        for track in album.get_tracks():
            item["tracks"].append(track_to_track_view(track, request, ftt))
        result["items"].append(item)

    return result


def track_to_track_view(track, request, ftt):
    compilation = track.on_compilation()
    return dict(on_compilation=compilation,
                                      download_url="%s/api/download/?track=%s" % \
                                      (request.application_url,
                                       str(track.id)),
                                      track=track.track,
                                      name=track.title,
                                      title=ftt(compilation)(track),
                                      year=track.year,
                                      artist=track.artist,
                                      album=track.album)


@view_config(context=models.DownloadModel, route_name="api")
def serve(context, request):
    """
    get's the file data from the context and dispatches off
    to the request builder
    """
    result = context.get_file(request)
    if result:
        buf, length, fname = result
        return _serve(buf, length, fname)
    else:
        return HTTPNotFound()


def _serve(filebuf, filename, filesize):
    """
    request builder for serving files
    """
    response = Response(conditional_response=True,
                        content_type=mimetypes.guess_type(filename)[0] \
                        or "binary/octet-stream")
    response.headers.add("Content-Disposition",
                         "attachment; filename=%s; size=%d" % (
            filename, filesize))
    response.app_iter = filebuf
    return response


def render_artists(items, request, context):
    base_url = context.get_url(request)
    item_views = [dict(name=unicode(item),
                       detail_url="%sdetail?artist=%s" \
                       % (base_url, quote(item.name))) \
                  for item in items]
    return item_views


def render_tracks(items, request, show_artist=False):
    """
    render functions assemble pieces from the context
    """
    ftt = f_track_title
    return [track_to_track_view(item, request, ftt) \
                        for item in items]


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
        try:
            track_title = track.title or u'(Unknown)'
        except:
            print track
            raise
        
        if _show:
            return u"%s by %s" % (track_title,
                                  track.artist or u'(Unknown)')
        else:
            return track_title
    return _x
