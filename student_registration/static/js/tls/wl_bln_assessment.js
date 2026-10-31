$(document).ready(function () {
    function calculateTotalForField(totalField) {
        var total = 0;

        $('[data-wl-bln-component="1"][data-wl-bln-total-target="' + totalField + '"]').each(function () {
            var value = parseFloat($(this).val());

            if (!isNaN(value)) {
                total += value;
            }
        });

        return total;
    }

    function renderTotal(totalField) {
        var formattedTotal = calculateTotalForField(totalField).toFixed(2);
        $('[data-wl-bln-total-field="' + totalField + '"]').val(formattedTotal);
        $('[data-wl-bln-total-display="' + totalField + '"]').text(formattedTotal);
    }

    function updateTotals() {
        $('[data-wl-bln-total-field]').each(function () {
            renderTotal($(this).data('wl-bln-total-field'));
        });
    }

    updateTotals();

    $(document).on('input change keyup', '[data-wl-bln-component="1"]', function () {
        renderTotal($(this).data('wl-bln-total-target'));
    });
});
