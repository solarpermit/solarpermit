// needs an alternate implementation for older browsers
function stateHistory(parse, serialize, listen) {
    if (this === window) {
	var that = new stateHistory();
    } else {
	var that = this;
    }

    that.pushState = function pushState(state) {
	if (document.location.href.indexOf('#') >= 0) {
	    history.pushState(state, "", document.location.href.replace(/#.*$/, '#' + serialize(state)));
	} else {
	    history.pushState(state, "", document.location.href + '#' + serialize(state));
	}
    };
    that.getState = function getState() {
	return history.state || parse(document.location.hash.substr(1));
    };
    that.listen = function popState(func) {
	var self = that;
	window.addEventListener("popstate",
				function (e) {
				    func(e.state || self.getState());
				});
    };
    that.listen(listen);
    return that;
}

function replaceItem(array, index, replacement) {
    var newArray = (array ? array.slice() : []);

    newArray.splice(index, 1, replacement);

    return newArray;
}

function serializeReports(params) {
    var reports = [];

    $.each(params,
	   function (index, item) {
	       var question = item.question;
	       var result = question;

	       if (item.filter && item.filter.type && item.filter.values) {
		   var filterType = item.filter.type;
		   var filterValues = item.filter.values;

		   result += ":" + filterType + "=" + filterValues.join(',');
	       }

	       reports.push(result);
	   });

    return reports.join(';');
}

function deserializeReports(paramstring) {
    var reports = paramstring.split(';');
    var newState = [];

    $.each(reports,
	   function(index, report) {
	       var result = {};
	       var parts = report.split(':');

	       result['question'] = parts[0];

	       if (parts[1]) {
		   var filter = parts[1].split('=');
		   if (filter[1]) {
		       var filterValues = filter[1].split(',');
		       result['filter'] = { type: filter[0], values: filterValues };
		   }
	       }

	       newState.push(result);
	   });

    return newState;
}
