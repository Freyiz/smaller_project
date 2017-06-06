/**
 * Created by Administrator on 2017/6/5.
 */
;$(function() {
    var max = 300;
    $(".post-text").each(function() {
        text = $(this).text();
        sub = text.substr(0, max);
        $(this).attr({his: text, sub: sub});
        if (text.length > max) {
            $(this).html(sub).append("<a href='javascript:void(0)' class='text-toggle'>...展开</a>");
        }
    });
    $(".post-text").on("click", ".text-toggle", function() {
        var me = this;
        show = $(me).text() == '...展开';
        attr = show ? "his" : "sub";
        name = show ? "...收起" : '...展开';
        $(me).parent().each(function() {
            $(this).html($(this).attr(attr)).append($(me).text(name));
        });
    });
});
