/*
$('#{{form_create_account_id}}').validate({
	messages: {
		email: 'You must enter a valid email address. For example, myname@mycompany.com.',
		password: 'Your password must be a minimum of 8 characters.',
		verify_password: 'The password fields must be exactly the same.'
	}
});
*/
function {{form_id}}_update_buttons() {
	//if all fields are populated, enable button right the way
	if ($('#{{form_id}}_field_field_title').val() != '' &&
		$('#{{form_id}}_field_field_value').val() != '') {
		$('#{{form_id}}_submit_button').removeClass('disabled');
	} else {
		$('#{{form_id}}_submit_button').addClass('disabled');
	}
}

{{form_id}}_update_buttons(); //initialize

$('#{{form_id}}_field_field_title').keyup(function() {
	{{form_id}}_update_buttons();
});

$('#{{form_id}}_field_field_value').keyup(function() {
	{{form_id}}_update_buttons();
});

$('#{{form_id}}_submit_button').click(function() {
    if($('#{{form_id}}').validate().form()){
        $('{{form_id}}_submit_button').attr('disabled','disabled');
    }
});

$('#{{form_id}}_cancel').click(function() {
	jQuery.fancybox.close();
    return false;
});

controller.setUpFormSubmitModalDialog('#{{form_id}}', '#{{form_id}}_submit_button');
