$(document).ready(function(e){
	$("#header ul li").mouseover(function(e){
		$(this).addClass("header_listshow");
	});
	$("#header ul li").mouseout(function(e){
		$(this).removeClass("header_listshow");
	});
});