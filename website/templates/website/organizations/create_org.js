$(document).ready(function() {
    var uploader_input = document.getElementById("file-uploader");
    if (uploader_input != null) {
        var uploader = new qq.FileUploader(
            {
                element: document.getElementById("file-uploader"),
                action: "/organization/logo/org_uploadfile/",
                debug: true,
                multiple: false,
                customHeaders: {"X-CSRFToken": js_csrf },
                uploadButtonText: "Upload Logo",
                onComplete: function(id, fileName, response) {
                                if (response.error){                            
                                		$(".qq-upload-failed-text").html(response.error);
                                    $("#filename").val();
                                    return;
                                } else {                                		
                                    $("#filename").val(fileName);
                                    $("#id_logo").val(fileName).trigger("change");
                                    if($("#error_message").is(":visible"))     $("#error_message").hide();
                                    $("#file_store_name").val(response.store_name);
                                    $("#thum_logo").empty().append("<img src='"+response.thum_path+"' alt='logo' >");
                                }
                            },
                            params: {
                                'csrfmiddlewaretoken': js_csrf,
              }
        });
    }



	//initialize forms and buttons
	controller.setUpFormSubmit('#{{form_create_org_id}}', '#{{form_create_org_id}}_submit_button');
	
	var submitCount = 0;
	
	$('#{{form_create_org_id}}_submit_button').click(function(event) {
		if (++submitCount == 1)
		{	
			controller.processUrlField('{{form_create_org_id}}_field_website');	
			var success = controller.submitHandler(event, submitCount);	
			if (success == false)
			{
				submitCount = 0;
			}
		}
	
		return false;
	});	

	$('#{{form_create_org_id}}_field_name').keyup(function() {
		controller.validateFormAndActivateSubmit('#{{form_create_org_id}}', '#{{form_create_org_id}}_submit_button');
	});

	$('#{{form_create_org_id}}_field_website').keyup(function() {
		controller.validateFormAndActivateSubmit('#{{form_create_org_id}}', '#{{form_create_org_id}}_submit_button');
	});
	
	$('#create_org_cancel').click(function(event) {
		controller.postRequest('/organization/', {ajax: 'open_choose_org'}); 
	    return false;
	});
	
	
	
	$('.modal_dialog_close a').click(function () {
		controller.postRequest('/organization/', {ajax: 'open_choose_org'});
		return false;
	});
	
	$('#open_choose_org').click(function() {
		$target = $(event.target);
		controller.postRequest('/organization/', {ajax: 'open_choose_org'});
		return false;
					
	});		
	
	$('#create_org_cancel').click(function() {
		$target = $(event.target);
		controller.postRequest('/organization/', {ajax: 'open_choose_org'});
		return false;
					
	});		

});

function create_org_update_buttons() {
		if ($('#{{form_create_org_id}}').validate().form()) {
			$('#{{form_create_org_id}}_submit_button').removeClass('disabled');
					return;
		}
		else {
			$('#{{form_create_org_id}}_submit_button').addClass('disabled');
		}

	
}

/*

  
	$('#{{form_create_org_id}}_field_name').blur(function() {
		create_org_update_buttons();
	});
	
	$('#{{form_create_org_id}}_field_website').blur(function() {
		create_org_update_buttons();
	});      
	
	$('#{{form_create_org_id}}_submit_button').click(function(event) {
		$target = $(event.target);
		if (!$target.hasClass('disabled')) {
			if ($('#{{form_create_org_id}}').valid()) {
				controller.submitForm('#{{form_create_org_id}}');
				$('#{{form_create_org_id}}_submit_button').hide();	
				$('#{{form_create_org_id}}_submit_button').attr("disabled", true);	
			}
		}
		return false;
	});	
	
	$('.modal_dialog_close a').click(function () {
		controller.postRequest('/organization/', {ajax: 'open_choose_org'});
		return false;
	});
	
	$('#form_create_org').submit(function() {
		return controller.submitForm('#form_create_org');
	});
	
	$('#create_org_cancel').click(function() {
		controller.postRequest('/organization/', {ajax: 'open_choose_org'}); 
		return false;
	});

});

function create_org_update_buttons() {
	if ($('#{{form_create_org_id}}_field_name').val() != '' && $('#{{form_create_org_id}}_field_website').val() != '') {
	//if ($('#{{form_create_org_id}}').valid()) {
		$('#{{form_create_org_id}}_submit_button').removeClass('disabled');
				return;
	}
		
	$('#{{form_create_org_id}}_submit_button').addClass('disabled');
}

*/