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
	src="${request.application_url}/static/js/jQuery.jPlayer.2.1.0/jquery.jplayer.min.js"></script>
	<script type="text/javascript" src="${request.application_url}/static/js/ui.js"></script>

  </head>
  <body>
  <div id="navigation">
    <ul>
      <li><a href="${get_url(request)}">Browse</a></li>
      <li><a href="${get_url(request)}search">Search</a></li>
      <li><a href="${request.application_url}/admin">Manage</a></li>
    </ul>
    <div id="player"></div>
    <div id="jp_container_1" class="jp-audio">
			<div class="jp-type-single">
				<div class="jp-gui jp-interface">
					<ul class="jp-controls">
						<li><a href="javascript:;" class="jp-play" tabindex="1">play</a></li>
						<li><a href="javascript:;" class="jp-pause" tabindex="1" style="display: none; ">pause</a></li>
						<li><a href="javascript:;" class="jp-stop" tabindex="1">stop</a></li>
						<li><a href="javascript:;" class="jp-mute" tabindex="1" title="mute">mute</a></li>
						<li><a href="javascript:;" class="jp-unmute" tabindex="1" title="unmute" style="display: none; ">unmute</a></li>
						<li><a href="javascript:;" class="jp-volume-max" tabindex="1" title="max volume">max volume</a></li>
					</ul>
					<div class="jp-progress">
						<div class="jp-seek-bar" style="width: 100%; ">
							<div class="jp-play-bar" style="width: 0%; "></div>

						</div>
					</div>
					<div class="jp-volume-bar">
						<div class="jp-volume-bar-value" style="width: 80%; "></div>
					</div>
					<div class="jp-current-time">00:00</div>
					<div class="jp-duration">04:27</div>
					<ul class="jp-toggles">
						<li><a href="javascript:;" class="jp-repeat" tabindex="1" title="repeat">repeat</a></li>
						<li><a href="javascript:;" class="jp-repeat-off" tabindex="1" title="repeat off" style="display: none; ">repeat off</a></li>
					</ul>
				</div>
				<div class="jp-title">
					<ul>
						<li>Cro Magnon Man</li>
					</ul>
				</div>
				<div class="jp-no-solution" style="display: none; ">
					<span>Update Required</span>
					To play the media you will need to either update your browser to a recent version or update your <a href="http://get.adobe.com/flashplayer/" target="_blank">Flash plugin</a>.
				</div>
			</div>
		</div>
  </div>
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
  </div>
  <script type="text/javascript">
    $(function(){
      $.UI.init_filter_widget("#filter-widget");
      $.UI.init_player_widget("#player",
        {
          swfPath:"${request.application_url}/static/js/jQuery.jPlayer.2.1.0/"
      });
    });

    
    function play(url){
       $.UI.play(url);
    }
  </script>
  </body>
</html>
