$(".ucommentReplyBtn").click(function(){
	cid = $(this).data("cid");
	controller.postRequest('.', {ajax: 'reply_comment', cid: cid});
	return false;
});

$(".ucommentDeleteBtn").click(function () {
	cid = $(this).data("cid");
	controller.postRequest('.', {ajax: 'remove_comment', cid: cid});
	return false;
});

$(".ucommentFlagBtn").click(function () {
	cid = $(this).data("cid");
	controller.postRequest('.', {ajax: 'flag_comment', cid: cid});
	return false;
});