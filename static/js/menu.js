$(document).ready(function() {
    var width = $(window).width();
    if (width < 720) {
        $("nav ul").hide();
        $('#pull').text('목록'); // 접힌 상태
    }
    $(window).resize(function() {
        var width = $(window).width();
        if (width > 720 && $("nav ul").is(":hidden")) {
            $("nav ul").removeAttr('style');
        } else if (width < 720 && $("nav ul").is(":visible")) {
            $("nav ul").hide();
            $('#pull').text('목록'); // 접힌 상태
        }
    });

    $("#pull").on('click', function(e) {
        e.preventDefault();
        $("nav ul").slideToggle(function() {
            if ($(this).is(':visible')) {
                $('#pull').text('△접기'); // 펼쳐진 상태
            } else {
                $('#pull').text('목록'); // 접힌 상태
            }
        });
    });
});
