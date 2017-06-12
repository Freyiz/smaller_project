/**
 * Created by Administrator on 2017/6/4.
 */
;$(function () {
    $('body').css({'background':'url("../../static/wow/race/orc_F6NZ76C2G2RD1472070211038.jpg")', 'background-size':'cover'});
    $('.wow-tab a').click(function () {
        $('.wow-tab a').removeClass('active');
        $(this).addClass('active');
        $('#wow-music iframe').attr('src', '');
    });
    $('.wow-tab a:last-child').click(function () {
        $('#wow-music iframe').attr('src', 'http://www.expoon.com/16074/panorama');
    });
    var vd = document.getElementById('wow-video');
    vd.addEventListener('play', function () {
        $('.wow-control').hide();
        $('.wow-control a').hide();
    });
    vd.addEventListener('pause', function () {
        $('.wow-control').show();
        $('.wow-control a').show();
    });
    $('#wow-video').click(function () {
        if (vd.paused) {
            vd.play();
            $('.wow-control').hide();
            $('.wow-control a').hide();
        } else {
            vd.pause();
            $('.wow-control').show();
            $('.wow-control a').show();
        }
    });
    $('.wow-control').click(function () {
        vd.play();
        $('.wow-control').hide();
        $('.wow-control a').hide();
        $('.wow-control img').hide();
    });
    $('.movie-tab div').click(function () {
        $('.movie-tab div').removeClass('active');
        $(this).addClass('active');
        $('.wow-control').show();
        $('.wow-control a').show();
        $('.wow-control img').show();
    });
    var youku = 'off';
    $('.to-youku a').click(function () {
        youku = 'on';
        $('.to-youku').hide();
        $('.quit-youku').show();
        $('.movie-tab div').removeClass('active');
        $('.wow-60').addClass('active');
        vd.src = '';
        $('.youku.yk1').show();
    });
    $('.quit-youku').click(function () {
        youku = 'off';
        $(this).hide();
        $('.to-youku').show();
        $('.movie-tab div').removeClass('active');
        $('.wow-60').addClass('active');
        vd.src = 'http://wow-movie.herokuapp.com/static/WOW_Intro.m4v';
        $('.youku').hide();
        $('.wow-control a').css('margin-top', '19%');
        $('.wow-control img').attr('src', '../static/wow/logo/world_of_warcraft.png');
    });
    $('.wow-60').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk1').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/WOW_Intro.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/world_of_warcraft.png');
        }
    });
    $('.wow-70').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk2').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/WOW_Intro_BC.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/the_burning_crusade.png');
        }
    });
    $('.wow-80').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk3').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/WOW_Intro_LK.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/wrath_of_the_LICH_KING.png');
        }
    });
    $('.wow-85').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk4').show();
        } else {
            vd.src = 'http://wow-movie2.herokuapp.com/static/WOW_Intro_CTM.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/CATACLYSM.png');
        }
    });
    $('.wow-90').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk5').show();
        } else {
            vd.src = 'http://wow-movie2.herokuapp.com/static/WOW_Intro_MOP.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/mists_of_PANDARIA.png');
        }
    });
    $('.wow-100').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk6').show();
        } else {
            vd.src = 'http://wow-movie2.herokuapp.com/static/WOW_Intro_WOD_1280.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/warlords_of_DRAENOR.png');
        }
    });
    $('.wow-110').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk7').show();
        } else {
            vd.src = 'http://wow-movie2.herokuapp.com/static/WOW_Intro_ROL_1280.m4v';
            $('.wow-control img').attr('src', '../static/wow/logo/rise_of_the_legion.png');
        }
    });
    $('.wow-lichking').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk8').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/FotLK.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-wrathgate').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk9').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/Wrathgate.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-worgen').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk10').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/Worgen.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-goblin').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk11').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/Goblin.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-deathwing').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk12').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/DSI_Act4.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-pandaren').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk13').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/MOP_BR.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-wra').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk14').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/MOP_WRA.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-wrh').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk15').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/MOP_WRH.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-jade').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk16').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/MOP_JADE.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.wow-ghellscream').click(function () {
        if (youku === 'on') {
            $('.youku').hide();
            $('.youku.yk17').show();
        } else {
            vd.src = 'http://wow-movie.herokuapp.com/static/ORO_Horde.m4v';
            $('.wow-control img').hide();
        }
    });
    $('.intro').click(function () {
        $('.wow-control a').css('margin-top', '19%');
    });
    $('.nointro').click(function () {
        $('.wow-control a').css('margin-top', '25%');
    });
});