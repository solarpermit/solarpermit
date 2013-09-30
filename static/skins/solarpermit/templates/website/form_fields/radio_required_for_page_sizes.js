//for IE8 fix, prevent form with ajax from submitting normally after validation
/*
$('input[name="ajax"]').closest('form').each(function () {
	$(this).submit( function( event ) {
		event.preventDefault();
	});
});
*/
{% include 'website/form_fields/common_form_utils.js' %}

$('#field_required_no_{{question_id}}').click(function(event) { 
	//$('#field_required_no_{{question_id}}').attr('checked', true);
	//$('#field_required_yes_{{question_id}}').removeAttr('checked');	

    $('#yes_{{question_id}}').hide();
        
});

$('#field_required_yes_{{question_id}}').click(function(event) {
	//$('#field_required_yes_{{question_id}}').attr('checked', true);
	//$('#field_required_no_{{question_id}}').removeAttr('checked');	

    $('#yes_{{question_id}}').show();
    //return false;
});

$('#field_size_{{question_id}}').change(function(event) {
    if ($('#field_size_{{question_id}}').val() == 'other')
        $('#other_{{question_id}}').show();
    else
        $('#other_{{question_id}}').hide();

    return false;
});


$('#save_{{question_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});

$('#save_edit_{{answer_id}}').click(function(event) {
	$target = $(event.target);
    
	return submitHandler(event);
});
