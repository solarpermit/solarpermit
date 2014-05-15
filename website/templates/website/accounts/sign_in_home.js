	$("#trouble_signing_in_a").click(function (){
		controller.postRequest('/account/', {ajax: 'trouble_signing_in'}); return false;
	});
	
	
	$("#form_sign_in_submit_button").click(function (){
        {% if FORUM_INTEGRATION == True %}
        controller.lssLogin();    
        {% else %}
		controller.submitForm('#form_sign_in');        
        {% endif %}
		return false;
	});