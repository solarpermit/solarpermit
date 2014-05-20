controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) 
{
	if (++submitCount_a_{{answer_id}} == 1)
	{
		var success = false;
		if($('#field_mail_{{question_id}}').is(':checked') == false && $('#field_email_{{question_id}}').is(':checked') == false && $('#field_onsite_{{question_id}}').is(':checked') == false)	
			$('#error_div_{{question_id}}').html('At least one option is required.');
		else
			success = controller.submitHandler(event, submitCount_q_{{question_id}});
		
		if (success == false)
			submitCount_q_{{question_id}} = 0;	
	}

});

$('#save_edit_{{answer_id}}').click(function(event) 
{
	if (++submitCount_a_{{answer_id}} == 1)
	{
		var success = false;	
		if($('#field_mail_{{question_id}}').is(':checked') == false && $('#field_email_{{question_id}}').is(':checked') == false && $('#field_onsite_{{question_id}}').is(':checked') == false)	
			$('#error_div_{{question_id}}').html('At least one option is required.');
		else
			success = controller.submitHandler(event, submitCount_q_{{question_id}});
			
		if (success == false)
			submitCount_a_{{answer_id}} = 0;
	}

});   