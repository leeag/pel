$(document).ready(function () {
    var choices = $('#choices-group');
    var forecastType = $('#id_forecast_type');
    var range = $('#id_min,#id_max').closest('.row');

    function triggerChoices() {
        if($(forecastType).val() == '1') {
            choices.show()
        } else {
            choices.hide()
        }
    }

    triggerChoices();

    function rangeShow() {
        if ($(forecastType).val() == '3') {
            range.show()
        } else {
            range.hide()
        }
    }

    rangeShow();


    $(forecastType).change(triggerChoices)
        .on('keyup keydown', function () { $(this).trigger('change') });
    $(forecastType).change(rangeShow)
        .on('keyup keydown', function () { $(this).trigger('change') });
});