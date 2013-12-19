
{% include 'website/form_fields/link_or_file.js' %}    

controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');
var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if (++submitCount_q_{{question_id}} == 1)
	{	//alert('submit');
		var success = validateLinkOrFile(true);
			
		if (success)
			success = controller.submitHandler(event, submitCount_q_{{question_id}});	
		else
			submitCount_q_{{question_id}} = 0;
	}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	if (++submitCount_a_{{answer_id}} == 1)
	{
		var success = validateLinkOrFile(false);
			
		if (success)
			success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
		else
			submitCount_a_{{answer_id}} = 0;
	}
	
	return false;
});


