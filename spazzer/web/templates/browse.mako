<!DOCTYPE html>
<html>
  <head>
    <title>Browse Collection</title>
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
  $("#artist-list").hide();
  $("#filter-widget").tabs({show:function(){
    $(".artist-item").each(function(idx){
      var content = $(this).find(".artist-content");
      $(this).find(".artist-header").click(function(event){
          event.preventDefault();
          var link = $(event.target);
          var url = $(link).attr("href");
          if(!$(content).is(":visible")){
            $(content).html("<div>Loading....</div>").show("normal");
            $.get(url,function(data){
                        $(content).hide("fast").html(data).show("normal");
                    }//end ajax callback
            );//end get
          }//end if not visible
          else{$(content).toggle("normal");}
      });//end click
    });//end each
   $("#artist-list").fadeIn("normal");
   },//end show
   load:function(event,ui){
          $("#artist-list").hide();
          $(".artist-content").hide();
          $(".artist-content").html("<p/>");
  },//end load
   fx:{opacity: "toggle"}
  });//end tabs
 });//end $
</script>
  </head>
  <body>
  <div id="navigation">
    <ul>
      <li><a href="${get_url(request)}">Browse</a></li>
      <li><a href="${get_url(request)}search">Search</a></li>
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
    <form action="${get_url(request)}search?POST" method="POST">
      <input type="text" name="criteria"/>
      <input type="submit" value="Search"/>
    </form>
  </div>
  <div id="filter-widget" class="list">
    <ul>
      % for idx in keys:
      <li>
	<a href="${get_url(request)}/${index[idx]}">${idx}</a>
      </li>
      %endfor
    </ul>
    </div>

  </body>
</html>