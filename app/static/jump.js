/**
 * Created by freyiz on 17-6-11.
 */
;function jump(arg) {
    $('.page-num').bind('input propertychange', function() {
        var val = $(this).val();
        if ((/^(\+|-)?\d+$/.test(val)) && val > 0 && val <= arg) {
            $('.jump').removeAttr('disabled').css('color', '#006dd0').addClass('active');
        } else {
            $('.jump').attr('disabled', 'disabled').css('color', 'gray').removeClass('active');
        }
        if (val > 99) {
            $(this).css('padding-left', '6px');
        }
        else if (val > 9) {
            $(this).css('padding-left', '10px');
        }
        else {
            $(this).css('padding-left', '14px')
        }
    });
}
