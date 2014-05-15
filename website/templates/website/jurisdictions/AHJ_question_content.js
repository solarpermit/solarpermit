var $questionLabel = $('.qasv_content.need_tooltip')
$questionLabel.each(function () {
	if (typeof isPrint != 'undefined' && isPrint){//isPrint global
		return false;
	}
	var $container = $(this);
	$container.removeClass('need_tooltip');
	var $target = $container.find('div.label');
	var questionId = $container.data('id');
	var pendingAids = $container.data('paids');
	var jurId = $container.data('jurid');
	var $editButton = $container.find('#edit_button_'+pendingAids);
	if ($editButton.length > 0) {
		//$target.attr('onclick', $editButton.attr('onclick'));
		$target.click(function (){
			return controller.suggestionField.clickEditBt(pendingAids, 'answer', jurId, questionId, pendingAids);
		});
	}
	var showIcon = $target.data('icon');
	if (showIcon == 'Y') {
		$target.tooltip({track: true, 
	        content: function() {
        		if (showIcon == 'Y') {
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

$('.canedit').click(function() {
	answer_id = $(this).data('answerid');
	terminology = $(this).data('terminology');
	jur_id = $(this).data('jurid');
	qid = $(this).data('qid');
	return controller.suggestionField.clickEditBt(answer_id,terminology,jur_id,qid,answer_id);
});

$('.canvoteup').click(function() {
	answer_id = $(this).data('answerid');
	terminology = $(this).data('terminology');
	canvotedown = $(this).data('canvotedown');
	
	set_entity(answer_id, terminology);
	vote_up(canvotedown);
	return false;
});

$('.canvotedown').click(function() {
	answer_id = $(this).data('answerid');
	terminology = $(this).data('terminology');
	canvoteup = $(this).data('canvoteup');
	
	set_entity(answer_id, terminology);
	vote_down(canvoteup);
	return false;
});

var $historyTooltip = $('.need_history');
$historyTooltip.each(function () {
	var $target = $(this);
	$target.removeClass('need_history');
	var answerId = $target.data('id');
	controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: '' });
	$target.tooltip({track: true, 
        content: function() {
            return $('#validation_history_div_'+answerId).html();
        }
	});
});
var $historyDialog = $('.need_history_dialog');
$historyDialog.each(function () {
	var $target = $(this);
	$target.removeClass('need_history_dialog');
	var answerId = $target.data('id');
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
var $downTip = $('.need_down_tip');
$downTip.each(function () {
	var $target = $(this);
	$target.removeClass('need_down_tip');
	$target.tooltip({track: true, 
        content: function() {
            return display_down_vote_last_msg(null, $target.data('last'), $target.data('date'), $target.attr('title'));
        }
	});
});

$('#add_to_favorites_{{question_id}}').click(function(event) 
{   
    $('#add_to_favorites_{{question_id}}').unbind('click');
    $('#add_to_favorites_{{question_id}}').attr('disabled', 'disabled');
    var $target = $(event.target);
    var questionId = $target.data('id');
	var jid = $target.data('jid');    
	controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
});

$('#add_to_quirks_{{question_id}}').click(function(event) 
{
    $('#add_to_quirks_{{question_id}}').unbind('click');
    $('#add_to_quirks_{{question_id}}').attr('disabled', 'disabled');
    var $target = $(event.target);
    var questionId = $target.data('id');
	var jid = $target.data('jid');    
	controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
});

$('#remove_from_favorites_{{question_id}}').click(function(event) 
{   
    var $target = $(event.target);
    var questionId = $target.data('id');
	var jid = $target.data('jid');    
	controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', destination: '' });
});

$('#remove_from_quirks_{{question_id}}').click(function(event) 
{
    var $target = $(event.target);
    var questionId = $target.data('id');
	var jid = $target.data('jid');    
	controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', destination: '' });
});

/*
$('#q_action_link_{{question_id}}').mouseover(function(event) 
{   
    var $target = $(event.target);
    var questionId = $target.data('id'); 
    $('#ahj_actions_{{question_id}}').show();
    $('#more_{{question_id}}').attr('src', '/media/images/more_on.png');
}).mouseout(function(event)
{   
    $('#ahj_actions_{{question_id}}').hide();
    $('#more_{{question_id}}').attr('src','/media/images/more_off.png');
});
*/
