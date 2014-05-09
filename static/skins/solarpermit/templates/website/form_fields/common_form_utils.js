

//initialize forms and buttons
controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

/* MOVED TO CONTROLLER */
/*
function processUrlField(id) {
	var value = $('#'+id).val();
	value = controller.urlValidScheme(value);
	$('#'+id).val(value);
	$('#'+id).addClass('url');
}

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
		$button.closest('.suggestion_edit_box').hide('slow');
		controller.submitForm('#'+$form.attr('id'));
	} else {
		$button.removeAttr('disabled');
	}
	return false;
}

*/