/**
 * Created by Administrator on 2017/6/4.
 */
;window.onload = function () {
    $('.recaptcha span').show();
};
function fadeout_in(x) {
    $('.promote > div > div').fadeOut();
    $(x).fadeIn(1000);
}
function to_black() {
    $('.promote > div').fadeOut(2000);
    $('.black-screen').fadeIn();
}
function to_light(x) {
    $('.black-screen').fadeOut(2000);
    $(x).fadeIn(2000);
}
function to_repatriate() {
    to_black();
    setTimeout("to_light('.repatriate')", 3000);
    setTimeout("fadeout_in('.repatriate .zeroth')", 5000);
    setTimeout("fadeout_in('.repatriate .first')", 7500);
    setTimeout("fadeout_in('.repatriate .second')", 10000);
    setTimeout("fadeout_in('.repatriate .third')", 11200);
    setTimeout("fadeout_in('.repatriate .fourth')",12400);
    setTimeout("fadeout_in('.repatriate .fifth')", 13600);
    setTimeout("fadeout_in('.repatriate .sixth')", 14800);
    setTimeout("fadeout_in('.repatriate .seventh')", 16000);
    setTimeout("to_black()", 18000);
    setTimeout("to_light('.housekeeper')", 21000);
    setTimeout("fadeout_in('.housekeeper .zeroth')", 21000);
}
$(function () {
    $('body').css({'background':'url("../../static/wow/race/dwarf_81WJBCPNYZ5F1472070113187.jpg")', 'background-size':'cover'});
    $('.promote-start .next').click(function () {
        to_black();
        setTimeout("to_light('.goblin-single')", 3000);
    });
    $('.goblin-single .zeroth .left').click(function () {
        fadeout_in('.goblin-single .first');
    });
    $('.goblin-single .zeroth .right').click(function () {
        fadeout_in('.goblin-single .first');
        $('.goblin-single .first span').text('嘿，伙计，我知道你要说什么。刚才都是误会，我发誓！每天来我这的客人成千上百，有时候一不留神就没招待好其中几个。你不会怪我吧？好了，还是谈正事儿吧。你需要支付2个金币40个银币。（拉兹登克看着你。）');
    });
    $('.goblin-single .first .left').click(function () {
        to_repatriate();
    });
    $('.housekeeper .zeroth .right').click(function () {
        fadeout_in('.housekeeper .first');
    });
    $('.to-repatriate').click(function () {
        to_black();
        $('.goblin-single .zeroth').show();
        $('.goblin-single .zeroth span').show();
        $('.goblin-single .zeroth .left').text('知道。');
        $('.goblin-single .zeroth .right').show();
        $('.goblin-single .first span').text('拉兹登克最喜欢和明白人做生意！一共需要3个金币。');
        $('.repatriate .zeroth').text('又是这个倒霉鬼！伙计们，打起精神来！');
        $('.housekeeper .zeroth span').text('嘿，又是你！如果你还想找拉兹登克，恐怕得自己想办法了。我可以派人送你到暴风城。');
        $('.housekeeper .zeroth .left').text('好。');
        $('.housekeeper .zeroth .right').hide();
        setTimeout("to_light('.goblin-single')", 3000);
    });
    $('.goblin-single .first .right').click(function () {
        fadeout_in('.goblin-single .second');
        $('.sound1').attr('src', '../../static/wow/sound/LootCoinSmall.ogg');
    });
    $('.goblin-single .second .left').click(function () {
        fadeout_in('.goblin-single .third');
    });
    $('.goblin-single .next').click(function () {
        to_black();
        setTimeout("fadeout_in('.black-screen .zeroth')", 2500);
        setTimeout("to_light('.discuss')", 5000);
        setTimeout("fadeout_in('.discuss .first')", 7000);
        setTimeout("fadeout_in('.discuss .second')", 9500);
        setTimeout("fadeout_in('.discuss .third')", 14500);
        setTimeout("fadeout_in('.discuss .fourth')", 18000);
        setTimeout("fadeout_in('.discuss .fifth')", 20500);
        setTimeout("fadeout_in('.discuss .sixth')", 23000);
    });
    $('.discuss .next').click(function () {
        to_black();
        setTimeout("fadeout_in('.black-screen .first')", 2500);
        setTimeout("to_light('.envoy')", 5000);
        setTimeout("fadeout_in('.envoy .first')", 7000);
        setTimeout("fadeout_in('.envoy .second')", 9500);
        setTimeout("fadeout_in('.envoy .third')", 12000);
        setTimeout("fadeout_in('.envoy .fourth')", 16000);
        setTimeout("fadeout_in('.envoy .fifth')", 19000);
        setTimeout("fadeout_in('.envoy .sixth')", 22000);
    });
    $('.envoy .next').click(function () {
        to_black();
        setTimeout("to_light('.baine')", 3000);
        setTimeout("fadeout_in('.baine .zeroth')", 5000);
        setTimeout("fadeout_in('.baine .first')", 7500);
        setTimeout("fadeout_in('.baine .second')", 9500);
        setTimeout("fadeout_in('.baine .third')", 12000);
        setTimeout("fadeout_in('.baine .fourth')", 14500);
        setTimeout("fadeout_in('.baine .fifth')", 17000);
        setTimeout("fadeout_in('.baine .sixth')", 19000);
        setTimeout("fadeout_in('.baine .seventh')", 22500);
        setTimeout("fadeout_in('.baine .eighth')", 27500);
        setTimeout("fadeout_in('.baine .ninth')", 32500);
        setTimeout("fadeout_in('.baine .tenth')", 35500);
        setTimeout("fadeout_in('.baine .eleventh')", 39000);
        setTimeout("fadeout_in('.baine .twelfth')", 42000);
    });
    $('.baine .next').click(function () {
        to_black();
        setTimeout("fadeout_in('.black-screen .second')", 2500);
        setTimeout("to_light('.lich-king')", 5000);
        setTimeout("fadeout_in('.lich-king .first')", 7500);
        setTimeout("fadeout_in('.lich-king .second')", 10000);
        setTimeout("fadeout_in('.lich-king .third')", 12500);
        setTimeout("fadeout_in('.lich-king .fourth')", 15000);
    });
    $('.lich-king .fourth .left').click(function () {
        fadeout_in('.lich-king .fifth');
        setTimeout("fadeout_in('.lich-king .sixth')", 3000);
        setTimeout("to_repatriate()", 5000);
    });
    $('.lich-king .fourth .right').click(function () {
        fadeout_in('.lich-king .seventh');
    });
    $('.lich-king .next').click(function () {
        to_black();
        setTimeout("to_light('.promote-finish')", 3000);
    });
});