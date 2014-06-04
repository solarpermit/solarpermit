(function($){    
    $.fn.silder = function(settings){    
        settings = jQuery.extend({
        	speed : "normal",
			slideBy : 2
    	}, settings);
		return this.each(function() {
		$.fn.silder.run( $( this ), settings );
    });
    }; 
	   
    $.fn.silder.run=function($this, settings){
		var ul = $( "ul:eq(0)", $this );
		var li = ul.children();
		if(li.length > settings.slideBy){
			var $next = $( ".next > a", $this );
			var $back = $( ".back > a", $this );
			var liWidth = $( li[0] ).outerWidth(true);
			var animating = false;
			ul.css( "width", liWidth* li.length);
			var Next = $next.click(function() {
				if(!animating){
					animating=true;
					offsetLeft = parseInt(ul.css("left"))-(liWidth* settings.slideBy);
					if ( offsetLeft + ul.width() > 0 ){
						$back.css( "display", "block" );
						ul.animate({left:offsetLeft},settings.speed,function(){
							if ( parseInt( ul.css( "left" ) ) + ul.width() <= liWidth * settings.slideBy ) {
								$next.css( "display", "none" );
							}
							animating = false;
						});
					}
				}
				return false;
			});
			var Back = $back.click(function() {
				if(!animating){
					animating=true;
					offsetRight = parseInt(ul.css("left"))+(liWidth * settings.slideBy);
					if ( offsetLeft + ul.width() <= ul.width() ){
						$next.css( "display", "block" );
						ul.animate({left:offsetRight},settings.speed,function(){
							if ( parseInt( ul.css( "left" ) ) ==0) {
								$back.css( "display", "none" );
							}
							animating = false;
						});
					}
				}
				return false;
			});	
		};
	}; 
})(jQuery);


$( "#attachement_slider" ).silder({
speed : "normal",
slideBy : 3
}); 

$(".attachement_save").click(function (){
	answerid = $(this).data('answerid');
	return controller.submitForm('#attach-form');
});

$(".attachement_cancel").click(function(){
	answerid = $(this).data('answerid');
	$('#qa_'+answerid+'_attachements').hide('slow');
});

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

