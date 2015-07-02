  $().ready(function () {
  $("#signupForm").validate({

    errorClass: "my-error-class",
    validClass: "my-valid-class",
    rules: {
      name: "required",
      surname: "required",
      //username: {
      //  required: true,
      //  minlength: 2
      //},
      password: {
        required: true,
        minlength: 5
      },
      password_conf: {
        required: true,
        minlength: 5,
        equalTo: "#id_password",
      },
      email: {
        required: true,
        email: true
      },
      country: "required",
      agree_with_terms: "required",
      captcha: "required",
    },
    messages: {
      name: "Please enter your name",
      surname: "Please enter your surname",
      username: {
        required: "Please enter a username",
        minlength: "Your username must consist of at least 2 characters"
      },
      password: {
        required: "Please provide a password",
        minlength: "Your password must be at least 5 characters long"
      },
      password_conf: {
        required: "Please provide a password",
        minlength: "Your password must be at least 5 characters long",
        equalTo: "Please enter the same password as above"
      },
      email: "Please enter a valid email address",
      country: "Please select a country",
      agree_with_terms: "Please accept our policy"
    }
  });
});