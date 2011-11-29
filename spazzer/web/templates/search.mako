<!DOCTYPE html>
<html>
<head>
  <title>Search Collection</title>
	<link type="text/css" href="${request.application_url}/static/css/custom-theme/style.css" rel="stylesheet" />
	<link type="text/css" href="${request.application_url}/static/css/site.css" rel="stylesheet" />
	<link type="text/css"
	      href="${request.application_url}/static/css/jplayer.pink.flag.css"
	      rel="stylesheet" />
	<script type="text/javascript" src="${request.application_url}/static/js/jquery-1.7.1.min.js"></script>
	<script type="text/javascript"
	src="${request.application_url}/static/js/jquery-ui-1.8.16.custom.min.js"></script>
	<script type="text/javascript"
	src="${request.application_url}/static/js/jquery.tmpl.min.js"></script>
	<script type="text/javascript"
	src="${request.application_url}/static/js/jQuery.jPlayer.2.1.0/jquery.jplayer.min.js"></script>
	<script type="text/javascript"
	src="${request.application_url}/static/js/jQuery.jPlayer.2.1.0/add-on/jplayer.playlist.min.js"></script>
	<script type="text/javascript" src="${request.application_url}/static/js/ui.js"></script>

</head>
<body>
  <div id="navigation">
    <ul>
      <li><a href="${request.context.get_url(request)}">Browse</a></li>
      <li><a href="${request.context.get_url(request)}search">Search</a></li>
      <li><a href="${request.application_url}/admin">Manage</a></li>
    </ul>
  </div>
  </div>
   <div id="player-widget"></div>
    <div id="search">
      <form action="?POST" method="POST">
	<input type="text" name="criteria"/>
	<input type="submit" value="Search"/>
      </form>
    </div>
    <div id="results" class="ui-widget-content">
	<div id="artist-results" class="results">
	  <h3>Artists</h3>
	  <p class="info">
	    Artists whose name contains '${criteria}'
	  </p>
	  <div class="content"></div>
	</div>
	<div id="album-results" class="results">
	  <h3>Albums</h3>
	  <p class="info">
	    Albums whose name contains '${criteria}'
	  </p>
	  <div class="content"></div>
	</div>
	<div id="track-results" class="results">
	  <h3>Tracks</h3>
	  <p class="info">
	    Tracks whose title contains '${criteria}'
	  </p>
	  <div class="content"></div>
	</div>
    </div>
  % if results:
  <script type="text/javascript">
    var results = ${results|n};
  </script>
  %else:
  <script type="text/javascript">
    var results = {};
  </script>
  %endif
<script type="text/javascript">
$(function(){
   $.UI.init_search_results("#results");
   $.UI.init_player_widget("#player-widget",
        {
          swfPath:"${request.application_url}/static/js/jQuery.jPlayer.2.1.0/"
      });

});
</script>
</body>
</html>
