$('#id_comment_post').bind('click', function(){
	if ($('#id_create_ucomment').validate().form()){
	} else {
		return false;
	} 
	$('#id_comment_post').attr('disabled', 'disabled');
	controller.submitForm('#id_create_ucomment');
	return false;
});

$("#id_cancel_create").bind('click', function(){
	controller.closeSecondDialog();
});