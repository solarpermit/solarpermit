{% include 'website/form_fields/common_form_utils.js' %}

$('#save_{{question_id}}').click(function(event) {
	return submitHandler(event);
});

$('#save_edit_{{answer_id}}').click(function(event) {
	return submitHandler(event);
});
