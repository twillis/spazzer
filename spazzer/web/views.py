from webob import Response
from webob.exc import HTTPNotFound
from repoze.bfg.chameleon_zpt import render_template_to_response as render, render_template
import os
from urllib import quote as url_quote

def quote(s):
    return url_quote(s.encode("utf-8"))

ALPHABET_SEQ = ( "A","B","C","D","E","F","G","H","I","J",
                 "K","L","M","N","O","P","Q","U","R","S",
                 "T","U","V","W","X","Y","Z")
idx = [(c, "data/?start=%s" % c) for c in ALPHABET_SEQ]
FILTER_INDEX = {}

EXTRA_INDEX = {"[ALL]":"data/?start=",
                "[#]":"data/?start=__num__",
               "Search":"#search",
               }
FILTER_INDEX.update(idx)
keys = FILTER_INDEX.keys()
keys.sort()
FILTER_INDEX.update(EXTRA_INDEX)
FILTER_INDEX.update(idx)

keys.reverse()
keys.append("[ALL]")
keys.reverse()
keys.append("[#]")
keys.append("Search")
def my_view(request):
    return {'project':'spazzer'}


def echo(context,request):
    result = """
<h1>Context</h1>
%s

<h1>Request</h1>
%s
""" % ("%s: %s" % (context.__class__.__name__, context), request.environ)
    return Response(result)

def search(context,request):
    request.url_quote = url_quote
    if "POST" in request.params:
        criteria = request.POST.get("criteria")
        artists = context.search_artists(criteria)
        albums = context.search_albums(criteria)
        tracks = context.search_tracks(criteria)

    return {
        "artists":render_items(artists,request),
        "albums":render_detail(context, request, albums or []),
        "tracks":render_tracks(tracks,request,show_artist = True)}

def artist_list(context, request):
    items = context.list_items(request)
    return {"items":"", "title":"list", "index": FILTER_INDEX, "keys": keys}

def view_data(context,request):
    request.url_quote = url_quote
    items = context.list_items(request)
    return Response(render_items(items, request))

def view_artist_detail(context, request):
    return Response(render_detail(context, request))

def render_detail(context,request, albums = None):
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
                           context = context, artist = artist)

def serve(context,request):
    result = context.get_file(request)
    if result:
        buf,length,fname = result
        try:
            return _serve(buf,length,fname)
        finally:
            buf.close()
    else:
        return HTTPNotFound()
        
def _serve(filebuf,filename,filesize):
    response = Response(content_type ="binary/octet-stream")
    response.headers.add("Content-Disposition",
                         "attachment; filename=%s; size=%d" % (
            filename,filesize))
    
    response.body = filebuf.read()
    return response

def render_items(items, request):
    request.url_quote = quote
    return render_template("templates/data.pt", 
                           items = items, 
                           request = request)
        
def render_tracks(items, request, show_artist = False):
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
                return u"%s by %s" % (track_title,track.artist or u'(Unknown)')
            else:
                return u"%s by %s" % (track_title, u'(Unknown)')
        else:
            return track_title

    return _x
