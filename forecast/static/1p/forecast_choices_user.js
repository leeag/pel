$(document).ready(function () {
    var choices = $('#hideable-choices');
    var forecastType = $('#id_forecast_type');

    function triggerChoices() {
        if($(forecastType).val() == '1') {
            choices.show()
        } else {
            choices.hide()
        }
    }
    triggerChoices();

    $(forecastType).change(triggerChoices)
        .on('keyup keydown', function () { $(this).trigger('change') });

});

$(document).ready(function () {
   var counter = 2;


    $("#delete_last").click(function(){
            $('#removable-choice-'+counter).remove();
        if(counter >2) {
            counter--;
            if (counter < 3){
                 $("#delete_last").hide();
            }
        }
    });
    $("#add_another").click(function() {
    counter++;
    if (counter>2){
        $("#delete_last").show();
    }
        var element = '<p id="removable-choice-'+counter+'"><label for="id_forecastvotechoicefinite_set-' + counter + '-choice">Choice:' +
                '</label>' +
                '<input class="form-control input-sm" id="id_forecastvotechoicefinite_set-' +
                counter + '-choice" maxlength="150" name="forecastvotechoicefinite_set-' +
                counter + '-choice" type="text" />' +
                '<input id="id_forecastvotechoicefinite_set-' + counter +
                '-id" name="forecastvotechoicefinite_set-' + counter +
                '-id" type="hidden" />' +
               '<input id="id_forecastvotechoicefinite_set-' + counter +
                '-forecast_question" name="forecastvotechoicefinite_set-' +
                counter + '-forecast_question" type="hidden" /></p>';
        $("#id_forecastvotechoicefinite_set-TOTAL_FORMS").val(counter+1)

        $("#hideable-choices").append(element);
    });

});











