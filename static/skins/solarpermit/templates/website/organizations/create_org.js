$(document).ready(function() {
	alert(js_csrf);
    var uploader_input = document.getElementById("file-uploader");
    if (uploader_input != null) {
        var uploader = new qq.FileUploader(
            {
                element: document.getElementById("file-uploader"),
                action: "/organization/logo/org_uploadfile/",
                customHeaders: {"X-CSRFToken": js_csrf },
                debug: true,
                multiple: false,
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

});

function create_org_update_buttons() {

	if ($('#{{form_create_org_id}}').valid()) {
		$('#{{form_create_org_id}}_submit_button').removeClass('disabled');
				return;
	}
		
	$('#{{form_create_org_id}}_submit_button').addClass('disabled');
}
