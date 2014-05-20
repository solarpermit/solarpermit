		var uploader_input = document.getElementById("file-uploader_{{unique_key}}");
    if (uploader_input != null) {
        var uploader = new qq.FileUploader(
            {
                element: document.getElementById("file-uploader_{{unique_key}}"),
                action: "/jurisdiction/answer_uploadfile/",
                customHeaders: {"X-CSRFToken": js_csrf },
                debug: true,
                multiple: false,
                uploadButtonText: "Select File to Attach",
                onComplete: function(id, fileName, response) {
                                if (response.error){
                                		$(".qq-upload-failed-text").html(response.error);
                                    	$("#filename_{{unique_key}}").val('');
                                    	onFailed();
                                    return;
                                } else {
                                		if ($("#filename_{{unique_key}}").val() == ''){
                                			$("#filename_{{unique_key}}").val(response.fileName);
                                		} else {
                                			fileName1 = $("#filename_{{unique_key}}").val() + ','+ response.fileName;
                                			$("#filename_{{unique_key}}").val(fileName1);
                                		}
	                                  if ($("#file_store_name_{{unique_key}}").val() == ''){
                                			$("#file_store_name_{{unique_key}}").val(response.store_name);
                                		} else {
                                			file_store_name1 = $("#file_store_name_{{unique_key}}").val() + ','+ response.store_name;
                                			$("#file_store_name_{{unique_key}}").val(file_store_name1);
                                		} 
                                    if($("#error_message").is(":visible"))     $("#error_message").hide();
                                    //$("#file_store_name").val(response.store_name);
                                    $('#file_validation_error_{{unique_key}}').html('');
                                    onPassed();
                                }
                            },
                            params: {
                                'csrfmiddlewaretoken': js_csrf,
                              }
        });
    }
    
    
function isFileUploaded() {
	if ($("#filename_{{unique_key}}").val() == '')
	{	
		$('#file_validation_error_{{unique_key}}').html('Please upload a pdf file.');
		return false;
	}
	else
		return true;
}    

function onFailed()
{
	if ($("#filename_{{unique_key}}").val() == '')
	{	
		$('#file_validation_error_{{unique_key}}').html('Please upload a pdf file.');
	}
	
        if ($('#save_{{question_id}}').length > 0)
        	controller.disableButton('#save_{{question_id}}');      
        else
        	controller.disableButton('#save_edit_{{answer_id}}');  
}

function onPassed()
{
	if ($("#filename_{{unique_key}}").val() != '')
	{	
		$('#file_validation_error_{{unique_key}}').html('');
	}
	
        if ($('#save_{{question_id}}').length > 0)
        	controller.activateButton('#save_{{question_id}}');      
        else
        	controller.activateButton('#save_edit_{{answer_id}}');  
}