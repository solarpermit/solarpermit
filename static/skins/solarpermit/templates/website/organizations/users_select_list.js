$('#user_list').jscroll({
	callback: function () {
		//since the list changed, bind events only to items with unbind class (new)
		//$('.selectable').unbind('click');
		$('.selectable.unbind').click(function (event) {
			selectableClick(event);
		});
		$('.selectable.unbind').removeClass('unbind'); //remove unbind class
	}
});
//initial bind event for list items
$('.selectable.unbind').click(function (event) {
	selectableClick(event);
});
$('.selectable.unbind').removeClass('unbind'); //remove unbind class

