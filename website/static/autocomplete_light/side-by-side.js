function nothing() {
    // do nothing, on purpose
}
var ourWidget = { initializeAutocomplete: function () {
                      this.select = this.widget.find('select.value-select');
                      var box = this.box = this.widget.find('select.box'); 
                      var deck = this.deck = this.widget.find('select.sbsdeck');
                      this.autocomplete = this.input.yourlabsAutocomplete({ box: this.box,
                                                                            fixPosition: nothing,
                                                                            hide: nothing,
                                                                            move: nothing,
                                                                            boxMouseenter: nothing,
                                                                            boxMouseleave: nothing,
                                                                            boxClick: nothing
                                                                          });
                      var self = this;
                      $("button.select").click(function () {
                                                   box.find(':selected')
                                                      .each(function () {
                                                                self.input.trigger('selectChoice',
                                                                                   [$(this), self]);
                                                            });
                                               });
                      $("button.deselect").click(function () {
                                                     deck.find(':selected')
                                                         .each(function () {
                                                                   self.deselectChoice($(this));
                                                               });
                                                 });
                  },
                  hide: nothing
                };

$(document).bind('yourlabsWidgetReady',
                 function() {
                     $('body').on('initialize',
                                  '.autocomplete-light-widget[data-widget-bootstrap=side-by-side]',
                                  function() {
                                      $(this).yourlabsWidget(ourWidget);
                                  });
                 });
