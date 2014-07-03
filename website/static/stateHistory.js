// needs an alternate implementation for older browsers
function stateHistory(parse, serialize, listen) {
    if (this === window) {
        var that = {};
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
