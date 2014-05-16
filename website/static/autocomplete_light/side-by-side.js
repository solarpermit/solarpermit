// These substrings get you hundreds or thousands of results so we
// avoid searching for them, opting instead to wait for the user to
// type another character
var COMMON = ["ille", "vill", "land", "owns", "svil", "ship", "nshi",
              "wnsh", "ield", "fiel", "burg", "ngto", "ingt", "gton",
              "ford", "ring", "town", "sbur", "ston", "wood", "ount",
              "ster", "orth", "prin", "nton", "ings", "lton", "nvil",
              "dale", "idge", "reen", "outh"];

// These, on the other hand, are all the cities which have
// three-character names. We'll autocomplete these even though some of
// them return more results than we'd like.
var THREE_LETTER = ["ace", "ada", "aho", "aid", "ajo", "ama", "amo",
                    "ari", "ark", "arm", "arp", "art", "ary", "ash",
                    "ava", "ayr", "bay", "bee", "bem", "bim", "bly",
                    "bow", "bud", "cid", "cly", "coe", "cox", "coy",
                    "cut", "day", "dee", "dix", "dow", "duo", "dye",
                    "eek", "ege", "ela", "eli", "elk", "elm", "ely",
                    "era", "eva", "fay", "fig", "flo", "fly", "fox",
                    "fry", "gap", "gas", "gay", "gem", "guy", "hay",
                    "hoy", "hye", "ida", "igo", "ila", "ina", "ink",
                    "ira", "iva", "ivy", "ixl", "jal", "jay", "jet",
                    "job", "joy", "jud", "kay", "keo", "kim", "lay",
                    "lea", "lee", "leo", "loa", "lon", "lum", "lux",
                    "mae", "man", "max", "may", "mio", "moe", "naf",
                    "ned", "ney", "nye", "oak", "odd", "ola", "oma",
                    "ona", "ong", "ono", "opp", "ops", "ora", "ord",
                    "orr", "oso", "oto", "pax", "pep", "poe", "ray",
                    "rea", "reo", "rew", "rex", "rig", "rio", "roe",
                    "roy", "rye", "sac", "sod", "sun", "tad", "tea",
                    "tok", "tom", "tow", "tye", "ulm", "una", "uno",
                    "usk", "ute", "uva", "van", "veo", "war", "wax",
                    "way", "wea", "why", "yoe", "zap", "zim", "zoe"];

$(document).bind('yourlabsWidgetReady',
                 function() {
                     $('body').on('initialize',
                                  '.autocomplete-light-widget[data-widget-bootstrap=side-by-side]',
                                  function() {
                                      $(this).yourlabsWidget(ourWidget);
                                  });
                 });

var ourWidget = { initializeAutocomplete: init,
                  selectChoice: select,
                  deselectChoice: deselect,
                  updateAutocompleteExclude: updateExclude,
                  hide: nothing
                };

function nothing() {
    // do nothing, on purpose
}

/**
 * Overrides for the Autocomplete class
 */
function refresh() {
    this.value = this.getQuery().toLowerCase();
    if (THREE_LETTER.indexOf(this.value) !== -1 ||
        this.value.length > 4 ||
        COMMON.indexOf(this.value) === -1) {
        yourlabs.Autocomplete.prototype.refresh.call(this);
    }
}

/**
 * Overrides for the Widget class
 */
function init() {
    this.select = this.widget.find('select.value-select');
    var box = this.box = this.widget.find('select.box'); 
    var deck = this.deck = this.widget.find('select.sbsdeck');
    this.autocomplete = this.input.yourlabsAutocomplete({ box: this.box,
                                                          fixPosition: nothing,
                                                          hide: nothing,
                                                          move: nothing,
                                                          boxMouseenter: nothing,
                                                          boxMouseleave: nothing,
                                                          boxClick: nothing,
                                                          minimumCharacters: 3,
                                                          refresh: refresh
                                                        });
    var self = this;
    $("button.select").click(function () {
                                 box.find(':selected')
                                    .each(function () {
                                              self.selectChoice($(this));
                                          });
                             });
    $("button.deselect").click(function () {
                                   deck.find(':selected')
                                       .each(function () {
                                                 self.deselectChoice($(this));
                                             });
                               });
}

function select(choice) {
    var self = this;
    var values = choice.data('value-multiple');
    if (values) {
        this.freeDeck();
        this.addToDeck(choice, choice.data('value'));
        if (typeof values === "string") {
            values = values.split(",");
        } else if (typeof values === "number") {
            values = [values];
        }
        values.map(function (v) {
                       yourlabs.Widget
                               .prototype
                               .addToSelect
                               .call(self, choice, v);
                   });
        var index = $(':input:visible').index(this.input);
        this.resetDisplay();
        if (this.input.is(':visible')) {
            this.input.focus();
        } else {
            var next = $(':input:visible:eq('+ index +')');
            next.focus();
        }
        if (this.clearInputOnSelectChoice === "1")
            this.input.val('');
    } else {
        yourlabs.Widget.prototype.selectChoice.call(this, choice);
    }
}

function deselect(choice) {
    var self = this;
    var values = choice.data('value-multiple');
    if (values) {
        if (typeof values === "string") {
            values = values.split(",");
        } else if (typeof values === "number") {
            values = [values];
        }
        values.map(function (v) {
                       self.select
                           .find('option[value="'+v+'"]')
                           .remove();
                   });
        this.select.trigger('change');
        choice.remove();
        this.updateAutocompleteExclude();
        this.resetDisplay();
    } else {
        yourlabs.Widget.prototype.deselectChoice.call(this, choice);
    }
}

function updateExclude() {
    var widget = this;
    var choices = this.select.find("[value]");
    this.autocomplete.data['exclude'] = $.map(choices,
                                              function(choice) { 
                                                  return $(choice).attr("value");
                                              });
}

