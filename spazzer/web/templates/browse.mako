<!DOCTYPE html>
<html>
  <head>
    <title>Browse Collection</title>
	<link type="text/css" href="${request.application_url}/static/css/custom-theme/style.css" rel="stylesheet" />
	<link type="text/css"
	href="${request.application_url}/static/css/jplayer.pink.flag.css"
	rel="stylesheet" />
	<link type="text/css"
	href="${request.application_url}/static/css/site.css"
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
      <li><a href="${get_url(request)}">Browse</a></li>
      <li><a href="${get_url(request)}search">Search</a></li>
      <li><a href="${request.application_url}/admin">Manage</a></li>
    </ul>
  </div>
  <div id="player-widget"></div>
  <div id="search">
    <form action="${get_url(request)}search?POST" method="POST">
      <input type="text" name="criteria"/>
      <input type="submit" value="Search"/>
    </form>
  </div>
  <div id="filter-widget" class="list">
    <ul>
      %for idx in keys:
      <li>
	<a href="${get_url(request)}/${index[idx]}">${idx}</a>
      </li>
      %endfor
    </ul>
    <div id="panel-content"></div>
  </div>
  <script type="text/javascript">
    $(function(){
      $.UI.init_filter_widget("#filter-widget");
      $.UI.init_player_widget("#player-widget",
        {
          swfPath:"${request.application_url}/static/js/jQuery.jPlayer.2.1.0/"
      });
    });
  </script>
  </body>
</html>
