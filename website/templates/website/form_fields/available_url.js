controller.setUpFormSubmit('#form_{{question_id}}', '#save_{{question_id}}');
controller.setUpFormSubmit('#form_edit_{{answer_id}}', '#save_edit_{{answer_id}}');

var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

if ($('#save_{{question_id}}').length > 0)
	controller.activateButton('#save_{{question_id}}');      
else
	controller.activateButton('#save_edit_{{answer_id}}'); 

$('#field_available_no_{{question_id}}').click(function(event) {
	if ($('#field_available_no_{{question_id}}').is(':checked')) 
    {
        $('#available_{{question_id}}').hide();
        if ($('#save_{{question_id}}').length > 0)
        	controller.activateButton('#save_{{question_id}}');      
        else
        	controller.activateButton('#save_edit_{{answer_id}}');            
    }

});

$('#field_available_yes_{{question_id}}').click(function(event) {
	if ($('#field_available_yes_{{question_id}}').is(':checked')) 
    {
        $('#available_{{question_id}}').show(); 
        if ($('#save_{{question_id}}').length > 0)
        	controller.disableButton('#save_{{question_id}}');      
        else
        	controller.disableButton('#save_edit_{{answer_id}}');       
    }

});    

$('#field_url_{{question_id}}').keyup(function(event) {
	// validate the url
	//alert('validate');
    var $control = $(event.target);
    urlVal = $control.val().substring(0, $control.val().length);
    if (urlVal != 'h' && urlVal != 'ht' && urlVal != 'htt' && urlVal != 'http' && urlVal != 'http:' && urlVal != 'http:/' && urlVal != 'http://')
    {	//alert('validate');
    	var $form = $control.closest('form');	
		controller.processUrlField('field_url_{{question_id}}');	
		if ($form.validate().form())
	        if ($('#save_{{question_id}}').length > 0)
	        	controller.activateButton('#save_{{question_id}}');      
	        else
	        	controller.activateButton('#save_edit_{{answer_id}}');   
	    else
	        if ($('#save_{{question_id}}').length > 0)
	        	controller.disableButton('#save_{{question_id}}');      
	        else
	        	controller.disableButton('#save_edit_{{answer_id}}');  	    			
	}
	
	return false;
});
   
var submitCount_q_{{question_id}} = 0;
var submitCount_a_{{answer_id}} = 0;

$('#save_{{question_id}}').click(function(event) {
	if (++submitCount_q_{{question_id}} == 1)
	{	
		if ($('#field_available_yes_{{question_id}}').is(':checked')) 
			controller.processUrlField('field_url_{{question_id}}');
		else
			$('#field_url_{{question_id}}').val('');
				
		var success = controller.submitHandler(event, submitCount_q_{{question_id}});	
		if (success == false)
		{
			//alert('success = false');
			submitCount_q_{{question_id}} = 0;
		}
	}

	return false;
});

$('#save_edit_{{answer_id}}').click(function(event) {
	if (++submitCount_a_{{answer_id}} == 1)
	{
		if ($('#field_available_yes_{{question_id}}').is(':checked')) 
			controller.processUrlField('field_url_{{question_id}}');
		else
			$('#field_url_{{question_id}}').val('');
			
		var success = controller.submitHandler(event, submitCount_a_{{answer_id}});	
		if (success == false)
			submitCount_a_{{answer_id}} = 0;
	}
	
	return false;
});

