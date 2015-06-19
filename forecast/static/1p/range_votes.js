$(function () {
    var vote0 = $('#id_vote_0');
    var vote1 = $('#id_vote_1');


    var opts = {
        range: true,
        values: [0, 100],
        slide: function (event, ui) {
            $(vote0).val(ui.values[0]);
            $(vote1).val(ui.values[1]);

        }
    };

    opts.min = +$(vote0).attr('min');
    opts.max = +$(vote0).attr('max');

    $("#range_vote").slider(opts);
    //$(vote1).val($("#range_vote").slider("values", 0) +
    //" - " + $("#range_vote").slider("values", 1));
});
