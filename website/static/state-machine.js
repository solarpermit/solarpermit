/**
 * Defines a state machine given a set of state, events and transitions.
 * @class StateMachine
 *
 * @param {String} name A name for the state machine, to use in logging.
 * @param {String} initial The initial state of the machine.
 * @param {Object} states An object whose keys are state names and
 *  whose values are objects whose keys are event names and whose
 *  values are transition functions that return a new state.
 * @param {Function} unexpectedEvent An optional function that is
 *  called when an event is received that is unexpected when the
 *  machine is in the current state.
 * @param {Function} unknownState An optional function that is called
 *  when a transition function returns an unknown state.
 * 
 * <p>states should take the form:
 * <pre>
 * {
 *   stateName: {
 *       event1: function () { ... },
 *       event2: function () { ... },
 *       ...
 *   },
 *   otherStateName: { ... },
 *   ...
 * }
 * </pre>
 *
 * <p>The generated StateMachine object will then take this shape:</p>
 * <pre>
 * {
 *     handleEvent: function (event) {
 *         // ...
 *     },
 *     event1: function () { ... },
 *     event2: function () { ... }
 * }
 * </pre>
 *
 * <p>Note that StateMachine's imported event names are NOT the methods on the
 * individual state objects. Instead, they are functions which splice in the
 * event and the current state before the existing arguments, before calling
 * those state object methods.</p>
 */
function StateMachine(name, initial, states, unexpectedEvent, unknownState) {
    if ((typeof name != "string") || !name) {
        throw new Error("StateMachine requires a name");
    }
    if ((typeof initial != "string") || !initial) {
        throw new Error("StateMachine initial state must be defined");
    }    
    if ((typeof states != "object") || !states) {
        throw new Error("StateMachine state definitions must be defined");
    }
    if (!(initial in states)) {
        throw new Error("Unknown initial state!");
    }

    for (var stateName in states) {
        if (typeof states[stateName] != "object") {
            throw new Error("states['" + stateName + "'] is not an event map!");
        }
        var state = states[stateName];
        for (var method in state) {
            if (typeof state[method] != "function") {
                throw new Error("Unknown state method: " + stateName + ", " + method);
            }
        }
    }

    var self = this;
    var current = initial;

    /**
     * Handle the named event
     * @param {String} event
     */
    this.handleEvent = function (event) {
        Array.prototype.splice.call(arguments, 0, 1, event, current);

        var next = (states[current][event] || logUnexpectedEvent).apply(this, arguments);
        if (!(next && states[next]))
            next = logUnknownState(next, event);
        return (current = next);
    };

    /**
     * Return the current state. Probably only needed for debugging.
     * @return {String} current state
     */
    this.getCurrentState = function () {
        return current;
    };

    // add a public method to this for each event type the machine should
    // support, as a convenience to the user
    $.each(states, function (state) {
        $.each(states[state], function (event) {
            if (!self[event]) {
                self[event] = function () {
                    Array.prototype.splice.call(arguments, 0, 0, event);
                    return self.handleEvent.apply(self, arguments);
                };
            }
            // else, some other state method had the same name, so we're already covered.
        });
    });

    function logUnexpectedEvent(event) {
        console.error("%s: state machine received unexpected event %s while in state %s", name, event, current);
        unexpectedEvent && unexpectedEvent(event);
    };
    function logUnknownState(next, event) {
        console.error("%s: state machine transitioned to unknown state %s by event %s from state %s", name, next, event, current);
        return unknownState && unknownState(next, event);
    };
}
/* Note this does NOT have any added prototype methods.  This is because StateMachine() defines
   public methods on itself based on the passed-in states. */

/**
 * A specialized state machine for objects that can be hidden
 *
 * @class
 * @param {Function} doShow called when the object needs to be shown
 * @param {Function} doHide called when the object needs to be hidden
 */
function Hideable(name, doShow, doHide) {
    function onShow() {
        var args = Array.prototype.slice.call(arguments, 2);
        doShow && doShow.apply(null, args);
        return "visible";
    }
    function onHide() {
        var args = Array.prototype.slice.call(arguments, 2);
        doHide && doHide.apply(null, args);
        return "hidden";
    }
    function ignore(event, state) { return state; }

    return new StateMachine(name,
                            "hidden",
                            { visible: { show: ignore,
                                         hide: onHide,
                                         toggle: onHide
                                       },
                              hidden: { show: onShow,
                                        hide: ignore,
                                        toggle: onShow
                                      }
                            });
}

/**
 * Set up a short-term timer
 * @param {Function} callback  call this function when the timer fires
 * @param {Number}   duration  wait this long (milliseconds) between calls to the callback
 * @param {Boolean}  [repeating] true for a repeating timer
 */
function QuickTimer(callback, duration, repeating) {
    if (!callback) {
        console.error("QuickTimer requires a callback");
    }

    var timerid;
    var machine = new StateMachine("QuickTimer",
                                   "waiting",
                                   { waiting: { timer: fire,
                                                cancel: cancel
                                              },
                                     firing: { repeat: repeat,
                                               done: done,
                                               cancel: cancel
                                             },
                                     done: { },
                                     cancelled: { }
                                   });

    function fire() {
        setTimeout(function() {
                       try {
                           callback();
                       } catch (x) {
                           console.warn("%s: QuickTimer callback threw an exception:", name, x);
                       } finally {
                           repeating ? machine.repeat()
                                     : machine.done();
                       }
                   });

        return "firing";
    };
    function repeat() { timerid = setTimeout(machine.timer, duration); return "waiting"; };
    function done() { return "done"; };
    function cancel() { clearTimeout(timerid); return "cancelled"; }
    this.cancel = function() { machine.cancel(); };

    timerid = setTimeout(machine.timer, duration);
};

QuickTimer.ONE_SECOND = 1000;
QuickTimer.ONE_MINUTE = 60 * 1000;

/**
 * Set up a repeating short-term timer
 * @param {Function} callback  call this function when the timer fires
 * @param {Number}   duration  wait this long (milliseconds) between calls to the callback
 */
function RepeatingQuickTimer(callback, duration) {
    return new QuickTimer(callback, duration, true);
}
