//initial bind event for list items
$('#admin_select_list .selectable').click(function (event) {
	var $target = $(event.target);
	if (!$target.hasClass('selectable')) {
		$target = $target.parent('.selectable');
	}
	
	if ($target.hasClass('selected')) {
		$target.removeClass('selected');
		$('#mid').val('');
		$('#admin_select_next_btn').addClass('disabled');
	} else {
		//deselect other ones first
		$('#admin_select_list .selectable.selected').removeClass('selected');
		$target.addClass('selected');
		$('#mid').val($target.attr('data-mid'));
		$('#admin_select_next_btn').removeClass('disabled');
	}
});

function assign_new_remove_me() {
	var mid = $('#mid').val();
	controller.postRequest('/organization/', {ajax: 'assign_new_remove_me', mid: mid});
}

$('#admin_select_next_btn').click(function (event) {
	var $target = $(event.target);
	if ($target.hasClass('disabled')) return; //don't proceed if button disabled
	controller.showConfirm({
		title: 'Assign new adminstrator',
		message: 'Proceed to assign selected member as the new administrator, and remove myself from {{organization.name}}?',
		proceedText: 'OK',
		cancelText: 'Cancel',
		callback: assign_new_remove_me
	});
});

$('#admin_select_cancel_btn').click(function () {
	controller.closeSecondDialog();
});