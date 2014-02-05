
$('#form_trouble_signing_in').validate({
	messages: {
		email: 'You must enter a valid email address. For example, myname@mycompany.com.'
	}
});


$('#form_trouble_signing_in_submit_button').click(function(event) {
	return controller.submitHandler(event);
});

$("#form_trouble_signing_in").submit(function (event){
	return controller.submitHandler(event);
})

$('#trouble_signing_in_cancel').click(function(event) {
	jQuery.fancybox.close();
    return false;
});

$('#form_trouble_signing_in_field_email').keyup(function() {
	controller.validateFormAndActivateSubmit('#form_trouble_signing_in', '#form_trouble_signing_in_submit_button');
});

$('#trouble_signing_in_close').click(function(event) {
	jQuery.fancybox.close();
    return false;
});

//initialize forms and buttons
controller.setUpFormSubmit('#form_trouble_signing_in', '#form_trouble_signing_in_submit_button');