/**
 * Created by freyiz on 17-6-11.
 */
;$(function () {
    var accord = document.getElementById('search').getAttribute('arg');
    $.getJSON($SCRIPT_ROOT + '/accord', {accord:accord} , function (data) {});
    var keywords = document.getElementById('search').getAttribute('arg2').split(' '), select = '.' + accord;
    var color = document.getElementById('search').getAttribute('arg3');
    for (var i=0; i<keywords.length; i++) {
        var keyword = keywords[i];
        if (keyword !== '') {
            var reg = new RegExp(keyword + "(?=[^<>]*<)" , "ig" );
            $(select).each(function () {
                $(this).html($(this).html().replace(reg,"<span style='color:" + color + "'>" + keyword + "</span>"));
            })
        }
    }
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
            $('.search').removeAttr('disabled').css('color', color).addClass('active');
        }
    }).focus(function () {
        $('.keywords').attr('placeholder', '');
    }).focusout(function () {
        $('.keywords').attr('placeholder', accord);
    });
});
