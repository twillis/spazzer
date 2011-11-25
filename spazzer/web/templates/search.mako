<!DOCTYPE html>
<html>
<head>
  <title>Search Collection</title>
	<link type="text/css" href="${request.application_url}/static/css/custom-theme/style.css" rel="stylesheet" />
	<link type="text/css" href="${request.application_url}/static/css/site.css" rel="stylesheet" />
	<script type="text/javascript" src="${request.application_url}/static/js/jquery-1.7.1.min.js"></script>
	<script type="text/javascript" src="${request.application_url}/static/js/jquery-ui-1.8.16.custom.min.js"></script>
<script type="text/javascript">
function play(file_url){
  var player = $("#player-object")[0];
  player.SetVariable("player:jsUrl",file_url);
  player.SetVariable("player:jsPlay", "");
}
$(function(){
    $("#results").hide();
    $(".artist-item").each(function(idx){
      var content = $(this).find(".artist-content").html("<div>Loading...</div>").hide();
      $(this).find(".artist-header").click(function(event){
          event.preventDefault();
          var link = $(event.target);
          var url = $(link).attr("href");
          if(!$(content).is(":visible")){
            $.get(url,function(data){
                        $(content).html(data).toggle("normal");
                    }//end ajax callback
            );//end get
          }//end if not visible
      });//end click
    });//end each
   $("#results").fadeIn("results");
   }//end show
  );//end tabs
</script>
</head>
<body>
  <div id="navigation">
    <ul>
      <li><a href="${request.context.get_url(request)}">Browse</a></li>
      <li><a href="${request.context.get_url(request)}search">Search</a></li>
      <li><a href="${request.application_url}/admin">Manage</a></li>
    </ul>
    <div id="player">
      <object id="player-object" type="application/x-shockwave-flash" 
	      data="${request.application_url}/static/flash/player_mp3_maxi.swf" width="200" height="20">
     <param name="movie" value="${request.application_url}/static/flash/player_mp3_maxi.swf" />
     <param name="FlashVars" value="showvolume=1&amp;showinfo=1&amp;bgcolor1=2e2e2e&amp;bgcolor2=d4d4d4" />
</object>      
    </div>
  </div>
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
	  <span>${artists|n}</span>
	</div>
	<div id="album-results" class="results">
	  <h3>Albums</h3>
	  <p class="info">
	    Albums whose name contains '${criteria}'
	  </p>
	  <span>${albums|n}</span>
	</div>
	<div id="track-results" class="results">
	  <h3>Tracks</h3>
	  <p class="info">
	    Tracks whose title contains '${criteria}'
	  </p>
	  <span>${tracks|n}</span>
	</div>
    </div>
</body>
</html>