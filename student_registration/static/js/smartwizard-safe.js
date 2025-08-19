// Prevent SmartWizard initialization errors when called on empty selections.
// If the plugin is invoked on a jQuery set with no matched elements it would
// previously throw an exception inside jQuery's data handling because
// `this[0]` was undefined.  We wrap the original plugin and simply return the
// jQuery object when there is nothing to initialize.
(function ($) {
  if ($.fn && $.fn.smartWizard) {
    var original = $.fn.smartWizard;
    $.fn.smartWizard = function () {
      if (this.length === 0) {
        // Gracefully handle empty selections.
        return this;
      }
      return original.apply(this, arguments);
    };
  }
})(jQuery);

