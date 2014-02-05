//Requires jquery.dajax.core.js to be loaded first!!!
//Requires jquery.validate.js

/* initialization */
/*$(document).ready(function(){
	$("form").validate(); //add validation to all forms?
    //diagnostic
    //controller.showForms();

});*/

var controller = new function () {
	var self = this;
/* for forum bridge integration
	//LSS: Change lssSMFUrl to your SMF installation with a trailing slash
	this.lssSMFUrl = 'http://test.solarpermit.org/forum/';
	
	//LSS:
	//hotfix 8-29-13
	this.lsslogin1 = function(usn, pass, data)
	{
		var datastr ='';
                user = usn;
                passwrd = pass;
                datastr = "user="+user+"&passwrd="+passwrd;
                cookieneverexp = 'on';
                datastr += "&cookielength=60&cookieneverexp=";
                $.ajax({type:'post',
                      data: datastr,
         	      //LSS: Change this to your SMF url
                      url:controller.lssSMFUrl + 'index.php?action=login2&lssajax=1',
                      dataType: 'json',
			success: function() {
				controller.handleResponse(data);
			},
				error: function() {
				controller.handleResponse(data);
			}
                });
	}
	this.lssLogin = function() {
		var datastr ='';
		user = $('#username').val();
		passwrd = $('#password').val();
		datastr = "user="+user+"&passwrd="+passwrd;
		cookieneverexp = 'on';
		if ($('#keep_me_signed_in').is(':checked')) {
			datastr += "&cookieneverexp=on";
		} else {
			datastr += "&cookielength=60&cookieneverexp=";
		}
		$.ajax({type:'post',
			data: datastr,
			//LSS: Change this to your SMF url
			url:controller.lssSMFUrl + 'index.php?action=login2&lssajax=1',
			dataType: 'json',
			success:function(data,textStatus) {
				console.log(data);
			}
		});
        controller.submitForm('#form_sign_in');
	}
	this.lsslogout = function(url) {
		$.ajax({
			type: 'post',
			url: this.lssSMFUrl + 'index.php?action=logout',
			data: '',
			dataType: 'json',
			success: function(a, b) {
				document.location = url;
			},
			error: function(a, b) {
				document.location = url;
			}
		});
	}
	//LSS: End
*/
	// submit form to server, with optional callbacks for success and error
/* for forum bridge imtegration
	//LSS: hotfix 8-29-13
	this.submitForm = function (formSelector, success, error, lsslogin) {
*/ 		
	this.submitForm = function (formSelector, success, error) {
		$(formSelector).find('input.url').each(function(index){
			var tValue = $(this).val();
			$(this).val(self.urlValidScheme(tValue));
		});
        //this.showMessage('Please wait...', false);
        
		if ($(formSelector).validate().form()) {  //do validation first
			params = $(formSelector).serialize();
			if (typeof js_csrf !== "undefined") {
		    params = params + '&csrfmiddlewaretoken='+js_csrf
			}
			jQuery.ajax({
				type:'post',
				data:params, 
				url:$(formSelector).attr('action'),
				dataType: 'json',
				success:function(data,textStatus){
					/* for forum bridge integration
					if (lsslogin) {
						success(data);
					} else {
						controller.handleResponse(data);
						if (typeof success !== "undefined") {
							success();
						}
					}
// replaces next four lines						
*/
					controller.handleResponse(data);
					if (typeof success !== "undefined") {
						success();
					}
				},
				error:function(XMLHttpRequest,textStatus,errorThrown){
					if (typeof error !== "undefined") {
						error();
					} else {
                        if (errorThrown !== '')
                            alert(textStatus + ' - ' + errorThrown);
					}
				}
			});
		}
		return false;
	}
	
	// submit form in parent window to server, like when it is in an iframe
	this.submitFormInParent = function (formSelector) {
		if ($(formSelector).validate().form()) {  //do validation first
			var url = $(formSelector).attr('action');
			var data = $(formSelector).serialize();
			//call the parent's function
			parent.controller.submitData(url, data);
		}
		return false;
	}
	
	// submit data (already serialized) to server
	this.submitData = function (url, data) {
		jQuery.ajax({
			type:'post',
			data: data, 
			url: url,
			dataType: 'json',
			success:function(data,textStatus){
				controller.handleResponse(data);
			},
			error:function(XMLHttpRequest,textStatus,errorThrown){
				alert(textStatus);
			}
		});
		return false;
	}
	
	//for modal dialog, set up ajax form submit and button, includes IE8 fix
	this.setUpFormSubmitModalDialog = function (form_selector, button_selector) {
		$(button_selector).unbind('click');
		$(form_selector).unbind('submit');
		$(form_selector).removeAttr('onsubmit'); //remove previous inline script, not needed
		$(form_selector).submit(function (event) {
			var $button = $(button_selector);
			var $form = $(form_selector);
			event.preventDefault(); //prevent non-ajax form post in IE8
			return controller.submitActionsModalDialog($form, $button);
		});
		$(button_selector).click(function (event) {
			var $button = $(button_selector);
			var $form = $(form_selector);
			event.preventDefault(); //prevent non-ajax form post in IE8
			return controller.submitActionsModalDialog($form, $button);
		});
	}
	    
	this.submitActionsModalDialog = function ($form, $button) {
		if (!$button.hasClass('disabled')) {
			$button.attr('disabled','disabled');
			$button.addClass('disabled')
			if ($form.validate().form()) {
				controller.submitForm('#'+$form.attr('id'));
			} else {
				$button.removeAttr('disabled');
				$button.removeClass('disabled')
			}
		}
		return false;
	}
	
	// handle response from server
	// run the script from server if it is provided
	this.handleResponse = function (response) {
		//handle message
		/*if (response.msg && (response.msg != '')) {
			this.showMessage(response.msg, response.error);
		}
		if (response.ac) {
			Dajax.process(response.ac);
		}*/
		Dajax.process(response);
	}
	
	// post request to server with given url and parameters
	this.postRequest = function (url, params) {
        if ("doNotShowMessage" in params)
        {
            if (params['doNotShowMessage'] != 'y')
            {
                //this.showMessage('Please wait...', false);
                //obj = document.getElementById("fancyboxformDiv");
                //obj.innerHTML = "Please wait...";
            }
        }
        else
        {
            //this.showMessage('Please wait...', false);
            //obj = document.getElementById("fancyboxformDiv");
            //obj.innerHTML = "Please wait...";            
        }
    //alert(js_csrf);
    if (typeof js_csrf !== "undefined") {
	    params = $.extend({
				csrfmiddlewaretoken: js_csrf
			}, params);
		}
		jQuery.ajax({
			type:'post',
			data:params, 
			url:url,
			dataType: 'json',
			success:function(data,textStatus){controller.handleResponse(data);},
			error:function(XMLHttpRequest,textStatus,errorThrown){}
		});
		return false;
	}
	
	//open a fancy box popup form, #popupForm on the page, included in main.gsp, get content from url
	/*this.openForm = function (url, refreshItem) {
		if (!refreshItem) {
			onClosed = function() {}
		} else {
			onClosed = function() {
				refreshAlbums();
			}
		}
		//$('#popupForm').craftlyFancybox({
		$('#popupForm').fancybox({
			'href': url,
			'scrolling': 'no',
			'titleShow': false,
			'autoscale' : false,
			'autoDimensions' : true,
			//'transitionIn'	:	'elastic',
			//'transitionOut'	:	'elastic',
			'showCloseButton' : true,
		    'hideOnOverlayClick' : false,
			'type': 'ajax',
			'onClosed': onClosed
		});
		$('#popupForm').click();
	}*/
	
	this.showModalDialog = function (selector, options) {
		var settings = $.extend({
			padding: 0,
			autoSize: true, 
			modal: true,
			helpers: { 
				overlay: {
					locked: true,
					opacity: 0.5
				}
			}
		}, options);
		$.fancybox(selector, settings);
	}
	this.closeModalDialog = function () {
		$.fancybox.close();
	}
	
	this.showSecondDialog = function (selector, options) {
		var settings = $.extend({
			zIndex: 9000
		}, options);
		var $container = $(selector);
		var $parent = $('.fancybox-wrap');
		if ($parent.length > 0) {
			//get parent location, to set container
			var parentPosition = $parent.position();
			var top = parentPosition.top + 25; //fix again 5/8/2003
			var left = parentPosition.left + 20 + 20;
		} else { //in case fancybox is not opened
			var top = Math.round(($('body').height() - $container.height()) / 2);
			var left = Math.round(($('body').width() - $container.width()) / 2);
		}
		$container.css('top', top + 'px');
		$container.css('left', left + 'px');
		if (settings.top > 0){
			$container.css('top', settings.top + 'px');
		}
		$container.css('z-index', settings.zIndex);
		//add overlay
		var $overlay = $('<div class="second_dialog_overlay">&nbsp;</div>');
		$overlay.css('z-index', settings.zIndex - 1);
		var $body = $('body');
		$body.append($overlay);
		
		$container.hide(); //hide before slide down
		$container.slideDown('slow');
	}
	this.closeSecondDialog = function () {
		var $container = $('#secondDialogDiv')
		$container.slideUp('slow', function () {
			$container.html('');
			$('.second_dialog_overlay').remove();
		});
	}
	
	this.showConfirm = function (options) {
		var settings = $.extend({
			title: 'Please Confirm',
			icon: '',
			message: 'Do you want to proceed?',
			proceedText: 'Proceed',
			cancelText: 'Cancel',
			zIndex: 10000,
			checkboxSelector: '',
			callback: null,
			cancelcallback: null,
			onShow: null //additional function run after dialog is shown
		}, options);
		
		var $confirm = $('#confirm');
		
		//see if fancybox is not opened 
		/* no longer show top block with close button in both cases
		if ($('.fancybox-wrap').css('display') == 'block') {
			$confirm.find('.modal_dialog_top_block').hide();
			$confirm.find('.confirm_header').show();
		} else {
			$confirm.find('.modal_dialog_top_block').show();
			$confirm.find('.confirm_header').hide();
		}*/
		
		$confirm.modal({
			autoResize: true,
			zIndex: settings.zIndex,
			onOpen: function (dialog) {
				/*dialog.overlay.fadeIn('slow', function () {
					dialog.container.slideDown('slow', function () {
						dialog.data.fadeIn('slow');
					});
				});*/
				dialog.overlay.show();
				dialog.container.hide(); //hide before slide down
				dialog.data.show();
				dialog.container.slideDown('slow');
			},
			onShow: function (dialog) {
				var modal = this;
				/* no longer show top block with close button in both cases
				if ($('.fancybox-wrap').css('display') == 'block') {
					$('.confirm_header', dialog.data[0]).html(settings.title);
				} else {
					$('.modal_dialog_title', dialog.data[0]).html(settings.title);
				}*/
				$confirm_header = $('.confirm_header', dialog.data[0]);
				$confirm_header.html(settings.title);
				if (settings.icon != '') {
					$icon = '<img src="/media/images/'+settings.icon+'" height="30" alt="image" >&nbsp;&nbsp;&nbsp;';
					$confirm_header.prepend($icon);
				}
				$('.confirm_message', dialog.data[0]).html(settings.message);
				$('.yes', dialog.data[0]).html(settings.proceedText);
				$('.no', dialog.data[0]).html(settings.cancelText);
				//checkbox enable and disable of yes button
				if (settings.checkboxSelector != '') {
					$('.yes', dialog.data[0]).addClass('disabled'); //initially disabled
					//bind checkbox...
					var $checkbox = $(settings.checkboxSelector);
					$checkbox.click(function () {
						if ($checkbox.is(':checked')) {
							$('.yes', dialog.data[0]).removeClass('disabled');
						} else {
							$('.yes', dialog.data[0]).addClass('disabled');
						}
					});
				}
				$('.yes', dialog.data[0]).click(function () {
					//don't proceed if has checkbox and not checked
					if (settings.checkboxSelector != '') {
						var $checkbox = $(settings.checkboxSelector);
						if (!$checkbox.is(':checked')) {
							return;
						}
					}
					// call the callback
					if ($.isFunction(settings.callback)) {
						settings.callback.apply();
					}
					// close the dialog
					modal.close();
					return false;
				});
				$('.close', dialog.data[0]).click(function () {
					if ($.isFunction(settings.cancelcallback)) {
						settings.cancelcallback.apply();
					}
					// close the dialog
					modal.close(); // or $.modal.close();
					return false;
				});
				
				//additional function run after dialog is shown
				if ($.isFunction(settings.onShow)) {
					settings.onShow.apply();
				}
			}
		});
		$('#confirm .confirm_buttons').show();
	}
	
	this.showInfo = function (options) {
		var settings = $.extend({
			target: '', //target element, required
			content: '',
			cancelText: 'Close',
			bufferzone: true,
			zIndex: 8000
		}, options);
		var $target = $(settings.target);
		var closeDialog = function () {
			$('.info_dialog_copy').remove();
			$('body').unbind('mousemove.showInfo');
		}
		if ($target.length > 0) {
			$('.info_dialog_copy').remove(); //remove any previous ones
			var $dialogMaster = $('#info_dialog_master');
			var $dialog = $dialogMaster.clone();
			$dialog.attr('id', ''); //remove id since it is a copy
			$dialog.addClass('info_dialog_copy'); //so we can delete all copies just in case
			var dialog_top = $target.position().top + $target.height();
			var dialog_left = $target.position().left;
			$dialog.css('top', dialog_top).css('left', dialog_left);
			$dialog.css('z-index', settings.zIndex);
			if (settings.content != '') {
				$dialog.find('.info_content').html(settings.content);
			}
			$dialog.appendTo($target.parent());
			$dialog.show();
			//if this is inside a modal_dialog, make sure it is not below the viewable area
			$modal_dialog = $target.closest('.modal_dialog');
			if ($modal_dialog.length > 0) {
				if (($modal_dialog.position().top + $modal_dialog.height()) < (dialog_top + $dialog.height() + 100)) {
					dialog_top = $modal_dialog.position().top + $modal_dialog.height() - $dialog.height() - 100;
					$dialog.css('top', dialog_top);
				}
			}
			$('body').bind('mousemove.showInfo', function (event) {
				//capture initial mouse location
				var startX = $target.data('mouseX');
				if (!startX) {
					$target.data('mouseX', event.pageX);
					startX = event.pageX;
				}
				var startY = $target.data('mouseY');
				if (!startY) {
					$target.data('mouseY', event.pageY);
					startY = event.pageY;
				}
				var dX = event.pageX - startX;
				var dY = event.pageY - startY;
				//see if mouse moves out of range
				if ((dX > $dialog.width()) || (dX < -100) ||
						(dY > $dialog.height() + 50) || (dY < -50)) {
					closeDialog();
				}
			});
			//if mouse actually enter the dialog, also close dialog when mouseleave
			$dialog.mouseenter(function (event) {
				$dialog.mouseleave(function (event) {
					closeDialog();
				});
			});
		}
	}
	
	this.showAlert = function (options) {
		var settings = $.extend({
			title: 'Alert',
			message: 'Something happened',
			cancelText: 'Close',
			zIndex: 10000
		}, options);
		$('#confirm').modal({
			//overlayClose: true,
			autoResize: true,
			zIndex: settings.zIndex,
			onShow: function (dialog) {
				var modal = this;
				$('.confirm_header', dialog.data[0]).html(settings.title);
				$('.confirm_message', dialog.data[0]).html(settings.message);
				$('.yes', dialog.data[0]).hide();
				$('.no', dialog.data[0]).html(settings.cancelText);
				$('.close', dialog.data[0]).click(function () {
					modal.close(); // or $.modal.close();
				});
			}
		});
	}
	
	/*this.showMessage = function (message, hasError) {
		if (hasError == true) {
			var cls = "error";
		} else {
			var cls = "success";
		}
		
		$.notifyBar({
		    html: message,
		    delay: 5000, //How long bar will be delayed, doesn't count animation time.
		    animationSpeed: "normal", //How long this bar will be slided up and down
		    jqObject: null, //Own jquery object for notify bar
		    cls: cls, //You can set own CSS class for 'Notify bar'. There is too premade clasess "error" and "success"
			close: true //If set to true close button will be displayed
		});
	}*/

	this.showMessage = function (message, message_type, message_times) {
		if (!message_type) {
			message_type = 'success';
		}
		if (!message_times) {
			message_times = 2;
		}
		if (message != '') {
			if (document.getElementById('system_message_type_img')){
				document.getElementById('system_message_type_img').src = '/media/images/system_message_type_'+message_type+'.png';
			}
			$('#message_text').html(message);
			var docWidth = $(document).width();
			var docHeight = $(document).height();
			var boxWidth = $('#system_message').width();
			var boxHeight = $('#system_message').height();
			//alert(docWidth);
			//alert(docHeight);
			var boxLeft = Math.round((docWidth - boxWidth) / message_times);
			//var boxTop = Math.round((docHeight - boxHeight) / message_times);
			var boxTop = 108;
			
			
			$('#system_message').css('top', boxTop+'px');
			$('#system_message').css('left', boxLeft+'px');
			$('#system_message').css('zIndex', 12100);
			$('#system_message').css('opacity', 0.8);
			$('#system_message').css('filter', 'alpha(opacity=80)');
			$('#system_message').hide();
			$('#system_message').slideDown('slow', function() {
					$('#system_message').fadeOut(4000, function () {
						$('#system_message').css('opacity', 0);
						$('#system_message').css('filter', 'alpha(opacity=0)');
						$('#message_text').html('');
					});		
				});	
		} else {
			/*$('#system_message').hide();*/
			$('#system_message').css('zIndex', -100);
		}
		return false;
	}
	
	this.showError = function (message) {
		this.showMessage(message, true);
	}
	
    //diagnostic functions
    this.showForms = function() {
        $("form").each(function (index, element) {
            alert($(element).html());
        });
    }
    
    this.sortList = function (listSelector, itemSelector, nameSelector) {
    	var list = $(listSelector);
    	var listitems = list.children(itemSelector).get();
    	listitems.sort(function(a, b) {
    		if (nameSelector) {
    			var textA = $(a).children(nameSelector).text().toUpperCase();
    			var textB = $(b).children(nameSelector).text().toUpperCase();
    		} else {
    			var textA = $(a).text().toUpperCase();
    			var textB = $(b).text().toUpperCase();
    		}
    	    return textA.localeCompare(textB);
    	})
    	$.each(listitems, function(idx, itm) { list.append(itm); });
    }
    
    this.initEditFieldEvent = function(container){
    	
    	this.editFieldEvents(container);
    	$(container).removeAttr("onmouseover");
    }
    this.editFieldEvents = function(container){
    	$(container).each(function(){
    		var field_name = $(this).attr("field");
    		var data_field = "#"+field_name+"_data_field";
    		var data_field_edit = "#"+field_name+"_edit_field";
    		var data_field_edit_btn = "#"+field_name+"_edit_btn";
    		var auth = $(this).attr("authenticated")=="true"?true:false;
    		var field = this;
    		var $form = $('#form_'+field_name);
    		$form.removeAttr("onclick"); //backward compatibility, in case onclick was added to the form
    		//form IE8 compatibility, no longer need to put onclick in the form
    		$form.submit(function (e) {
    			controller.submitForm('#form_'+field_name, function () {
    				$(data_field_edit).hide("slow");
    			});
    			e.preventDefault(); //prevent non-ajax form post in IE8
    			return false;
    		});
    		$(field).find('.show_data').mouseover(function(e){
    			if (auth){
    				//$('#'+field_name+'_edit_btn').show();
    				$(data_field+" div.label").addClass("field_mo_l1");
    			}else{
    				$('#'+field_name+'_suggest_answer_prompt').hide();
    				$(data_field).addClass('show_data');
    			}
    			
    		}).mouseout(function(e){
    			if (auth){
    				//$('#'+field_name+'_edit_btn').hide();
    				$(data_field+" div.label").removeClass("field_mo_l1");
    			}else{
    				$('#'+field_name+'_suggest_answer_prompt').hide();
    				$(data_field).addClass('show_data');
    			}    			
    		});
    		
    		$(data_field+" div.label").mouseover(function(e){
    			if (auth){
    				//$('#'+field_name+'_edit_btn').show();
    				$(this).addClass("field_mo_l2");
    			}
    			
    		}).mouseout(function(e){
    			if (auth){
    				//$('#'+field_name+'_edit_btn').hide();
    				$(this).removeClass("field_mo_l2");
    			} 			
    		}).click(function(e){
    			//$(data_field).css("visibility","hidden");
    			$(data_field_edit_btn).hide();
    			$(data_field_edit).show("slow");
    			
    		});
    		
    		$(field).find("#cancel_"+field_name).click(function(){
    			//$(data_field).css("visibility","visible");
    			$(data_field_edit).hide("slow");
    		});
    		$(field).find("#save_"+field_name).click(function(e){
    			$target = $(e.target);
    			$target.attr("disabled", "disabled"); //prevent multiple clicks
    			if (controller.submitForm('#form_'+field_name)){
    				$(data_field_edit).hide("slow", function () {$target.removeAttr("disabled");});
    			} else {
    				$target.removeAttr("disabled");
    			}
    			
    			return false;
    		});
    	});
    }
    
    this.initSuggestionFieldEvent = function(container){
    	this.suggestionFieldEvents(container);
    	$(container).removeAttr("onmouseover");		
    }
    
    this.suggestionFieldEvents = function(container){
    	var answer_id = $(container).attr("answer.id");
    	var formContainer = $("#form_edit_"+answer_id);
    	var jurisdiction_id = $(formContainer).find("input[name='jurisdiction_id']").val();
    	var question_id = $(formContainer).find("input[name='question_id']").val();
    	
    	$(container).click(function(e){
    		//$("#edit_button_"+answer_id).trigger('click');
    		
    	});
    	$("#save_edit_"+answer_id).click(function(){
    		if($('#form_edit_'+answer_id).validate().form()){
    			$('save_edit_'+answer_id).attr('disabled','disabled');
    			$('#qa_{{answer_key}}_add').hide('slow');
    		}
    	});
    	$("#cancel_edit_"+answer_id).click(function(){
			controller.closeSuggestion(answer_id);
			$("#edit_btn_"+answer_id).css('visibility','visible');
    	});
    }
    this.suggestionField = {};
    this.suggestionField.clickEditBt = function(answer_id,terminology,jurisdiction_id,question_id,answer_id){
	    	if (typeof isPrint != 'undefined' && isPrint){
	    		return false;
	    	}
    		set_entity(answer_id, terminology);
    		controller.postRequest('.', {ajax: 'get_edit_form', jurisdiction_id: jurisdiction_id, question_id: question_id, answer_id: answer_id });
    		controller.openSuggestionEditAnswer(answer_id);
    		//$("#edit_btn_"+answer_id).css('visibility','hidden'); //no need to hide the button
    		return false;
    }
    this.suggestionField.clickAddLabel = function(jurisdiction_id,question_id){
    	
    	if (typeof isPrint != 'undefined' && isPrint){
    		return false;
    	}
    	
    	controller.postRequest('.', {ajax: 'get_add_form', jurisdiction_id: jurisdiction_id, question_id: question_id });
    	controller.openSuggestion(question_id);
    	return false;
    	
    }
    /* using AHJ_question_content.js for mouseover instead
    this.suggestionField.containerMouseover = function(container,pending_editable_answer_ids){
    	
    	if (typeof isPrint != 'undefined' && isPrint){//isPrint is global variable from AHJ_print.html
    		return false;
    	}
    	
    	//if ($(container).find("div.prompt").length>0){
    		$(container).find("div.label").addClass("field_mo_l1").mouseover(function(){
    			$(this).addClass("field_mo_l2");
                
    		}).mouseout(function(){
    			$(this).removeClass("field_mo_l2");
                
    		});
    	//}
    	show_edit_cancel_btns(pending_editable_answer_ids);
    	$(container).mouseout(function(){
    		$(container).find("div.label").removeClass("field_mo_l1").removeClass("field_mo_l2");
    		$(container).removeClass("editdiv");
            hide_edit_cancel_btns(pending_editable_answer_ids);
    	});
    	$(container).addClass("editdiv");
    	//document.getElementById('edit_question_{{question_id}}').style.display='block';show_edit_cancel_btns('{{pending_editable_answer_ids}}');
    }*/
    
    
    this.initOrgEditFieldEvent = function(container){
    	$(container).removeAttr("onmouseover");
    	this.editOrgFieldEvents(container);
		$(container).find('div.label').addClass("field_mo_l1");
    }
    
    this.editOrgFieldEvents = function(container){
    	$(container).hover(
    		function(e){
    			$(container).find('div.label').addClass("field_mo_l1");
    		},
    		function(e){
    			$(container).find('div.label').removeClass("field_mo_l1");
    		}
    	);
    	$(container).find('div.label').hover(
    		function(e){
    			$(container).find('div.label').addClass("field_mo_l2");
    		},
    		function(e){
    			$(container).find('div.label').removeClass("field_mo_l2");
    		}
    	).click(function(e){
    		$(container).find('div.form').show('slow');
    	});
    	$(container).find('div.form input.cancel').click(function(e){
    		$(container).find('div.form').hide('slow');
    	});
    	$(container).find('div.form a.cancel').click(function(e){
    		$(container).find('div.form').hide('slow');
    	});
    }
    
    this.initOrgFieldEvent = function(container){
    	$(container).removeAttr("onmouseover");
    	this.editOrgListFieldEvents(container);
		$(container).find('a').addClass("field_mo_l1");
		$(container).find('.org_remove').css("visibility","visible");
    }
    
    this.editOrgListFieldEvents = function(container){
    	$(container).hover(
    		function(e){
    			$(container).find('a').addClass("field_mo_l1");
    			$(container).find('.org_remove').css("visibility","visible");
    		},
    		function(e){
    			$(container).find('a').removeClass("field_mo_l1");
    			$(container).find('.org_remove').css("visibility","hidden");
    		}
    	);
    	$(container).find('a').hover(
    		function(e){
    			$(container).find('a').addClass("field_mo_l2");
    		},
    		function(e){
    			$(container).find('a').removeClass("field_mo_l2");
    		}
    	);
    }    
    
    this.openSuggestion = function(questionId){
    	$('#qa_'+questionId+'_data div.prompt').hide();
    	$('#qa_'+questionId+'_add').show('slow');
    	$('#suggest_value_btn_'+questionId).hide();
    }
    this.closeSuggestion = function(questionId){
    	$('#qa_'+questionId+'_data div.prompt').show();
    	$('#qa_'+questionId+'_add').hide('slow');
    	$('#suggest_value_btn_'+questionId).show();
    }
    this.openSuggestionEditAnswer = function(answerId){
    	$('#qa_answer_'+answerId+'_edit').show('slow');
    	$('#suggest_value_btn_'+answerId).hide();
    }
    this.closeSuggestionEditAnswer = function(answerId){
    	$('#qa_answer_'+answerId+'_edit').hide('slow');
    	$('#suggest_value_btn_'+answerId).show();
    }	
    
    this.urlValidScheme = function(url){
    	if (url.indexOf('http://')!=0 && url.indexOf('https://')!=0){
    	    url = 'http://'+url;
    	}

    	var urlParts = url.split('?');
    	if (urlParts.length==1){
    	  return url;
    	}
    	var urlPrex = urlParts[0];
    	urlParts = urlParts.splice(1);
    	var urlParams = urlParts.join('?');
    	params = urlParams.split('&');
    	for(var i=0;i<params.length;i++){
    	   param = params[i];
    	   paramParts = param.split('=');
    	   if (paramParts.length==1){
    	        continue;
    	   }
    	   paramParts[1] = encodeURIComponent(decodeURIComponent(paramParts[1]));
    	   params[i] = paramParts.join('=');
    	}
    	urlParams = params.join('&');
    	url = urlPrex+'?'+urlParams;
    	return url;
    }
    
    this.updateUrlAnchor = function(anchor) {
    	if (typeof window.history.replaceState == 'function') { //only if browser supports it
    		var path = location.pathname;
    		var anchor_pos = path.search('#')
    		if (anchor_pos > -1) {
    			path = path.substring(0, anchor_pos)
    		}
    		var new_path = path + anchor
    		window.history.replaceState({}, '', new_path);
    	}
    }
    
    /************** FORM ***************/
    //set up ajax form submit, includes IE8 fix, for ahj question forms.
    this.setUpFormSubmit = function(form_selector, button_selector) {
        $(button_selector).removeAttr('disabled');
        $(button_selector).unbind('click');
        $(form_selector).removeAttr('onsubmit'); //remove previous inline script, not needed
        $(form_selector).unbind('submit');
        $(form_selector).submit(function (event) {
            var $button = $(button_selector);
            var $form = $(form_selector);
            event.preventDefault(); //prevent non-ajax form post in IE8
            return controller.submitActions($form, $button, 1);
        });
    }
    
    this.submitHandler = function(event, submitCount) {
        var $button = $(event.target);
        var $form = $button.closest('form');
        event.preventDefault();
      
        return controller.submitActions($form, $button, submitCount);
    }   

    this.submitActions = function($form, $button, submitCount) {
    	//alert('submitCount '+submitCount);
        $button.attr('disabled','disabled');
		$form.keypress(function(e){
			  if ( e.which == 13 && submitCount > 1) {return false;} 
		});
        if ($form.validate().form()) {     
            controller.submitForm('#'+$form.attr('id'));
            return true;
        } else {
            $button.removeAttr('disabled');
            return false;
        }
    }

    this.validateFormAndActivateSubmit = function(form_selector, button_selector) {
        if ($(form_selector).validate({
        	/*
            showErrors: function(errorMap, errorList) {
            // Do nothing here
            }
            */
        
        }).form()) {
	        $(button_selector).removeAttr('disabled');
	        $(button_selector).removeClass('disabled');              
        }
        else
        {
            $(button_selector).attr('disabled'); 
            $(button_selector).addClass('disabled');          
        }
        

        
        
        return false;
    }
    
    
    
    this.processUrlField = function(id) {
        var value = $('#'+id).val();
        value = controller.urlValidScheme(value);
        $('#'+id).val(value);
        $('#'+id).addClass('url');
    }
    
    this.activateButton = function(button_selector) {
	    $(button_selector).removeAttr('disabled');
	    $(button_selector).removeClass('disabled');     
    }
    
    this.disableButton = function(button_selector) {
	    $(button_selector).attr('disabled');
	    $(button_selector).addClass('disabled');     
    }    
    
}