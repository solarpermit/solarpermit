{% include 'website/form_fields/common_form_utils.js' %}

$('#form_reset_password').validate({
	messages: {
		password: 'Your password must be a minimum of 8 characters.',
		verify_password: 'The password fields must be exactly the same.'
	}
});

$('#form_reset_password_submit_button').click(function (event)
{
	controller.submitForm('#form_reset_password');
	return false;
});

$('#form_reset_password_field_password').keyup(function() {
	reset_password_submit_button();
});

$('#form_reset_password_field_verify_password').keyup(function() {
	reset_password_submit_button();
});

function reset_password_submit_button()
{
		if ($('#form_reset_password_field_password').valid())		
			if ($('#form_reset_password_field_verify_password').valid())
            {				
                $('#form_reset_password_submit_button').removeAttr('disabled');
                $('#form_reset_password_submit_button').removeClass('disabled');
            }

}


/*

$("#form_reset_password_submit_button").click(function (event){
	controller.submitForm('#form_reset_password');
});
*/

$("#reset_password_cancel").click(function (){
	jQuery.fancybox.close();
});