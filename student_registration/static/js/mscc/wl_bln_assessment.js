$(document).ready(function () {
    function updateTotals() {
        var totals = {};

        $('[data-wl-bln-component="1"]').each(function () {
            var totalField = $(this).data('wl-bln-total-target');
            var value = parseInt($(this).val(), 10);

            if (!totals[totalField]) {
                totals[totalField] = 0;
            }

            if (!isNaN(value)) {
                totals[totalField] += value;
            }
        });

        $('[data-wl-bln-total-field]').each(function () {
            var totalField = $(this).data('wl-bln-total-field');
            var totalValue = totals[totalField] || 0;
            $(this).val(totalValue);
            $('[data-wl-bln-total-display="' + totalField + '"]').text(totalValue);
        });
    }

    updateTotals();

    $(document).on('input change', '[data-wl-bln-component="1"]', function () {
        updateTotals();
    });
});
