/*ui logic for spazzer depends on jquery*/
(function($){

  var init_header_click = function(selector, OPTIONS){
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
								       content.hide("fast").html(data).show("normal");
								   }
								  );
							 }else{
							     $(content).toggle("normal");
							 }
						     });
     
  };

  $.UI = {init_filter_widget: function(selector, options){
	      var DEFAULT_OPTIONS = {
		  item_selector: ".artist-item",
		  content_selector: ".artist-content",
		  header_selector: ".artist-header",
		  list_selector: ".artist-list"
	      };

	      var OPTIONS = $.extend(DEFAULT_OPTIONS, options || {});
	      init_header_click(selector, OPTIONS);

	      $(selector).tabs(
		  {show: function(){
		       $(OPTIONS.list_selector).fadeIn("normal");
		   }, //end show

		   load: function(event,ui){
		       $(OPTIONS.list_selector).hide();
		       $(OPTIONS.content_selector).hide();
		       $(OPTIONS.content_selector).html("<p/>");
		   },//end load
		   fx:{opacity: "toggle"}
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
	      init_header_click(selector, OPTIONS);
	  }
  };   
 })(jQuery);

