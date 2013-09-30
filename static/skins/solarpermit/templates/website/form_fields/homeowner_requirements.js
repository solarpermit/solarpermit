{% include 'website/form_fields/common_form_utils.js' %}



$('#save_{{question_id}}').click(function(event) 
{
	if($('#field_disclose_communication_64').is(':checked') == false) 
		if($('#field_disclose_issue_64').is(':checked') == false)	
			$('#error_div_homeowner_req').html('At least one option is required.');
		else 
			return submitHandler(event);
	else
		return submitHandler(event);
		
	return false;

});

$('#save_edit_{{answer_id}}').click(function(event) 
{
	if($('#field_disclose_communication_64').is(':checked') == false) 
		if($('#field_disclose_issue_64').is(':checked') == false)	
			$('#error_div_homeowner_req').html('At least one option is required.');
		else 
			return submitHandler(event);
	else
		return submitHandler(event);
		
	return false;

});
