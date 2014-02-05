controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if($('#field_disclose_communication_64').is(':checked') == false && $('#field_disclose_issue_64').is(':checked') == false)	
		$('#error_div_homeowner_req').html('At least one option is required.');
	else
		if (++submitCount_q_{{question_id}} == 1)
		{	
			var success = controller.submitHandler(event, submitCount_q_{{question_id}});	
			if (success == false)
				submitCount_q_{{question_id}} = 0;
		}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	if($('#field_disclose_communication_64').is(':checked') == false && $('#field_disclose_issue_64').is(':checked') == false)	
		$('#error_div_homeowner_req').html('At least one option is required.');
	else
		if (++submitCount_a_{{answer_id}} == 1)
		{
			var success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
			if (success == false)
				submitCount_a_{{answer_id}} = 0;
		}
	
	return false;
});