$(document).ready(function () {
    $(".header .title").fitText(1.9);
    $(".header .nav a").fitText(0.7);

    // Cookie law stuff
    window.cookieconsent.initialise({
        "palette": {
            "popup": {
                "background": "#363032",
                "text": "#ffffff"
            },
            "button": {
                "background": "#d33e20",
                "text": "#ffffff"
            }
        },
        "theme": "edgeless",
        "position": "bottom-left",
        "content": {
            "message": "Denne hjemmeside bruger cookies til at sikre, at du får den bedste oplevelse på vores hjemmeside.",
            "dismiss": "Forstået!",
            "link": "Lær mere",
            "href": "/privatliv"
        }
    });

    // Hide edit profile until you click button
    var hidden = false;
    $('.box#profile .hide').hide();
    if ($('.box#profile #edit.hide').length) {
        hidden = true
    }
    $('.box#profile form input[type="submit"]').click(function (e) {
        if (hidden) {
            e.preventDefault();
            $('.box#profile #show').slideUp();
            $('.box#profile #edit').slideDown();
            $('.box#profile form input[type="submit"]').val('Gem profil');
            hidden = false
        }
        setTimeout(function () {
            $(window).resize()
        }, 500);
    });

    // Proper file upload (make it so you can see which file you've selected, even if we do the fancy label thing we did
    var input = $('div.file input[type="file"]'),
        label = $('div.file .choose'),
        labelText = label.html();
    input.on('change', function (e) {
        var fileName = e.target.value.split('\\').pop();

        if (fileName) {
            label.html(fileName);
        } else {
            label.html(labelText);
        }
    });


    // Footer spacer
    $(window).resize(function () {
        var spacer = $('.spacer');
        spacer.height($('.sidebar').height() - $('.page').height() + spacer.height() + $(window).height() * 0.05)
        $('.footer').show();
    });
    $(window).on('orientationchange', function () {
        $(window).resize();
    });
    setTimeout(function () {
        $(window).resize()
    }, 500);

    // Show input helptext only when input is focussed
    $('form span.helptext').each(function () {
        var input = $(this).prevAll('input').slice(0,1);
        var helpText = $(this);
        input.focus(function () {
            helpText.slideDown()
        }).blur(function () {
            helpText.slideUp()
        });
    });

    /* Countdown clock (if tilmelding isn't open yet) */
    if ($('h3#notopen').length) {
        var div = $('div#countdown');
        var remainingTimeMillis = parseInt(div.attr('data-opens')) * 1000;
        var now = new Date();
        var opens = new Date(now.getTime() + remainingTimeMillis);
        console.log(remainingTimeMillis, now, opens);
        div.countdown(opens, function (event) {
            if (event.offset.totalDays >= 1) {
                $(this).html(event.strftime('%-D %!D:dag,dage;, %H:%M:%S'));
            } else {
                $(this).html(event.strftime('%H:%M:%S'));
            }
        });
        setTimeout(function () {
            $('div#countdown').fitText(0.6)
        }, 500);
    }

    /* Pretty tilmeldlist table */
    var table = $('#tilmeldlist').find('table');
    if (table.length) {
        table.DataTable({
            paging: false,
            responsive: {
                details: {
                    display: $.fn.dataTable.Responsive.display.childRowImmediate,
                    type: ''
                }
            },
            language: {
                "sProcessing": "Henter...",
                "sLengthMenu": "Vis _MENU_ tilmeldte",
                "sZeroRecords": "Ingen tilmeldte matcher s&oslash;gningen",
                "sInfo": "Viser _START_ til _END_ af _TOTAL_ tilmeldte",
                "sInfoEmpty": "Viser 0 til 0 af 0 tilmeldte",
                "sInfoFiltered": "(filtreret fra _MAX_ tilmeldte)",
                "sInfoPostFix": "",
                "sSearch": "S&oslash;g:",
                "sUrl": "",
                "oPaginate": {
                    "sFirst": "F&oslash;rste",
                    "sPrevious": "Forrige",
                    "sNext": "N&aelig;ste",
                    "sLast": "Sidste"
                }
            }
        })
    }

    // Tournament things
    $('.game > a').click(function(e) {
        e.preventDefault();
        $(this).closest('div').find('div').slideToggle();
    });
});

// Make iframes not flash on load.
// From https://css-tricks.com/prevent-white-flash-iframe/
(function () {
    var div = document.createElement('div'),
        ref = document.getElementsByTagName('base')[0] ||
            document.getElementsByTagName('script')[0];

    div.innerHTML = '&shy;<style> div#discord iframe { visibility: hidden; } </style>';

    ref.parentNode.insertBefore(div, ref);

    window.onload = function () {
        div.parentNode.removeChild(div);
    }
})();
