{% include 'website/form_fields/common_form_utils.js' %}



$('#save_{{question_id}}').click(function(event) 
{
	var value = $('#'+'id_3').val();
	value = controller.urlValidScheme(value);
	$('#'+'id_3').val(value);
	$('#'+'id_3').addClass('url');
	return submitHandler(event);
	
});

$('#save_edit_{{answer_id}}').click(function(event) 
{
	var value = $('#'+'id_3').val();
	
	value = urlValidScheme(value);
	$('#'+'id_3').val(value);
	$('#'+'id_3').addClass('url');
	return submitHandler(event);

});

function encode(url) {
    url = url.replace(/!/g, '%21')
    url = url.replace(/'/g, '%27')
    url = url.replace(/\(/g, '%28')
    url = url.replace(/\)/g, '%29')
    url = url.replace(/\*/g, '%2A')
    url = url.replace(/\{/g, '%7B')
    url = url.replace(/\}/g, '%7D')
    url = url.replace(/\</g, '%3C')
    url = url.replace(/\>/g, '%3E');    
        
    /*
    	# % & * { } \ : < > ? / +
    */
    
    return url
}
