$(".commentReplayBtn").click(function(){
	cid = $(this).data("cid");
	controller.postRequest('/jurisdiction_comment/', {ajax: 'reply_comment', cid: cid});
	return false;
});

$(".commentFlagBtn").click(function () {
	cid = $(this).data("cid");
	controller.postRequest('/jurisdiction_comment/', {ajax: 'flag_comment', cid: cid});
	return false;
});