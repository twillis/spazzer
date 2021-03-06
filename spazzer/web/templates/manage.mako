<!DOCTYPE HTML>
<html>
<head>
  <title>Manage Collection</title>
	<link type="text/css" href="${request.application_url}/static/css/custom-theme/style.css" rel="stylesheet" />
	<link type="text/css" href="${request.application_url}/static/css/site.css" rel="stylesheet" />
	<script type="text/javascript" src="${request.application_url}/static/js/jquery-1.7.1.min.js"></script>
	<script type="text/javascript" src="${request.application_url}/static/js/jquery-ui-1.8.16.custom.min.js"></script>
<script type="text/javascript">
$(function(){
$("#manage-content").hide().fadeIn("slow");
});
</script>
</head>
<body>
  <div id="navigation">
    <ul>
      <li><a href="${request.application_url}/collection">Browse</a></li>
      <li><a href="${request.application_url}/collection/search">Search</a></li>
      <li><a href="${request.application_url}/admin">Manage</a></li>
    </ul>
  </div>
  <div id="manage-content" class="ui-widget-content">
    <h2>Collection Mounts</h2>
    <table class="mount-table">
	%for mount in mounts:
      <tr>
	<td class="mount-cell">${mount.mount}</td>
	<td class="action-cell">
	  <form action="?POST=1&amp;DELETE=1" method="POST">
	    <input type="hidden" name="mount" value="${mount.id}"/>
	    <input type="image" alt="Remove" 
		   src="${request.application_url}/static/css/custom-theme/images/remove.png"/>
	  </form>
	</td>
      </tr>
	%endfor
      <tr>
	<td><h4>Add a new mount</h4></td>
	<td>
	  <div id="add-mount">
	    <form action="?POST" method="POST">
	      <input type="text" name="mount"/>
	      <input type="image" alt="Add" 
		     src="${request.application_url}/static/css/custom-theme/images/add.png"/>
	    </form>
	  </div>
	</td>
      </tr>
    </table>
    <hr/>
    <form action="?POST=1&amp;SCAN=1" method="POST">
	<input type="image" value="update" 
	       src="${request.application_url}/static/css/custom-theme/images/update.png"/>
    </form>
    <div class="error-message" tal:content="message"/>
  </div>
</body>
</html>
