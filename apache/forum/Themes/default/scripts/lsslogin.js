$.lsslogin = {
	solarurl: 'http://solarpermit.org/'
};
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
$.lsslogin.doLogin = function(formSelector)
{
		var user, pass, ajax;
		if (getParameterByName('lssajax') == '') //don't loop!
		{
			user = $(formSelector + " input[name=user]").first().val();
			password = $(formSelector + " input[name=passwrd]").first().val();
			var staylog;
			try {	
				staylog = $(formSelector + " input[name=cookeineverexp]").first();
			}catch (e)
			{
				staylog = 1;
			}
			
			if (staylog.is(":checked"))
			{
				staylog = '1';
			}
			else
			{
				staylog = '0';
			}
			var datas = "ajax=login&caller=sign_in_home&username="+user+"&password="+password+"&keep_me_signed_in="+staylog;
			$.ajax({
				type:'post',
				data:datas, 
				url:$.lsslogin.solarurl + 'account/',
				dataType: 'json',
				success:function(data,textStatus){
					$(formSelector).submit();
				},
				error:function(data, textStatus){
					console.log(data);
					$(formSelector).submit();
				}
			});
		}
};
$.lsslogin.doLogOut = function()
{
	$.ajax({
		type: 'post',
		data: '',
		url:$.lsslogin.solarurl + 'logout/',
		dataType: 'json',
		success: function(a, b){
			document.location = 'index.php?action=logout';
		},
		error: function (a, b){
			document.location = 'index.php?action=logout';	
		}
		   });
}