$(document).ready(function() {
	$("#create_account_a").click(function (){
		controller.postRequest('/account/', {ajax: 'create_account'}); 
		return false;
	});
	
	
	$("#form_sign_in_submit_button").click(function (){
		controller.submitForm('#form_sign_in');
		return false;
	});
    
	$("#trouble_signing_in").click(function (){
		controller.postRequest('/account/', {ajax: 'trouble_signing_in'});
		return false;
	});    
});