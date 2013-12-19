

$('#{{form_id}}_submit_button').click(function(event) {
	return controller.submitHandler(event);
});

$('#cancel_feedback').click(function(event) {
	jQuery.fancybox.close();
    return false;
});

$('#{{form_id}}_field_feedback').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

$('#{{form_id}}_firstname').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

$('#{{form_id}}_lastname').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

$('#{{form_id}}_email').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

$('#{{form_id}}_title').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

$('#{{form_id}}_org').keyup(function() {
	controller.validateFormAndActivateSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
});

/*
function validateForm(formId)
{   
    return $(formId).validate().form();

}
*/

/*
//set up ajax form submit, includes IE8 fix
function setUpFormSubmit(form_selector, button_selector) {
	$(button_selector).removeAttr('disabled');
	$(button_selector).unbind('click');
	$(form_selector).removeAttr('onsubmit'); //remove previous inline script, not needed
	$(form_selector).unbind('submit');
	$(form_selector).submit(function (event) {
		var $button = $(button_selector);
		var $form = $(form_selector);
		event.preventDefault(); //prevent non-ajax form post in IE8
		return submitActions($form, $button);
	});
}
    
function submitHandler(event) {
	var $button = $(event.target);
	var $form = $button.closest('form');
	event.preventDefault();
	return submitActions($form, $button);
}

function submitActions($form, $button) {
	$button.attr('disabled','disabled');
	if ($form.validate().form()) {
		controller.submitForm('#'+$form.attr('id'));
	} else {
		$button.removeAttr('disabled');
	}
	return false;
}
*/


//initialize forms and buttons
controller.setUpFormSubmit('#{{form_id}}', '#{{form_id}}_submit_button');
