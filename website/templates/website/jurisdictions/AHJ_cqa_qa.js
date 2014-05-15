
        var $questionLabel = $('.qasv_content.need_tooltip')
        $questionLabel.each(function () {
            
            var $container = $(this);
            $container.removeClass('need_tooltip');
            var $target = $container.find('div.label');
            var questionId = $container.data('id');
            var pendingAids = $container.data('paids');
            var jurId = $container.data('jurid');
            var $editButton = $container.find('#edit_button_'+pendingAids);
            if ($editButton.length > 0) {
                $target.click(function (){
                    return controller.suggestionField.clickEditBt(pendingAids, 'answer', jurId, questionId, pendingAids);
                });
            }
            var showIcon = $target.data('icon');
            var label_tooltip = $target.data('label_tooltip');
            if (showIcon == 'Y') {
                $target.tooltip({track: true, 
                    content: function() {
                        if (showIcon == 'Y') {
                            if (label_tooltip != '') {
                                return label_tooltip;                   
                            }
                            else
                            {
                                v1 = $target.attr('title'); 
                                if (v1 != 'None') {
                                    var a_or_an = 'a';  
                                    var vowels = 'aeiou';
                                    if (vowels.indexOf(v1.charAt(0)) >= 0)
                                        a_or_an = 'an';
                                        
                                    return 'Suggest ' + a_or_an + ' ' + v1 + ' for this field';
                                } else { 
                                    return 'Suggest a value for this field';
                                }
                            }
                        }
                    }
                });
                                
                $target.mouseover(function (e) {
                    $target.addClass("field_mo_l1").addClass("field_mo_l2");
                    $container.addClass("editdiv");
                    //show_edit_cancel_btns(pendingAids);
                });
                $target.mouseleave(function (e) {
                    $target.removeClass("field_mo_l2");
                });
                $container.parent().mouseleave(function (e) {
                    $target.removeClass("field_mo_l1").removeClass("field_mo_l2");
                    $container.removeClass("editdiv");
                    //hide_edit_cancel_btns(pendingAids);
                });
                var is_print = $target.data('print');
                if (is_print == 'F'){
                    $target.click(function (){
                        return controller.suggestionField.clickAddLabel(jurId, questionId);
                    });
                }
            }
        });        
        
        
        
        
        $('.cancel_this_value').each(function() {         
            $(this).click(function (e) {
                $target = $(e.target);
                answer_id = $target.data('id');  
                controller.showConfirm({
                    title: 'Are you sure you want to cancel your suggestion?',
                    icon: 'question_mark.jpg',
                    message: '<br>',
                    proceedText: 'Yes',
                    cancelText: 'No',
                    callback: function()
                        {
                            controller.postRequest('.', {ajax: 'cancel_suggestion', entity_id : answer_id});
                        }
                }); 
            });
        });
        
        $('.approve_this_value').each(function(event) {
            $(this).click(function (e) {        
                $target = $(e.target);
                answer_id = $target.data('id');
                terminology = $target.data('terminology');                                                       
         
                controller.showConfirm({
                        title: 'Are you sure you want to approve this '+terminology+'?',
                        icon: 'question_mark.jpg',
                        message: '<br>',
                        proceedText: 'Yes',
                        cancelText: 'Cancel',
                        callback: function() {
                            $('#approve_this_value_'+answer_id).attr('disabled','disabled');
                            controller.postRequest('.', {ajax: 'approve_suggestion', entity_id : answer_id});                                             
                        }
                });       
            });
        });
        
        $('.canvoteup').each(function() {
            $(this).click(function (e) {        
                $target = $(e.target);
                answer_id = $target.data('answerid');
                terminology = $target.data('terminology');
                canvotedown = $target.data('canvotedown');
                
            
                if (canvotedown == 'false')
                {
                    controller.showConfirm({
                        title: 'Do you want to change your vote to approve?',
                        icon: 'question_mark.jpg',
                        message: '<br>',
                        proceedText: 'Yes',
                        cancelText: 'Cancel',
                        callback: function() {
                            $('#voteup_'+answer_id).unbind('click');
                            $('#voteup_'+answer_id).attr('disabled','disabled');
                            $('#voteup_'+answer_id).addClass('disabled');
                            controller.postRequest('.', {ajax: 'vote', vote: 'up', entity_name: 'requirement', entity_id: answer_id});
                            //return true;                                          
                        }
                    });  
                }
                else   
                {
                    $('#voteup_'+answer_id).unbind('click');
                    $('#voteup_'+answer_id).attr('disabled','disabled');
                    $('#voteup_'+answer_id).addClass('disabled');
                    controller.postRequest('.', {ajax: 'vote', vote: 'up', entity_name: 'requirement', entity_id: answer_id});            
                }
                                          
            });
        });
        
                        
        $('.canvotedown').each(function() {
            $(this).click(function (e) {
                $target = $(e.target);
                answer_id = $target.data('answerid');
                terminology = $target.data('terminology');
                canvoteup = $target.data('canvoteup');
            
                if (canvoteup == 'false')
                {    
                    controller.showConfirm({
                        title: 'Do you want to change your vote to disapprove?',
                        icon: 'question_mark.jpg',
                        message: '<br>',
                        proceedText: 'Yes',
                        cancelText: 'Cancel',
                        callback: function() {
                                $('#votedown_'+answer_id).unbind('click');    
                                $('#votedown_'+answer_id).attr('disabled','disabled');
                                $('#votedown_'+answer_id).addClass('disabled');        
                                controller.postRequest('.', {ajax: 'vote', vote: 'down', entity_name: 'requirement', entity_id: answer_id});                                          
                            }
                    });  
                }
                else   
                {
                    $('#votedown_'+answer_id).unbind('click');    
                    $('#votedown_'+answer_id).attr('disabled','disabled');
                    $('#votedown_'+answer_id).addClass('disabled');        
                    controller.postRequest('.', {ajax: 'vote', vote: 'down', entity_name: 'requirement', entity_id: answer_id});
                }
            
            });
        });        
        
        $('.add_another_value').each(function(event) 
        {
            $(this).click(function (e) {        
                $target = $(e.target);
                var questionId = $target.data('id');
                var jid = $target.data('jid');    
                controller.postRequest('.', {ajax: 'get_add_form', jurisdiction_id: jid, question_id: questionId});
                controller.openSuggestion(questionId);
                //return false;
            });
        });
        
        
    

                
    function confirm_rejected(entity_id, value_terminology)
    {
            controller.showConfirm({
                title: 'Reject this '+value_terminology+'?',
                icon: 'question_mark.jpg',
                message: 'Your vote will confirm this '+value_terminology+' as false and close voting.<br/>Are you sure you want to reject this '+value_terminology+'?',
                proceedText: 'Yes',
                cancelText: 'Cancel',
                callback: function(){
                    controller.postRequest('.', {ajax: 'vote', vote: 'down', entity_name: 'requirement', entity_id: entity_id, confirmed:'yes'});                     
                }
            });  
        return false;
    }  
    
        var $historyTooltip = $('.need_history');
        $historyTooltip.mouseover(function (event) {
            //alert('validaetion');
            var $target = $(event.target);
            //var $target = $(event.target);
            //$target.removeClass('need_history');
            var answerId = $target.data('id');
            //alert(answerId);
            controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: '' });
            $target.tooltip({track: true, 
                content: function() {
                    return $('#validation_history_div_'+answerId).html();
                }
            });
        });
        var $historyDialog = $('.need_history_dialog');
        $historyDialog.click(function (event) {
            var $target = $(event.target);
            //$target.removeClass('need_history_dialog');
            var answerId = $target.data('id');
            //alert('history dialog');
            $target.click(function () {
                controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: 'dialog' });
            });
        });          
    
        var $commentsDialog = $('.need_comment');
        $commentsDialog.each(function () {
            var $target = $(this);
            $target.removeClass('need_comment');
            var answerId = $target.data('id');
            var jid = $target.data('jid');
            $target.click(function (e) {
                controller.postRequest('/jurisdiction_comment/', {ajax: 'open_jurisdiction_comment', jurisdiction_id: jid, entity_id: answerId, entity_name: 'AnswerReference'});
                e.preventDefault();
            });
        });            
    
        $('.add_another_value').each(function(event) 
        {
            $(this).click(function (e) {        
                $target = $(e.target);
                var questionId = $target.data('id');
                var jid = $target.data('jid');    
                controller.postRequest('.', {ajax: 'get_add_form', jurisdiction_id: jid, question_id: questionId});
                controller.openSuggestion(questionId);
                //return false;
            });
        });    
    
        $('.cancel_this_value').each(function() {         
            $(this).click(function (e) {
                $target = $(e.target);
                answer_id = $target.data('id');  
                controller.showConfirm({
                    title: 'Are you sure you want to cancel your suggestion?',
                    icon: 'question_mark.jpg',
                    message: '<br>',
                    proceedText: 'Yes',
                    cancelText: 'No',
                    callback: function()
                        {
                            controller.postRequest('.', {ajax: 'cancel_suggestion', entity_id : answer_id});
                        }
                }); 
            });
        });      
        
        $('.canedit').each(function(event) 
        {
            $(this).click(function (e) {        
                $target = $(e.target);
                var answer_id = $target.data('id');
	            terminology = $(this).data('terminology');
	            jur_id = $(this).data('jurid');
            	qid = $(this).data('qid');	            
            	return controller.suggestionField.clickEditBt(answer_id,terminology,jur_id,qid,answer_id);
            });
        });            
        
        $('.add_to_favorites').click(function(event) 
        {   
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            $('#add_to_favorites_'+questionId).unbind('click');
            $('#add_to_favorites_'+questionId).attr('disabled', 'disabled');            
            controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
        });
        
        $('.add_to_quirks').click(function(event) 
        {

            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');   
            $('#add_to_quirks_'+questionId).unbind('click');
            $('#add_to_quirks_'+questionId).attr('disabled', 'disabled');            
            controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
        });
        
        $('.remove_from_favorites').click(function(event) 
        {   
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
        });
        
        $('.remove_from_quirks').click(function(event) 
        {
            var $target = $(event.target);
            var questionId = $target.data('id');
            var jid = $target.data('jid');    
            controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
        });
        
        $('.q_action_link').each(function() {
            $(this).mouseover(function (e) { 
                $target = $(e.target);
                questionId = $target.data('id');
                $('#ahj_actions_'+questionId).show();
                $('#more_'+questionId).attr('src', '/media/images/more_on.png');
            }).mouseout(function (e) {
            	$target = $(e.target);
            	questionId = $target.data('id'); 
            	p =  $target.position();
            	l = p.left ;
            	t = p.top ;
            	startX = e.pageX ;    	
            	startY = e.pageY ;
            	//alert($target.width());
            	//alert(l);alert(t);alert(startX);alert(startY);
            	if ( (startX > l && startX < l+ 150) && ( t+$target.height()-5 < startY && startY < t+100 +$target.height()) ) {} else{
            		//alert(123);            
                	$('#ahj_actions_'+questionId).hide();
                	$('#more_'+questionId).attr('src', '/media/images/more_off.png');
                }
            });       
         });
         
         $('.ahj_action_flyout').mouseover(function (){
         	qid = $(this).data('id');
         	$('#ahj_actions_'+qid).show();
            $('#more_'+qid).attr('src', '/media/images/more_on.png');
         });
         
         $('.ahj_action_flyout').mouseout(function (){
         	qid = $(this).data('id');
         	$('#ahj_actions_'+qid).hide();
            $('#more_'+qid).attr('src', '/media/images/more_off.png');
         });        
                
        $(".cancel_btn").tooltip({track: true});
        $(".edit_btn").tooltip({track: true});               
                             