$(".org_settings_close a").click(function (){
	$.fancybox.close();
	return false;
});

$("#setting_submit_button").click(function (){
	controller.submitForm('#form_notification_setting'); 
	return false;
});

$("#setting_org_cancel").click(function (){
	jQuery.fancybox.close(); 
	return false;
});