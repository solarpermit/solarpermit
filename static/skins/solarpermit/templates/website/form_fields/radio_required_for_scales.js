//for IE8 fix, prevent form with ajax from submitting normally after validation
/*
$('input[name="ajax"]').closest('form').each(function () {
	$(this).submit( function( event ) {
		event.preventDefault();
	});
});
*/

controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');


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