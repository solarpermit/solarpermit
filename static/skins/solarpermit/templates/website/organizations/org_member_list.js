if (typeof org_member_list_changed == 'undefined') {
	var org_member_list_changed = {};
}
if (typeof org_member_list_removed == 'undefined') {
	var org_member_list_removed = {};
}

$('#org_members_list select.unbind').bind('change', function(event){
	$target = $(event.target);
	var memberId = $target.data('memberId');
	var memberUid = $target.data('memberUid');
	var userId = $('#userid').val();
	var right = $target.val();
	//is uer change his own?
	if ((right == 'Member') && (memberUid == userId)) {
		controller.showConfirm({
			title: 'Please confirm',
			message: 'Are you sure you want to change yourself from Administrator to Member?',
			proceedText: 'OK',
			cancelText: 'Cancel',
			callback: function () {
				$target.val('Member'); //change it again if confirmed
				change_member(memberId, right);
			}
		});
		$target.val('Administrator'); //change it back first
	} else {
		change_member(memberId, right);
	}
	return false;
});

function change_member(memberId, right) {
	org_member_list_changed[memberId] = right;
	var changed_text = '';
	for (var mid in org_member_list_changed) {
		if (changed_text != '') {
			changed_text += ',';
		}
		changed_text += mid + ':' + org_member_list_changed[mid];
	}
	$('#changed_members').val(changed_text);
	//change footer buttons...
	if (changed_text != '') {
		showSaveButton()
	}
}
/*
$('.member_name').each(function(i){
		user_id = $(this).data('user');
		member_id = $(this).data('member');
		alert(user_id);
		$(this).bind('mouseover', function(){
			controller.postRequest('/account/', {ajax: 'user_profile_short', user_id: user_id, unique_list_id: member_id, caller:'dialog' });
			});
	});
*/
{% for member in members %}
	$('#id_'+{{member.id}}).bind('mouseover', function(){controller.postRequest('/account/', {ajax: 'user_profile_short', user_id: {{member.user.id}}, unique_list_id: {{member.id}}, caller:'dialog' });});
{% endfor %}
$('#org_members_list a.unbind').bind('click', function(event){
	$target = $(event.target);
	var memberId = $target.data('memberId');
	if ($target.hasClass('undo')) {
		//handle undo
		org_member_list_removed[memberId] = false;
		//enable this row
		$row = $target.closest('table').closest('div');
		$row.find('td').css('color', '');
		$row.find('select').removeAttr('disabled');
		$row.find('.smallbutton').removeClass('undo').html('Remove');
		$row.css('background-color', '');
	} else {
		org_member_list_removed[memberId] = true;
		//hide this row
		//$target.closest('table').hide();
		//disable this row
		$row = $target.closest('table').closest('div');
		$row.find('td').css('color', '#888888');
		$row.find('select').attr('disabled', 'disabled');
		$row.find('.smallbutton').addClass('undo').html('Undo');
		$row.css('background-color', '#bbbbbb').css('opacity', 0.1);
		$row.animate({'opacity': 1}, 5000);
		
	}
	//update hidden input with list of removed members
	var changed_text = '';
	for (var mid in org_member_list_removed) {
		if (org_member_list_removed[mid] == true) {
			if (changed_text != '') {
				changed_text += ',';
			}
			changed_text += mid;
		}
	}
	$('#removed_members').val(changed_text);
	//change footer buttons...
	if (changed_text != '') {
		showSaveButton()
	}
	return false;
});

$('#org_members_list .unbind').removeClass('unbind');

$('.approve_btn').click(function (){
	mid = $(this).data('mid');
	controller.postRequest('/organization/', {ajax: 'handle_pending_request', type: 'approve', mid: mid });
	return false;
});

$('.deny_btn').click(function (){
	mid = $(this).data('mid');
	controller.postRequest('/organization/', {ajax: 'handle_pending_request', type: 'deny', mid: mid });
	return false;
});


function showSaveButton() {
	$('#save_members_btn').show();
	//bind event now since can't do it when hidden
	$('#save_members_btn.unbind').click(function (){
		controller.showConfirm({
			title: 'Please confirm',
			message: 'Are you sure you want to save you change?',
			proceedText: 'OK',
			cancelText: 'Cancel',
			callback: function () {
				controller.submitForm("#form_org_details_members");
			}
		});		
	});
	$('#save_members_btn.unbind').removeClass('unbind'); //only bind one time
	$('#delete_org_btn').hide();
	$('#org_details_close_btn').html('Cancel');
	$('.modal_dialog_bottom_message').html('You have made changes you need to save.');
	$('.modal_dialog_bottom_message').addClass('active');
}