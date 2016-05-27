$(document).ready(function(e){
	$("td.error").hide();
	
	$("form#form_change").submit(function(e){
		var new_password=$("input[name='new_password']").val();
		var new_password_again=$("input[name='new_password_again']").val();
		var is_ok=true;
		
		$("td.error").hide();
		
		if((/[\u4e00-\u9fa5]/).test(new_password)||!(/^\S{6,16}$/).test(new_password)){
			$("td.error[name='new_password']").show();
			is_ok=false;
		}
		if(new_password!=new_password_again){
			$("td.error[name='new_password_again']").show();
			is_ok=false;
		}
		if(!is_ok)
			e.preventDefault();
	});
});