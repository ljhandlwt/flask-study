$(document).ready(function(e){
	$("td.error").hide();
	
	$("form#form_register").submit(function(e){
		var nickname=$("input[name='nickname']").val();
		var password=$("input[name='password']").val();
		var password_again=$("input[name='password_again']").val();
		var email=$("input[name='email']").val();
		var is_ok=true;
		
		$("td.error").hide();
		
		if(!(/^[A-Za-z_0-9]{1,20}$/).test(nickname)){
			$("td.error[name='nickname']").show();
			is_ok=false;
		}
		if((/[\u4e00-\u9fa5]/).test(password)||!(/^\S{6,16}$/).test(password)){
			$("td.error[name='password']").show();
			is_ok=false;
		}
		if(password!=password_again){
			$("td.error[name='password_again']").show();
			is_ok=false;
		}
		if(!(/^[a-z0-9]+([._\\-]*[a-z0-9])*@([a-z0-9]+[-a-z0-9]*[a-z0-9]+.){1,63}[a-z0-9]+$/).test(email)){
			$("td.error[name='email']").show();
			is_ok=false;
		}
		if(!is_ok)
			e.preventDefault();
	});
});