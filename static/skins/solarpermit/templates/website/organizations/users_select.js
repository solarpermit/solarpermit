var selectedUserIds = {};

var validator = $('#org_user_select_form').validate();

$('#search_user').bind('keyup', function (event) {
	var $target = $(event.target);
    if ((event.which != 38) &&
    		(event.which != 40) &&
    		(event.which != 13)) {
    	var searchText = $target.val();
    	controller.postRequest('/organization/', {ajax: 'search_user', text: searchText});
    }
});

var enableLeftRightButtons = function () {
	var $leftSelectedItems = $('#user_list .selectable.selected');
	if ($leftSelectedItems.length > 0) {
		$('#user_select_btn').removeClass('disabled');
	} else {
		$('#user_select_btn').addClass('disabled');
	}
	var $rightSelectedItems = $('#selected_user_list .selectable.selected');
	if ($rightSelectedItems.length > 0) {
		$('#user_deselect_btn').removeClass('disabled');
	} else {
		$('#user_deselect_btn').addClass('disabled');
	}
}

var enableInviteButton = function () {
	var $rightItems = $('#selected_user_list .selectable');
	if ($rightItems.length > 0) {
		$('#user_invite_btn').removeClass('disabled');
		document.getElementById('user_invite_btn').disabled = false;
	} else {
		$('#user_invite_btn').addClass('disabled');
		document.getElementById('user_invite_btn').disabled = true;
	}
}

//click to select, single item, shift or control click to select multiple
//global so that users_select_list.js can use too
selectableClick = function (event) {
	var $target = $(event.target);
	if (!$target.hasClass('selectable')) {
		$target = $target.parent('.selectable');
	}
	if (event.shiftKey) {
		//select this, the first selected and anything in between
		//is this also the first, deselect
		if ($target.hasClass('first')) {
			//deselect all
			$selectables = $('.selectable');
			$selectables.removeClass('selected');
			$selectables.removeClass('first');
			$selectables.removeClass('last');
		} else {
			//find first one and last
			$firstSelected = $('.selected.first');
			$lastSelected = $('.selected.last');
			if ($firstSelected.length > 0) {
				$lastSelected.removeClass('last'); //last last no longer last
				$target.addClass('selected');
				$target.addClass('last');
				selectBetween();
			} else {
				//no first one, make this first
				$lastSelected.removeClass('last'); //should not be any last one
				$target.addClass('selected');
				$target.addClass('first');
			}
		}
	} else if (event.ctlKey || event.metaKey) {
		//find first one and last
		$firstSelected = $('.selected.first');
		$lastSelected = $('.selected.last');
		//add or remove this one
		if ($target.hasClass('selected')) {
			//if this is first, make last the first
			if ($target.hasClass('first')) {
				$lastSelected.addClass('first');
				$lastSelected.removeClass('last');
			}
			$target.removeClass('selected');
			$target.removeClass('first');
			$target.removeClass('last');
			selectedUserIds[$target.attr('data-userid')] = false;
		} else {
			if ($firstSelected.length > 0) {
				$lastSelected.removeClass('last'); //last last no longer last
				$target.addClass('selected');
				$target.addClass('last');
			} else {
				//no first one, make this first
				$lastSelected.removeClass('last'); //should not be any last one
				$target.addClass('selected');
				$target.addClass('first');
			}
			selectedUserIds[$target.attr('data-userid')] = true;
		}
	} else {
		//not multiple select, deselect others
		$selectables = $('.selectable');
		$selectables.removeClass('selected');
		$selectables.removeClass('first');
		$selectables.removeClass('last');
		//select just this
		$target.addClass('selected');
		$target.addClass('first');
		selectedUserIds[$target.attr('data-userid')] = true;
	}
	enableLeftRightButtons();
};

//select all selectables between first and last / last and first
//deselect all outside
selectBetween = function () {
	$selectables = $('.selectable');
	var between = false;
	$selectables.each(function () {
		if (between == false) {
			if ($(this).hasClass('first') || $(this).hasClass('last')) {
				between = true;
			} else {
				$(this).removeClass('selected');
			}
		} else {
			if ($(this).hasClass('first') || $(this).hasClass('last')) {
				between = false;
			} else {
				$(this).addClass('selected');
			}
		}
	});
};

//arrow button to selected items, move from left to right
$('#user_select_btn').click(function () {
	var $leftSelectedItems = $('#user_list .selectable.selected');
	$leftSelectedItems.each(function () {
		var $this = $(this);
		$this.removeClass('selected');
		$this.appendTo('#selected_user_list');
	});
	enableLeftRightButtons();
	enableInviteButton();
});
//arrow button to deselected items, move from right to left
$('#user_deselect_btn').click(function () {
	var $rightSelectedItems = $('#selected_user_list .selectable.selected');
	$rightSelectedItems.each(function () {
		var $this = $(this);
		$this.removeClass('selected');
		if ($this.hasClass('emails')) {
			//for email field, just delete
			$this.remove();
		} else {
			//for others, move back to left
			$this.prependTo('#user_list');
		}
	});
	//controller.sortList('#user_list', 'div', 'div');
	enableLeftRightButtons();
	enableInviteButton();
});

$('#invite_email_btn').click(function () {
	var emails = $.trim($('#invite_email').val());
	if (emails == '') { //blank field
		$('#invite_email').val('');
		return;
	}
	if ($('#invite_email').valid()) {
		var div = '<div class="selectable emails" data-userid="" data-useremail="'+emails+'">';
		div += emails;
		div += '</div>';
		var $newDiv = $(div);
		$newDiv.appendTo('#selected_user_list');
		$('#invite_email').val(''); //clean input
		//bind event
		$newDiv.click(function (event) {
			selectableClick(event);
		});
		enableInviteButton();
		validator.resetForm(); //so that error doesn't show up until user click button again
	}
});

$('#user_invite_cancel_btn').click(function () {
	controller.closeSecondDialog();
});

$('#user_invite_btn').click(function (){
	var users = '';
	var emails = '';
	orgid = $('#orgid').val();
	$selectableItems = $('#selected_user_list .selectable');
	if ($selectableItems.length > 0) {
		$selectableItems.each(function () {
			$this = $(this);
			user_id = $this.data('userid');
			if (user_id != ''){
				if (users == ''){
					users = user_id;
				} else{
					users += ','+user_id;
				}
			} else{
				email = $this.data('useremail');
				if (emails == ''){
					emails = email;
				} else{
					emails += ','+email;
				}
			}
		});
	}
	controller.postRequest('/organization/', {ajax: 'invite_member', orgid: orgid, users: users, emails: emails});
	$('#user_invite_btn').addClass('disabled');
	document.getElementById('user_invite_btn').disabled = true;
	return false;
});

