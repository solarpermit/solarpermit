
$("#ahj_message_close").click(function (){
	jQuery.fancybox.close();
});

$('#register').click(function() {
	jQuery.fancybox.close();
    controller.postRequest('/account/', {ajax: 'create_account'}); 
    return false;
});