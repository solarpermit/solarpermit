$('#reply_comment_btn').bind('click', function(){
	if ($('#id_reply_comment').validate().form()){
	} else {
		return false;
	}
	controller.submitForm('#id_reply_comment');
	$('#reply_comment_btn').attr('disabled', 'disabled');
	return false;
});

$('#id_cancel_create').click(function() {
	controller.postRequest('/jurisdiction_comment/', {ajax: 'cancel_reply', cid: {{comment.id}}});
	return false;
});