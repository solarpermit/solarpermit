{% include 'website/form_fields/common_form_utils.js' %}



$('#save_{{question_id}}').click(function(event) 
{
	if($('#field_mail_{{question_id}}').is(':checked') == false) 
		if($('#field_email_{{question_id}}').is(':checked') == false)	
			if($('#field_onsite_{{question_id}}').is(':checked') == false)	
				$('#error_div_{{question_id}}').html('At least one option is required.');
			else 
				return submitHandler(event);			
		else 
			return submitHandler(event);
	else
		return submitHandler(event);
		
	return false;

});

$('#save_edit_{{answer_id}}').click(function(event) 
{
	if($('#field_mail_{{question_id}}').is(':checked') == false) 
		if($('#field_email_{{question_id}}').is(':checked') == false)	
			if($('#field_onsite_{{question_id}}').is(':checked') == false)	
				$('#error_div_{{question_id}}').html('At least one option is required.');
			else 
				return submitHandler(event);			
		else 
			return submitHandler(event);
	else
		return submitHandler(event);
		
	return false;

});
