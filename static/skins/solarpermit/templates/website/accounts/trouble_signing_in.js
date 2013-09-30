{% include 'website/form_fields/common_form_utils.js' %}

$('#form_trouble_signing_in').validate({
	messages: {
		email: 'You must enter a valid email address. For example, myname@mycompany.com.'
	}
});

$('#form_trouble_signing_in_submit_button').click(function (event)
{
	return submitHandler(event);
});


$('#form_trouble_signing_in_field_email').keyup(
	function(){
		if ($('#form_trouble_signing_in_field_email').valid()) {
			$('#form_trouble_signing_in_submit_button').removeAttr('disabled');
			$('#form_trouble_signing_in_submit_button').removeClass('disabled');
		}
	}
);

$("#form_trouble_signing_in").submit(function (event){
	controller.submitForm('#form_trouble_signing_in');
	return false;
})
/*
$('#form_trouble_signing_in_submit_button').click(
	function (event){
		obj = document.getElementById('form_trouble_signing_in_field_email');
		if( obj.value === '' || !validateEmail(obj.value)){
        document.getElementById('msg_form_trouble_signing_in_field_email').innerHTML="You must enter a valid email address. For example, myname@mycompany.com.";
        return false;
    }else
        document.getElementById('msg_form_trouble_signing_in_field_email').innerHTML='';
		controller.submitForm('#form_trouble_signing_in');
		$('#form_trouble_signing_in_submit_button').attr('disabled', 'disabled');
		$('#form_trouble_signing_in_submit_button').addClass('disabled');
		return false;
	}
);
*/

$("#trouble_signing_in_cancel").click(function (){
	jQuery.fancybox.close();
});
