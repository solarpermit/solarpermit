/*
$('.comment-list li').hover(
	function (){
		cid = $(this).data('commentId');
		$('#button-div-'+cid).css("visibility","visible");
	},
	function (){
		cid = $(this).data('commentId');
		if ($("#button-div-"+cid+" form").length==0){
			$('#button-div-'+cid).css("visibility","hidden");
		}
		
	}
);
*/
$('#id_a_hide').click(function (event) {
	show_comment_a();
});

$('#id_close_btn').click(function (event) {
	jQuery.fancybox.close();
	if ($('#id_close_btn').data('commentsChanged') == 'yes') {
		controller.postRequest('/jurisdiction/{{jurisdiction.id}}/',{ajax: 'reload_all_items'});
	}
});
$('.modal_dialog_close').click(function (event) {
	jQuery.fancybox.close();
	if ($('#id_close_btn').data('commentsChanged') == 'yes') {
		controller.postRequest('/jurisdiction/{{jurisdiction.id}}/',{ajax: 'reload_all_items'});
	}
});

function show_comment_a(){
	$('#show_commnet_div').empty().append('<a id="id_a_show" href="#"><img src="/media/images/arrow_right.png" style="vertical-align:middle;" alt="show old comments"  > Show old comments </a>');
	$('#old_list').hide();
	$('#id_a_show').bind('click', function(){hide_comment_a();});
}

function hide_comment_a(){
	$('#show_commnet_div').empty().append('<a id="id_a_hide" href="#"><img src="/media/images/arrow_down.png" style="vertical-align:middle;" alt="hide old comments"  > Hide old comments </a>');
	$('#old_list').show();
	$('#id_a_hide').bind('click', function(){show_comment_a();});;
}

$('#add_new_comment_bt').click(function (){
	controller.postRequest('/jurisdiction_comment/',{ajax: 'create_jurisdiction_comment', jurisdiction_id: {{jurisdiction.id}}, answer_id: {{answer.id}} });
	return false;
});

$('#show_old_comments_link').click(function() {
	jid = $(this).data('jid')
	old_id = $(this).data('oldid')
	controller.postRequest('/jurisdiction_comment/',{ajax: 'show_old_comments', jurisdiction_id: jid, answer_id: old_id });
	return false;
});


