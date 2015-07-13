$(document).ready(function () {
    var choices = $('#choices-group');
    var forecastType = $('#id_forecast_type');
    var range = $('#id_min,#id_max').closest('.row');
    var finite = $('#forecastvotechoicefinite_set-group');

    function triggerChoices() {
        if($(forecastType).val() == '1') {
            choices.show()
        } else {
            choices.hide()
        }
    }

    triggerChoices();

    function triggerFinite() {
        if($(forecastType).val() == '1') {
            finite.show()
        } else {
            finite.hide()
        }
    }

    triggerFinite();

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
    $(forecastType).change(triggerFinite)
        .on('keyup keydown', function () { $(this).trigger('change') });
    $(forecastType).change(rangeShow)
        .on('keyup keydown', function () { $(this).trigger('change') });
});