var $questionLabel = $('.question-container');
$questionLabel.each(function () {

    var $container = $(this);
    $container.removeClass('need_tooltip');
    var $label = $container.find('div.label');
    var $target = $container.find('.editicon');
    var $editButton = $container.parent().find('input.editbt.canedit');
    var jurId = $container.find('.qasv_content').data('jurid');
    var questionId = $container.find('.qasv_content').data('id');
    if ($editButton.length > 0) {
        $label.click(function (){
            return controller.suggestionField.clickEditBt($editButton.data('id'),
                                                          'answer',
                                                          jurId,
                                                          questionId);
        });
    }
    var showIcon = $label.data('icon');
    var label_tooltip = $label.data('label_tooltip');
    if (showIcon == 'Y') {
        $target.tooltip({track: true,
            content: function() {
                if (showIcon == 'Y') {
                    if (label_tooltip != '') {
                        return label_tooltip;
                    }
                    else
                    {
                        var v1 = $target.attr('title');
                        if (v1) {
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
    }
});




$('.cancel_this_value').each(function() {
    $(this).click(function (e) {
        var $target = $(e.target);
        var answer_id = $target.data('id');
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
        var $target = $(e.target);
        var answer_id = $target.data('id');
        var terminology = $target.data('terminology');

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
        var $target = $(e.target);
        var answer_id = $target.data('answerid');
        var terminology = $target.data('terminology');
        var canvotedown = $target.data('canvotedown');


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
        var $target = $(e.target);
        var answer_id = $target.data('answerid');
        var terminology = $target.data('terminology');
        var canvoteup = $target.data('canvoteup');

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
        var $target = $(e.target);
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
/*
var $historyTooltip = $('.need_history');
$historyTooltip.mouseover(function (event) {
    var $target = $(event.target);
    $target.removeClass('need_history');
    var answerId = $target.data('id');
    controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: '', callback:
				 function() { $target.tooltip({track: true,
							       content: function() {
								   return $('#validation_history_div_'+answerId).html();
							       }
							      });
					    }});
});

var $historyDialog = $('.need_history_dialog');
$historyDialog.click(function (event) {
    var $target = $(event.target);
    //$target.removeClass('need_history_dialog');
    var answerId = $target.data('id');
    $target.click(function () {
        controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: 'dialog' });
    });
});
*/
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
        var $target = $(e.target);
        var questionId = $target.data('id');
        var jid = $target.data('jid');
        controller.postRequest('.', {ajax: 'get_add_form', jurisdiction_id: jid, question_id: questionId});
        controller.openSuggestion(questionId);
        //return false;
    });
});

$('.cancel_this_value').each(function() {
    $(this).click(function (e) {
        var $target = $(e.target);
        var answer_id = $target.data('id');
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
        var $target = $(e.target);
        var answer_id = $target.data('id'),
            terminology = $(this).data('terminology'),
            jur_id = $(this).data('jurid');
        var qid = $(this).data('qid');
        return controller.suggestionField.clickEditBt(answer_id,terminology,jur_id,qid,answer_id);
    });
});
$(".cancel_btn").tooltip({track: true});
$(".edit_btn").tooltip({track: true});

$("#ahj_tab_content").on('click',
			 ".ahj_category_header",
			 function (event) {
			     $(this).parent().toggleClass("closed").find(".ahj_category_body").slideToggle();
			 });

$("#ahj_tab_content").on('click',
			 ".valhis",
			 function (event) {
			     $that = $(this);
			     $box = $that.parent().parent().siblings(".valhis_box");
			     answerId = $that.data('id');
			     if (!$box.html() || $box.html() == "") {
				 controller.postRequest('.', {ajax: 'validation_history', entity_id: answerId, entity_name: 'requirement', destination: '', callback:
							      function() {
								  $box.slideToggle();
								  $that.toggleClass("closed");
							      }});
			     } else {
				 $box.slideToggle();
				 $that.toggleClass("closed");
			     }
			 });

var category = window.location.pathname.match('/([^/]*?)/$')[1];

$("#ahj_tab_content").on('click',
			 ".add_to_favorites",
			 function (event) {
			     $that = $(this);
			     questionId = $that.data('id');
			     jid = $that.data('jid');
			     $('#favorite_field_'+questionId).unbind('click');
			     $('#favorite_field_'+questionId).attr('disabled', 'disabled');
			     controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', category: category });
			 });

$("#ahj_tab_content").on('click',
			 ".remove_from_favorites",
			 function (event) {
			     $that = $(this);
			     questionId = $that.data('id');
			     jid = $that.data('jid');
			     $('#favorite_field_'+questionId).unbind('click');
			     $('#favorite_field_'+questionId).attr('disabled', 'disabled');
			     controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'favorites', category: category });
			 });

$("#ahj_tab_content").on('click',
			 ".add_to_quirks",
			 function (event) {
			     $that = $(this);
			     questionId = $that.data('id');
			     jid = $that.data('jid');
			     $('#favorite_field_'+questionId).unbind('click');
			     $('#favorite_field_'+questionId).attr('disabled', 'disabled');
			     controller.postRequest('.', {ajax: 'add_to_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', category: category });
			 });

$("#ahj_tab_content").on('click',
			 ".remove_from_quirks",
			 function (event) {
			     $that = $(this);
			     questionId = $that.data('id');
			     jid = $that.data('jid');
			     $('#favorite_field_'+questionId).unbind('click');
			     $('#favorite_field_'+questionId).attr('disabled', 'disabled');
			     controller.postRequest('.', {ajax: 'remove_from_views', jurisdiction_id: jid, question_id: questionId, entity_name: 'quirks', category: category });
			 });
