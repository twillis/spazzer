from webob import Response
from webob.exc import HTTPNotFound
from repoze.bfg.chameleon_zpt import render_template_to_response as render, render_template
import os

ALPHABET_SEQ = ( "A","B","C","D","E","F","G","H","I","J",
                 "K","L","M","N","O","P","Q","U","R","S",
                 "T","U","V","W","X","Y","Z")
idx = [(c, "data/?start=%s" % c) for c in ALPHABET_SEQ]
FILTER_INDEX = {}

EXTRA_INDEX = {"[ALL]":"data/?start=",
                "[#]":"data/?start=__num__",
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

def artist_list(context, request):
    items = context.list_items(request)
    return {"items":"", "title":"list", "index": FILTER_INDEX, "keys": keys}

def artist_view(context, request): pass
def album_list(context, request): pass
def album_view(context, request): pass

def view_data(context,request):
    items = context.list_items(request)
    return Response(render_items(items, request))

def view_artist_detail(context, request):
    return Response(get_artist_detail(context, request))

def get_artist_detail(context,request):
    key = request.params.get("artist")
    print "Key = %s" % key
    try:
        artist = context[key]
    except KeyError, key:
        raise HTTPNotFound()

    return render_template("templates/detail.pt",
                           albums = artist.get_albums(), 
                           request = request, 
                           context = context, artist = artist)

def serve(context,request):
    return _serve(open(context.file_name, "rb"),
                  context.safe_file_name,
                  os.path.getsize(context.file_name))

def serve_album(context,request):
    zf,length,fname = context.get_zip_file()
    try:
        return _serve(zf,fname,length)
    finally:
        zf.close()
        

def _serve(filebuf,filename,filesize):
    response = Response(content_type ="binary/octet-stream")
    response.headers.add("Content-Disposition",
                         "attachment; filename=%s; size=%d" % (
            filename,filesize))
    
    response.body = filebuf.read()
    return response
    

def render_items(items, request):
    return render_template("templates/data.pt", 
                           items = items, 
                           request = request)

            

#artist_list = echo
artist_view = echo
album_list = artist_list
album_view = echo

