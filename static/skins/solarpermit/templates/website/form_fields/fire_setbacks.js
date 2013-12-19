controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');
var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	current_submit_count = submitCount_q_{{question_id}};
	submitCount_q_{{question_id}}++;
	if (current_submit_count == 0)
	{
		var success = controller.submitHandler(event, current_submit_count);	
		if (success == false)
			submitCount_q_{{question_id}} = 0;
	}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	current_submit_count = submitCount_a_{{answer_id}};
	submitCount_a_{{answer_id}}++;
	if (current_submit_count == 0)
	{
		var success = controller.submitHandler(event, current_submit_count);	
		if (success == false)
			submitCount_a_{{answer_id}} = 0;
	}
	
	return false;
});



$('#field_enforced_no_{{question_id}}').click(function(event) { 

    $('#yes_with_exceptions_{{question_id}}').hide();
    $('#field_note_{{question_id}}').val('');
        
});

$('#field_enforced_yes_{{question_id}}').click(function(event) { 

    $('#yes_with_exceptions_{{question_id}}').hide();
    $('#field_note_{{question_id}}').val('');        
});

$('#field_enforced_yes_with_exception_{{question_id}}').click(function(event) { 

    $('#yes_with_exceptions_{{question_id}}').show();
        
});