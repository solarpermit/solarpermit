{% include 'website/form_fields/file_uploading.js' %}    

$('#field_form_option_link_{{unique_key}}').click(function(event) {
    $target = $(event.target);
	if ($('#field_form_option_link_{{unique_key}}').is(':checked')) 
    {
        $('#form_option_link_{{unique_key}}').show();
        $('#form_option_upload_{{unique_key}}').hide(); 
        
        if ($('#save_{{question_id}}').length > 0)
        	controller.disableButton('#save_{{question_id}}');      
        else
        	controller.disableButton('#save_edit_{{answer_id}}');           
    }

});

$('#field_form_option_upload_{{unique_key}}').click(function(event) {
    $target = $(event.target);
	if ($('#field_form_option_upload_{{unique_key}}').is(':checked')) 
    {   
        $('#form_option_upload_{{unique_key}}').show();
        $('#form_option_link_{{unique_key}}').hide();     
        
        if ($('#save_{{question_id}}').length > 0)
        	controller.disableButton('#save_{{question_id}}');      
        else
        	controller.disableButton('#save_edit_{{answer_id}}');                
    }

});

$('#field_link_1_{{unique_key}}').keyup(function(event) {
	// validate the url

    var $control = $(event.target);
    urlVal = $control.val().substring(0, $control.val().length);
    if (urlVal != 'h' && urlVal != 'ht' && urlVal != 'htt' && urlVal != 'http' && urlVal != 'http:' && urlVal != 'http:/' && urlVal != 'http://')
    {	//alert('validate');
    	var $form = $control.closest('form');	
		controller.processUrlField('field_link_1_{{unique_key}}');	
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
});


function validateLinkOrFile(add)
{
	var pass = true;
	
		if ($('#field_form_option_link_{{unique_key}}').is(':checked'))
		{
			controller.processUrlField('field_link_1_{{unique_key}}');	
			$('#filename').val('');
			$('#file_store_name').val('');
		}
		else
			if ($('#field_form_option_upload_{{unique_key}}').is(':checked'))
			{	
				if (add || $('#has_file_{{answer_id}}').val() != 'Y')
					return isFileUploaded();
			}

	return pass;
}