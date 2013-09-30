//for IE8 fix, prevent form with ajax from submitting normally after validation
/*
$('input[name="ajax"]').closest('form').each(function () {
	$(this).submit( function( event ) {
		event.preventDefault();
	});
});
*/
{% include 'website/form_fields/common_form_utils.js' %}

$('#field_allowed_no_{{question_id}}').click(function(event) { 

    $('#yes_with_exceptions_{{question_id}}').hide();

});

$('#field_allowed_yes_{{question_id}}').click(function(event) { 

    $('#yes_with_exceptions_{{question_id}}').hide();

});


$('#field_allowed_yes_with_exception_{{question_id}}').click(function(event) {

    $('#yes_with_exceptions_{{question_id}}').show();

});

$('#field_depends_on_system_rating_{{question_id}}').click(function(event) {

	if ($('#field_depends_on_system_rating_{{question_id}}').is(':checked')) 
        $('#system_rating_method_{{question_id}}').show();
    else
        $('#system_rating_method_{{question_id}}').hide();
          

});


$('#save_{{question_id}}').click(function(event) {
	$target = $(event.target);
	
    return submitHandler(event);
});

$('#save_edit_{{answer_id}}').click(function(event) {
	$target = $(event.target);
	
	
	return submitHandler(event);
});