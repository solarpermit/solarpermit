/*

Usage example:

$(document).ready(function() {
	$('#search_field').flexcomplete({
		list_groups: [
		    {id: 'my', local: true, container: '#my_items', header: 'My', max_items: 3},
		    {id: 'recent', local: true, container: '#recent_items', header: 'Recent', max_items: 3},
		    {id: 'others', local: false, url: '/s/search/general/?text=', header: 'Others', max_items: 7}
        ],
		show_headers: true, //optional, default true
		dynamic_headers: true, //optional, default true
		top_margin: 10, //optional, default 10
		left_margin: 0, //optional, default 0
		right_margin: 0 //optional, default 0
	});
});

Options definition:
list_groups - 
	id - 
	local - 
	container - 
	url - 
	header - 
	max_items - 
show_headers
dynamic_headers
top_margin
left_margin
right_margin

*/
(function($){
	var methods = {
		init: function (options) {
			
			return this.each(function () {
				var $this = $(this);
				var data = $this.data('flexcomplete');
				
				//extend default settings
				var settings = $.extend({
					list_groups: [],
					search_url: '',
					search_parameter: '',
					request_post: false,
					allow_form_post: true,
					show_headers: true,
					dynamic_headers: true,
					top_margin: 10,
					left_margin: 0,
					right_margin: 0,
					footer: ''
				}, options);
				
				//size and position
				var line_height = $this.height(); //use input height as line height
				var position = $this.offset();
				position.top = position.top + line_height + settings.top_margin; //dropdown to be under the input
				
				var highlighted_item = null; //currently highlighted item
				var items_count = 0; //total number of items
				var actual_search_text = '' //actual search test entered by user
				
				//create the dropdown div and list groups
				var dropdown = $('<div class="flexcomplete" style="line-height: '+line_height+'px;position:absolute;"></div>');
				//var dropdown = $('<div class="flexcomplete"></div>'); // {# removed inline style -RG #}
				var lists = [];
				for (var i = 0; i < settings.list_groups.length; i++) {
					var listGroup = settings.list_groups[i];
					if (settings.show_headers) {
						var header = $('<div class="header">'+listGroup.header+'</div>');
						dropdown.append(header);
					}
					var list = $('<ul></ul>');
					dropdown.append(list);
					lists.push(list);
				}
				if (settings.footer != '') {
					var footer = $('<div class="footer">'+settings.footer+'</div>');
					dropdown.append(footer);
				}
				
				dropdown.width($this.width()); //set to same width as input box
				dropdown.offset(position); //set dropdown position
				dropdown.hide();
				dropdown.css('position', '');
				var search_icon = $this.next();
				if (search_icon.length > 0) {
					search_icon.after(dropdown);
				} else {
					$this.after(dropdown);
				}
				
				// If the plugin hasn't been initialized yet
				if (!data) {
					
					$(this).data('flexcomplete', {
						target: $this,
						settings: settings,
						dropdown: dropdown,
						lists: lists,
						line_height: line_height,
						position: position,
						highlighted_item: highlighted_item,
						items_count: items_count,
						actual_search_text: actual_search_text,
						request: null, //the http request object to enable abort
						data_buffer: [] //buffer for data from all lists, initially empty
					});
				}
				
				//load local items
				$this.flexcomplete('loadItems');
				
				//bind events
				$this.bind('focusin.flexcomplete', methods.handleFocusIn);
				$this.bind('focusout.flexcomplete', methods.handleFocusOut);
				$this.bind('keydown.flexcomplete', methods.handleKeyDown);
				$this.bind('keyup.flexcomplete', methods.handleKeyUp);
			});
		},
		destroy: function () {
			return this.each(function () {
				$(window).unbind('.flexcomplete');
			});
		},
		addItem: function (listIndex, label, url) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			var $list = data.lists[listIndex]; //get list by index
			
			//see if already max # of items
			var addMore = true;
			var maxItems = data.settings.list_groups[listIndex].max_items;
			if (maxItems) {
				if ($list.find('li').length >= maxItems) {
					addMore = false;
				}
			}
			if (addMore) {
				if (!label) label = 'No label provided!';
				if (!url) url = '';
				var $item = $('<li data-url="'+url+'">'+label+'</li>');
				$list.append($item);
				data.items_count++;
				
				//bind events
				$item.bind('click.flexcomplete', function (event) {
					methods.handleItemClick(event, $this);
				});
			}
		},
		//listIndex is optional, if not passed in, all lists will be emptied
		removeItems: function (listIndex) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			if (listIndex) {
				var $list = data.lists[listIndex];
				data.items_count = data.items_count - $list.find('li').length;
				$list.empty();
			} else {
				for (var i = 0; i < data.lists.length; i++) {
					var $list = data.lists[i];
					$list.empty();
				}
				data.items_count = 0;
			}
			data.highlighted_item = null;
			$this.flexcomplete('updateHeaders');
		},
		highlightNextItem: function () {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			if (data.items_count > 0) {
				if (data.highlighted_item == null) {
					data.highlighted_item = 0;
					$this.flexcomplete('highlightItem', data.highlighted_item);
				} else if (data.highlighted_item < data.items_count - 1) {
					$this.flexcomplete('unHighlightItem', data.highlighted_item);
					data.highlighted_item++;
					$this.flexcomplete('highlightItem', data.highlighted_item);
				}
			}
		},
		highlightPreviousItem: function () {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			if (data.items_count > 0) {
				if (data.highlighted_item == 0) {
					$this.flexcomplete('unHighlightItem', data.highlighted_item);
					data.highlighted_item = null;
				} else if (data.highlighted_item > 0) {
					$this.flexcomplete('unHighlightItem', data.highlighted_item);
					data.highlighted_item--;
					$this.flexcomplete('highlightItem', data.highlighted_item);
				}
			}
		},
		highlightItem: function (index) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			var $item = data.dropdown.find('li:eq('+index+')');
			$item.addClass('highlight');
			data.target.val($item.html()); //copy to search field also
		},
		unHighlightItem: function (index) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			var $item = data.dropdown.find('li:eq('+index+')');
			$item.removeClass('highlight');
			data.target.val(data.actual_search_text); //reset search field also
		},
		loadItems: function (isRemote, remoteDataHtml) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			for (var i = 0; i < data.settings.list_groups.length; i++) {
				var listGroup = data.settings.list_groups[i];
				//skip if local & remote mismatch
				if ((listGroup.local && isRemote) || (!listGroup.local && !isRemote)) {
					continue;
				}
				//load from different sources
				if (isRemote) {
					var $remote = $(remoteDataHtml);
					var $items = $remote.find(listGroup.container);
				} else {
					var $items = $(listGroup.container);
				}
				var listData = [];
				$items.each(function () {
					var $container = $(this);
					$container.find('li').each(function () {
						var $li = $(this);
						var $a = $li.find('a:eq(0)');
						
						var label = '';
						var url = '';
						if ($a.length > 0) {
							//has link to another page
							label = $a.html();
							url = $a.attr('href');
						} else {
							label = $li.html();
						}
						var id = $li.attr('data-id');
						var value = $li.attr('data-value');
						var itemData = {
								label: label,
								url: url,
								id: id,
								value: value
							};
						listData.push(itemData);
						$this.flexcomplete('addItem', i, label, url);
					});
					data.data_buffer[i] = listData;
				});
			}
			$this.flexcomplete('updateHeaders');
		},
		updateHeaders: function () {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			if (data.settings.dynamic_headers) {
				//see if more than one group has items
				var populatedGroupCount = 0;
				for (var i = 0; i < data.settings.list_groups.length; i++) {
					var $list = data.lists[i];
					if ($list.find('li').length > 0) {
						populatedGroupCount++;
						data.dropdown.find('.header:eq('+i+')').show();
					} else {
						data.dropdown.find('.header:eq('+i+')').hide(); //this one has no item, hide anyway
					}
				}
				//hide all header if only one group
				if (populatedGroupCount == 1) {
					data.dropdown.find('.header').hide();
				}
			}
		},
		//go to the page specified by the url of the highlighted item
		selectHighlighted: function () {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
			if (data.highlighted_item != null) {
				var $item = data.dropdown.find('li:eq('+data.highlighted_item+')');
				var url = $item.attr('data-url');
	            if (url && url != null & url != '') {
	            	window.location = url;
	            } else {
	            	//copy item text to input field
	            	$this.val($item.html());
	            	//unselect and hide dropdown
	            	data.highlighted_item = null;
	    			$item.removeClass('highlight');
					data.dropdown.hide();
					$this.blur();
	            }
			}
		},
		search: function (searchText) {
			var $this = $(this);
			var data = $this.data('flexcomplete');
			
        	data.actual_search_text = searchText; //remember actual search text
        	
			//if no search text, just remove all and reload all local
			if (searchText == '') {
				$this.flexcomplete('removeItems');
				$this.flexcomplete('loadItems');
				return;
			}
			
			for (var i = 0; i < data.settings.list_groups.length; i++) {
				var listGroup = data.settings.list_groups[i];
				var listData = data.data_buffer[i];
				if (listGroup.local) {
					//local search
					$this.flexcomplete('removeItems', i);
					if (listData) {
						for (var j=0;j<listData.length;j++) {
							var itemData = listData[j];
							if (itemData.label.toLowerCase().indexOf(searchText.toLowerCase()) !== -1) {
								$this.flexcomplete('addItem', i, itemData.label, itemData.url);
							}
						}
					}
					$this.flexcomplete('updateHeaders');
				}
			}
			
			//remote search
			//abort previous request first
			if (data.request) {
				data.request.abort();
			}
			if (data.settings.search_url != '') {
				var searchData = {};
				if (data.settings.search_parameter != '') {
					searchData[data.settings.search_parameter] = searchText;
				}
				if (data.settings.request_post) {
					var requestType = 'post';
				} else {
					var requestType = 'get';
				}
				data.request = $.ajax({
					type: requestType,
					url: data.settings.search_url,
					data: searchData,
					dataType: 'html',
					success:function(response, textStatus){
						$this.flexcomplete('loadItems', true, response);
					},
					error:function(XMLHttpRequest, textStatus, errorThrown){
						//fail silently
					}
				});
				
			}
		},
		
		/* event handler methods */
		
		handleFocusIn: function (event) {
			var $target = $(event.target);
            data = $target.data('flexcomplete');
            
			//show the dropdown div
			//data.dropdown.show();
            //if there is text already, do a search and show dropdown div
            if ($target.val() != '') {
            	$target.flexcomplete('search', $target.val());
            	data.dropdown.show();
            }
		},
		handleFocusOut: function (event) {
			var $target = $(event.target);
            data = $target.data('flexcomplete');
            
            //delay with timer so other events can happen first
			setTimeout(function () {
				data.dropdown.hide();
			}, 200);
		},
		//using keydown to handle dropdown selection
		handleKeyDown: function (event) {
			var $target = $(event.target);
            data = $target.data('flexcomplete');
			
			if (event.which == 38) { //up-arrow
				$target.flexcomplete('highlightPreviousItem');
				event.preventDefault(); //prevent going to the beginning of input text
			} else if (event.which == 40) { //down-arrow
				$target.flexcomplete('highlightNextItem');
			} else if (event.which == 13) { //enter key
				if (data.highlighted_item == null) {
					//no item selected, so normal form submit?
					if (!data.settings.allow_form_post) {
						event.preventDefault(); //prevent normal form submit
					}
				} else {
					$target.flexcomplete('selectHighlighted');
					event.preventDefault(); //prevent normal form submit
				}
			}
		},
		//using keyup to handle search, since the char has been entered at this point
		handleKeyUp: function (event) {
			var $target = $(event.target);
            data = $target.data('flexcomplete');
			
            if ((event.which != 38) &&
            		(event.which != 40) &&
            		(event.which != 13)) {
            	$target.flexcomplete('search', $target.val());
            }
			//if there is search text, show the dropdown div
            if ($target.val() != '') {
            	data.dropdown.show();
            } else {
            	data.dropdown.hide();
            }
		},
		handleItemClick: function (event, $input) {
			var $target = $(event.target);
      var url = $target.attr('data-url'); //go to the page specified by the url
      if (url && url != null & url != '') {
      	window.location = url;
      } else {
      	//copy item text to input field
      	$input.val($target.html());
      }
		}
	};
	
	$.fn.flexcomplete = function (method) {
		//Method calling logic
		if (methods[method]) {
			return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
		} else if (typeof method === 'object' || !method) {
			return methods.init.apply(this, arguments);
		} else {
			$.error('Method ' +  method + ' does not exist on jQuery.flexcomplete');
		}
	};
})(jQuery);