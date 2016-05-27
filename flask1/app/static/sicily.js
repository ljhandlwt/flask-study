var cnt=0;
var is_press=false;
var sx1,sx2,sy1,sy2;
$(document).ready(function(e) {
	$("div#sicily").css("top",$(window).height()/4);
	$("div#sicily").css("left",$(window).width()*3/4);
	var sicilies=document.getElementById("sicily").childNodes;
	for(i=0;i<sicilies.length;++i)
		sicilies[i].ondragstart=function(){return false;};
	var imgs=$("div#sicily img.sicily_body");
	imgs.eq(1).hide();
	imgs.eq(2).hide();
	setInterval("update()",100);
	
	$(window).mousemove(function(e) {
		if(is_press){
			$("div#sicily").css("top",e.clientY-sy1+sy2);
			$("div#sicily").css("left",e.clientX-sx1+sx2);
		}
    });
	$(window).mousedown(function(e) {
		sx1=e.clientX;
		sy1=e.clientY;
		sx2=parseInt($("div#sicily").first().css("left"));
		sy2=parseInt($("div#sicily").first().css("top"));
    });
	$("div#sicily").mousedown(function(e){
		is_press=true;
	});
	$("div#sicily").mouseup(function(e){
		is_press=false;
	});
});

function update(){
	var sicilies=$("div#sicily img.sicily_body");
	++cnt;
	if(cnt%30==0){
		sicilies.eq(0).show();
		sicilies.eq(2).hide();
	}
	else if(cnt%30==27){
		sicilies.eq(1).show();
		sicilies.eq(0).hide();
	}
	else if(cnt%30==29){
		sicilies.eq(2).show();
		sicilies.eq(1).hide();
	}
}