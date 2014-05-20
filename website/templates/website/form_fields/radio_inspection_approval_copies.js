controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

if ($('#save_{{question_id}}').length > 0)
	controller.activateButton('#save_{{question_id}}');      
else
	controller.activateButton('#save_edit_{{answer_id}}'); 
	
$('#field_apply_in_person_{{question_id}}').click(function(event) { 
	//$('#field_scale_any_{{question_id}}').attr('checked', true);
	//$('#field_scale_specific_{{question_id}}').removeAttr('checked');	

    $('#remotely_{{question_id}}').hide();
    if ($('#save_{{question_id}}').length > 0)
    	controller.activateButton('#save_{{question_id}}');      
   	else
       	controller.activateButton('#save_edit_{{answer_id}}');          
    //return false;
});

$('#field_apply_remotely_{{question_id}}').click(function(event) {
	//$('#field_scale_specific_{{question_id}}').attr('checked', true);
	//$('#field_scale_any_{{question_id}}').removeAttr('checked');	

    $('#remotely_{{question_id}}').show();
    
    //return false;
});

$('#field_request_by_phone_{{question_id}}').click(function(event) {
	if ($('#field_request_by_phone_{{question_id}}').is(':checked')) 
        $('#phone_{{question_id}}').show();
    else
        $('#phone_{{question_id}}').hide();

});

$('#field_request_by_fax_{{question_id}}').click(function(event) {
	if ($('#field_request_by_fax_{{question_id}}').is(':checked')) 
        $('#fax_{{question_id}}').show();
    else
        $('#fax_{{question_id}}').hide();

});

$('#field_request_by_email_{{question_id}}').click(function(event) {
	if ($('#field_request_by_email_{{question_id}}').is(':checked')) 
        $('#email_{{question_id}}').show();
    else
        $('#email_{{question_id}}').hide();

});

var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if (++submitCount_q_{{question_id}} == 1)
	{	
		var success = controller.submitHandler(event, submitCount_q_{{question_id}});	
		if (success == false)
			submitCount_q_{{question_id}} = 0;
	}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	if (++submitCount_a_{{answer_id}} == 1)
	{
		var success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
		if (success == false)
			submitCount_a_{{answer_id}} = 0;
	}
	
	return false;
});
