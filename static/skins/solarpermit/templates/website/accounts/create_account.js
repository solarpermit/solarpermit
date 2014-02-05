$('#{{form_create_account_id}}').validate({
	messages: {
		email: 'You must enter a valid email address. For example, myname@mycompany.com.',
		password: 'Your password must be a minimum of 8 characters.',
		verify_password: 'The password fields must be exactly the same.'
	}
});
/*
$('#{{form_create_account_id}}_field_firstname').blur(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_lastname').blur(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_title').blur(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_username').blur(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_email').blur(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_display_as_realname').click(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_display_as_username').click(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_password').blur(function(event) {
	$target = $(event.target);
	if ($target.val() != '') {
		if ($target.valid()) {
			$('#{{form_create_account_id}}_field_verify_password').removeAttr('disabled');
			$('#{{form_create_account_id}}_field_verify_password').focus();
		} else {
			$('#{{form_create_account_id}}_field_verify_password').attr('disabled', 'disabled');
		}
	}
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_verify_password').blur(function() {
	create_account_update_buttons();
});
*/
function create_account_update_buttons() {
	var realname = 'failed';
	var username = 'failed';

	//if all fields are populated, not need to validated, enable button
	if($('#{{form_create_account_id}}_field_display_as_realname').is(':checked')) {
		if ($('#{{form_create_account_id}}_field_firstname').val() != '')	
			if ($('#{{form_create_account_id}}_field_lastname').val() != '')	
				realname = 'passed';
		$('#{{form_create_account_id}}_field_firstname').addClass('required');
		$('#{{form_create_account_id}}_field_lastname').addClass('required');
	} else {
		$('#{{form_create_account_id}}_field_firstname').removeClass('required');
		$('#{{form_create_account_id}}_field_lastname').removeClass('required');
	}
	if ($('#{{form_create_account_id}}_field_username').val() != '')	
		realname = 'passed';
	//if($('#{{form_create_account_id}}_field_display_as_username').is(':checked')) {
		if ($('#{{form_create_account_id}}_field_username').val() != '')		
				username = 'passed';
		//$('#{{form_create_account_id}}_field_username').addClass('required');
	//} else {
		//$('#{{form_create_account_id}}_field_username').removeClass('required');
	//}
	
	//if (realname == 'passed' || username == 'passed')
	if (realname == 'passed' && username == 'passed')
		if ($('#{{form_create_account_id}}_field_title').val() != '')		
			if ($('#{{form_create_account_id}}_field_email').val() != '')
				if ($('#{{form_create_account_id}}_field_password').val() != '')
					if ($('#{{form_create_account_id}}_field_verify_password').val() != '') {
						if ($('#{{form_create_account_id}}_field_password').val() == $('#{{form_create_account_id}}_field_verify_password').val()){
							$('#{{form_create_account_id}}_submit_button').removeClass('disabled');
							return;
						}
					}
	$('#{{form_create_account_id}}_submit_button').addClass('disabled');
}

$("#create_account_cancel").click( function(event) {
		jQuery.fancybox.close();
});

$('#{{form_create_account_id}}_submit_button').click(function(event) {
	$target = $(event.target);
	if (!$target.hasClass('disabled')) {
		if ($('#{{form_create_account_id}}').valid()) {
			controller.postRequest('/account/', {ajax: 'terms_of_use'});
		}
	}
	return false;
});

$('#launch_privacy_policy').click(function() {
	controller.postRequest('/account/', {ajax: 'privacy_policy'});
	return false;
});
$('#launch_disclaimer').click(function() {
	controller.postRequest('/account/', {ajax: 'disclaimer'});
	return false;
});

$('#{{form_create_account_id}}_field_firstname').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_lastname').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_title').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_username').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_email').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_verify_password').keyup(function() {
	create_account_update_buttons();
});

$('#{{form_create_account_id}}_field_password').blur(function(event) {
	$target = $(event.target);
	if ($target.val() != '') {
		if ($target.valid()) {
			$('#{{form_create_account_id}}_field_verify_password').removeAttr('disabled');
			$('#{{form_create_account_id}}_field_verify_password').focus();
		} else {
			$('#{{form_create_account_id}}_field_verify_password').attr('disabled', 'disabled');
		}
	}
	create_account_update_buttons();
});