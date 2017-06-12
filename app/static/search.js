/**
 * Created by freyiz on 17-6-11.
 */
;$(function () {
    var accord = document.getElementById('search').getAttribute('arg');
    $.getJSON($SCRIPT_ROOT + '/accord', {accord:accord} , function (data) {});
    $('.accord-tab a').click(function () {
        accord = $(this).attr('name');
        $('.accord-tab a').removeClass('active');
        $(this).addClass('active');
        $('.keywords').attr('placeholder', accord).val('');
        $.getJSON($SCRIPT_ROOT + '/accord', {accord:accord} , function (data) {});
        $('.search').attr('disabled', 'disabled').css('color', 'gray').removeClass('active');
    });
    $('.keywords').bind('input propertychange', function() {
        var val = $(this).val();
        if (/^\s*$/.test(val)) {
            $('.search').attr('disabled', 'disabled').css('color', 'gray').removeClass('active');
        } else {
            $('.search').removeAttr('disabled').css('color', '#006dd0').addClass('active');
        }
    }).focus(function () {
        $('.keywords').attr('placeholder', '');
    }).focusout(function () {
        $('.keywords').attr('placeholder', accord);
    });
});