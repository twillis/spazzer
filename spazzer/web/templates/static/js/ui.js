/*ui logic for spazzer depends on jquery*/
(function($){

  var init_artist_header_click = function(selector, OPTIONS, render_cb){
      /*handle click events on all child headers of selector present and future*/
      $(selector).find(OPTIONS.header_selector).live("click",
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
							 }
						     });
     
  };
  var template_cache = {};
  var render = function(template, data, container){
      /*handles template caching*/
      var x = function(){
	  console.info("rendering data with template " + template);
	  $(container).hide("fast").html($.tmpl(template, data)).show("normal");
      };

      if(!template_cache[template]){
	  $.get(template,function(data){
		    console.info("fetched template: " + template);
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
		  detail_template: "/static/detail.html"
	      };
	      
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      
	      var render_artist_content_cb = function(container, data){
		  render(OPTIONS.detail_template, data, container);

	      };

	      var render_artist_list = function(data, status, xhr){
		  render(OPTIONS.artist_list_template, data, $("#panel-content", selector));
	      };

	      init_artist_header_click(selector, OPTIONS, render_artist_content_cb);

	      $(selector).tabs(
		  {show: function(){
		       $(OPTIONS.list_selector).fadeIn("normal");
		   }, //end show

		   load: function(event,ui){
		       $(OPTIONS.list_selector).hide();
		       $(OPTIONS.content_selector).hide();
		       $(OPTIONS.content_selector).html("<p/>");
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
		solution:"html, flash"  
	      };
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});	      
	      $(document).ready(function(){$(selector).jPlayer(OPTIONS);});//player init
	      self.play = function(url){
		  $(selector).jPlayer("setMedia",{mp3:url}).jPlayer("play");		  
	      };
	  },
	  init_search_results: function(selector, options){
	      var DEFAULT_OPTIONS = {
		  item_selector: ".artist-item",
		  content_selector: ".artist-content",
		  header_selector: ".artist-header",
		  list_selector: ".artist-list"
	      };
	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      $(selector).find(OPTIONS.content_selector).hide();
	      init_artist_header_click(selector, OPTIONS);
	  }
  };   
 })(jQuery);

