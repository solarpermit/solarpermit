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

$('#field_required_no_{{question_id}}').click(function(event) { 

    $('#no_{{question_id}}').show();   
    $('#yes_with_exceptions_{{question_id}}').hide();
    if ($('#save_{{question_id}}').length > 0)
    	controller.activateButton('#save_{{question_id}}');      
   	else
       	controller.activateButton('#save_edit_{{answer_id}}');
});

$('#field_required_yes_{{question_id}}').click(function(event) {

    $('#no_{{question_id}}').hide();   
    $('#yes_with_exceptions_{{question_id}}').hide();
    if ($('#save_{{question_id}}').length > 0)
    	controller.activateButton('#save_{{question_id}}');      
   	else
       	controller.activateButton('#save_edit_{{answer_id}}');
});

$('#field_required_yes_with_exception_{{question_id}}').click(function(event) {

    $('#no_{{question_id}}').hide();    
    $('#yes_with_exceptions_{{question_id}}').show();
    if ($('#save_{{question_id}}').length > 0)
    	controller.activateButton('#save_{{question_id}}');      
   	else
       	controller.activateButton('#save_edit_{{answer_id}}');
});

$('#field_depends_on_system_rating_{{question_id}}').click(function(event) {

	if ($('#field_depends_on_system_rating_{{question_id}}').is(':checked')) 
        $('#system_rating_method_{{question_id}}').show();
    else
        $('#system_rating_method_{{question_id}}').hide();
          

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