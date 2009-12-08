from webob import Response

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

def artist_list(context, request): pass
def artist_view(context, request): pass
def album_list(context, request): pass
def album_view(context, request): pass

artist_list = echo
artist_view = echo
album_list = echo
album_view = echo
