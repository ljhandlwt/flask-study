function settings_form_check(){
	file=document.getElementsByName("avatar")[0].files[0];
	if(file.type!='image/jpeg');
		alert("请上存jpg格式的头像!");
	else if(file.size>1024*1024)
		alert("文件大小过大!");
	else
		return true;
		
	return false;
}