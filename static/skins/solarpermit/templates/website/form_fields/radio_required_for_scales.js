//for IE8 fix, prevent form with ajax from submitting normally after validation
/*
$('input[name="ajax"]').closest('form').each(function () {
	$(this).submit( function( event ) {
		event.preventDefault();
	});
});
*/
{% include 'website/form_fields/common_form_utils.js' %}

$('#field_scale_any_{{question_id}}').click(function(event) { 
	//$('#field_scale_any_{{question_id}}').attr('checked', true);
	//$('#field_scale_specific_{{question_id}}').removeAttr('checked');	

    $('#specific_{{question_id}}').hide();
        
    //return false;
});

$('#field_scale_specific_{{question_id}}').click(function(event) {
	//$('#field_scale_specific_{{question_id}}').attr('checked', true);
	//$('#field_scale_any_{{question_id}}').removeAttr('checked');	

    $('#specific_{{question_id}}').show();
    
    //return false;
});

$('#field_scale_factor_other_{{question_id}}').click(function(event) {
    $target = $(event.target);

	if ($('#field_scale_factor_other_{{question_id}}').is(':checked')) 
        $('#other_{{question_id}}').show();
    else
        $('#other_{{question_id}}').hide();       

});

$('#save_{{question_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});

$('#save_edit_{{answer_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});
