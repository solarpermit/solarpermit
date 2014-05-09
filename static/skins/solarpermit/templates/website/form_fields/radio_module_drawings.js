
{% include 'website/form_fields/link_or_file.js' %}    

controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

if ($('#save_{{question_id}}').length > 0)
	controller.activateButton('#save_{{question_id}}');      
else
	controller.activateButton('#save_edit_{{answer_id}}'); 
	
$('#field_value_draw_{{question_id}}').click(function(event) {
    $target = $(event.target);
	if ($('#field_value_draw_{{question_id}}').is(':checked')) 
    {
        $('#link_or_file_{{question_id}}').show();
        if ($('#save_{{question_id}}').length > 0)
        	controller.disableButton('#save_{{question_id}}');      
        else
        	controller.disableButton('#save_edit_{{answer_id}}');          
    }

});

$('#field_value_series_{{question_id}}').click(function(event) {
    $target = $(event.target);
	if ($('#field_value_series_{{question_id}}').is(':checked')) 
    {
        $('#link_or_file_{{question_id}}').hide();    
        if ($('#save_{{question_id}}').length > 0)
        	controller.activateButton('#save_{{question_id}}');      
        else
        	controller.activateButton('#save_edit_{{answer_id}}');             
    }

});    


var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if (++submitCount_q_{{question_id}} == 1)
	{	
		if ($('#field_value_draw_{{question_id}}').is(':checked')) 
			success = validateLinkOrFile(true);
		else
			success = true;
				
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
		if ($('#field_value_draw_{{question_id}}').is(':checked')) 
			success = validateLinkOrFile(false);
		else
			success = true;
			
		if (success)
			success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
		else
			submitCount_a_{{answer_id}} = 0;
	}
	
	return false;
});