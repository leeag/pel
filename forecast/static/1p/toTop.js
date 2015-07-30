$(document).ready(function() {
    $(function () {
        $("#Go_Top").hide().removeAttr("href");
        if ($(window).scrollTop() >= "350") $("#Go_Top").fadeIn("slow")
        $(window).scroll(function () {
            if ($(window).scrollTop() <= "350") $("#Go_Top").fadeOut("slow")
            else $("#Go_Top").fadeIn("slow")
        });

        $("#Go_Bottom").hide().removeAttr("href");
        if ($(window).scrollTop() <= $(document).height() - "999") $("#Go_Bottom").fadeIn("slow")
        $(window).scroll(function () {
            if ($(window).scrollTop() >= $(document).height() - "999") $("#Go_Bottom").fadeOut("slow")
            else $("#Go_Bottom").fadeIn("slow")
        });

        $("#Go_Top").click(function () {
            $("html, body").animate({scrollTop: 0}, "slow")
        })
        $("#Go_Bottom").click(function () {
            $("html, body").animate({scrollTop: $(document).height()}, "slow")
        })
    });
});