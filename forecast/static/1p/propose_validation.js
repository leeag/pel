  $().ready(function () {
  $("#propose").validate({

    errorClass: "my-error-class",
    validClass: "my-valid-class",
    rules: {
        'forecastvotechoicefinite_set-0-choice': "required",
        'forecastvotechoicefinite_set-1-choice': "required",
    },

    messages: {
      'forecastvotechoicefinite_set-0-choice': "Please enter a choice",
      'forecastvotechoicefinite_set-1-choice': "Please enter a choice"

    }
  });
});