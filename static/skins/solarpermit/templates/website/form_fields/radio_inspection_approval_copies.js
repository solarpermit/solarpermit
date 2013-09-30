{% include 'website/form_fields/common_form_utils.js' %}

$('#field_apply_in_person_{{question_id}}').click(function(event) { 
	//$('#field_scale_any_{{question_id}}').attr('checked', true);
	//$('#field_scale_specific_{{question_id}}').removeAttr('checked');	

    $('#remotely_{{question_id}}').hide();
        
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

$('#save_{{question_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});

$('#save_edit_{{answer_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});
