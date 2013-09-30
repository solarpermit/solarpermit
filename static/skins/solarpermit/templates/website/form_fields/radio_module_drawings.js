		var uploader_input = document.getElementById("file-uploader");
    if (uploader_input != null) {
        var uploader = new qq.FileUploader(
            {
                element: document.getElementById("file-uploader"),
                action: "/jurisdiction/answer_uploadfile/",
                customHeaders: {"X-CSRFToken": js_csrf },
                debug: true,
                multiple: true,
                uploadButtonText: "Select File to Attach",
                onComplete: function(id, fileName, response) {
                                if (response.error){
                                		$(".qq-upload-failed-text").html(response.error);
                                    //$("#filename").val();
                                    return;
                                } else {
                                		if ($("#filename").val() == ''){
                                			$("#filename").val(fileName);
                                		} else {
                                			fileName1 = $("#filename").val() + ','+ fileName;
                                			$("#filename").val(fileName1);
                                		}
	                                  if ($("#file_store_name").val() == ''){
                                			$("#file_store_name").val(response.store_name);
                                		} else {
                                			file_store_name1 = $("#file_store_name").val() + ','+ response.store_name;
                                			$("#file_store_name").val(file_store_name1);
                                		} 
                                    if($("#error_message").is(":visible"))     $("#error_message").hide();
                                    //$("#file_store_name").val(response.store_name);
                                }
                            },
                            params: {
                                'csrfmiddlewaretoken': js_csrf,
                              }
        });
    }