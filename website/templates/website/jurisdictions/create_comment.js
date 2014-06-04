$('#id_comment_post').bind('click', function(){
	if ($('#id_create_comment').validate().form()){
	} else {
		return false;
	} 
	$('#id_comment_post').attr('disabled', 'disabled');
	controller.submitForm('#id_create_comment');
	return false;
});

$('#id_cancel_create').click(function (){
	controller.closeSecondDialog();
});