/*ui logic for spazzer depends on jquery*/
(function($){

  var init_artist_view = function(selector, OPTIONS, render_cb){
      /*handle click events on all child headers of selector present and future*/
      $(OPTIONS.header_selector, selector).live("click",
						     function(event){
							 event.preventDefault();
							 var content = $(event.target).closest(OPTIONS.item_selector).children(OPTIONS.content_selector);
							 var link = $(event.target);
							 var url = $(link).attr("href");
							 if(!$(content).is(":visible")){

							     $(content).html("<div>Loading....</div>").show("normal");
							     $.get(url, 
								   function(data){
								       render_cb(content, data);

								   }
								  );
							 }else{
							     $(content).toggle("normal");
							     console.info("toggled");
							 }
						     });
      /*handles click events on all play links*/
      $(OPTIONS.play_link, selector).live("click",
					  function(event){
					      event.preventDefault();
					      var url = $(event.target).attr("href");
					      $.UI.play(url, {artist:$(event.target).attr("artist"),
							     album_title:$(event.target).attr("album-title"),
							     track_title:$(event.target).attr("track-title")}); 
					  });
     
  };
  var template_cache = {};
  var render = function(template, data, container, cb){
      /*handles template caching
       * template: url to template to fetched
       * data: data to use to render the template
       * container: container to insert template result in to
       * cb: callback to call when rendering is done*/
      var x = function(){
	  var content = $.tmpl(template, data);
	  $(container).hide("fast").html(content).show("normal");
	  if(cb){
	      cb();
	  }
      };

      if(!template_cache[template]){
	  $.get(template,function(data){
		    template_cache[template] = $.template(template, data);
		    x();
		});
      }else{
	  x();
      }
  };

  $.UI = {

      init_filter_widget: function(selector, options){
	      var DEFAULT_OPTIONS = {
		  item_selector: ".artist-item",
		  content_selector: ".artist-content",
		  header_selector: ".artist-header",
		  list_selector: ".artist-list",
		  artist_list_template: "/static/artist-list.html",
		  detail_template: "/static/detail.html",
		  tracks_template: "/static/tracks.html",
		  play_link:".play-link"
	      };
	      
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      
	      var render_artist_content_cb = function(container, data){
		  render(OPTIONS.detail_template, data, container);

	      };

	      var render_artist_list = function(data, status, xhr){
		  render(OPTIONS.artist_list_template, data, $("#panel-content", selector), 
			 function(){
			     $(OPTIONS.content_selector).hide();
			     $(OPTIONS.content_selector).html("<p/>");
			 });
	      };

	      init_artist_view(selector, OPTIONS, render_artist_content_cb);

	      $(selector).tabs(
		  {show: function(){
		       $(OPTIONS.list_selector).fadeIn("normal");
		   }, //end show

		   load: function(event,ui){
		   },//end load
		   ajaxOptions:{
		       success:render_artist_list
		   },
		   fx: {opacity: "toggle"}
		  });//end tabs
	  },
	  init_player_widget: function(selector, options){
	      var self = this;
	      var DEFAULT_OPTIONS = {
		  solution:"html, flash",
		  player_template:"/static/player.html"
	      };
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      self.PLAYLIST = new jPlayerPlaylist({
						      jPlayer: selector + " " + "#player",
						      cssSelectorAncestor: selector + " " + "#jp_container_1"
						  }, 
						  [],
						  {playlistOptions:{enableRemoveControls:true}}
						 );

              render(OPTIONS.player_template,{}, selector, function(){
			 $("#player", selector).jPlayer(OPTIONS);
			 self.play = function(url, info){
			     self.PLAYLIST.add({artist:info.artist,
					       title:info.track_title + "(" + info.album_title+ ")",
					       mp3:url});
			     $("#player",selector).jPlayer("play");
	      };
			 

		     });

	  },
	  init_search_results: function(selector, options){
	      var DEFAULT_OPTIONS = {
		  item_selector: ".artist-item",
		  content_selector: ".artist-content",
		  header_selector: ".artist-header",
		  list_selector: ".artist-list",
		  artist_list_template: "/static/artist-list.html",
		  detail_template: "/static/detail.html",
		  tracks_template: "/static/tracks.html",
		  play_link:".play-link"

	      };
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      var render_artist_list = function(data){
		  render(OPTIONS.artist_list_template, data, $(".content",$("#artist-results", "#results")), 
			 function(){
			     $(OPTIONS.content_selector).hide();
			     $(OPTIONS.content_selector).html("<p/>");
			 });

	      };
	      var render_artist_content_cb = function(container, data){
		  render(OPTIONS.detail_template, data, container);

	      };

	      var render_album_list = function(data){
		  render(OPTIONS.detail_template, data, $(".content",$("#album-results", "#results")));
	      };

	      var render_track_list = function(data){
		  render(OPTIONS.tracks_template, data, $(".content",$("#track-results", "#results")));
	      };

	      $(selector).find(OPTIONS.content_selector).hide();
	      init_artist_view(selector, OPTIONS, render_artist_content_cb);

	      if(window.results){
		  render_artist_list({items:window.results.artists});
		  render_album_list({items:window.results.albums});
		  render_track_list({items:window.results.tracks});
	      }
	  }
  };   
 })(jQuery);

