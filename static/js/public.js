(function ($) {
    var ua = navigator.userAgent.toLowerCase(),
        tips = function (img) {
            $('#tkl1,#tkl2,.bg').hide();
            return $('<div>', {
                style: 'position:fixed;left:0;top:0;z-index:999999999;width:100%;height:100%;background:url(' + img + ') no-repeat right top rgba(0,0,0,0.8);background-size:contain;',
                click: function () { $(this).remove(); }
            }).appendTo('body');
        };
    $.extend({
        tipsBrowser: function () {
            tips('/Public/images/tipsbrowser.png');
        },
        tipsShare: function () {
            tips('/Public/images/tipsshare.png');
        },
        openTbApp: function (url, jmp) {
            var jump_key = window['JUMP_KEY'] || '';
            $.tipsBrowser();
            // if (!jmp && /(iphone|ipad|ipod|ios)/i.test(ua)) {
            //     $.tipsBrowser();
            //     return;
            // }
            //window.location.href = '/jump?key=' + jump_key + '&go=' + encodeURIComponent(url);
        }
    });
})(jQuery);