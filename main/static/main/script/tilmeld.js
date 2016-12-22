$(document).ready(function () {
    var tabletd = $('.seats table td');
    $(window).resize(function () {
        var m = -1;
        tabletd.each(function () {
            var h = $(this).width();
            if (h > m) {
                m = h
            }
        });
        var s = m / 3;
        $('.seats table td').css({height: m, fontSize: s})
    }, 200).resize();

    tabletd.each(function () {
        if ($(this).attr('role') == 'button') {
            if ($(this).attr('data-name')) {
                $(this).addClass('occupied');
                var url = $(this).attr('data-url');
                var name = $(this).attr('data-name');
                var username = $(this).attr('data-username');
                var grade = $(this).attr('data-grade');
                var thumbnail = $(this).attr('data-thumbnail');

                var content = '';
                if (thumbnail) {
                    content += '<img src="' + thumbnail + '" />'
                }
                content += '<a href="' + url + '">' + name + '</a>' + '<br>';
                content += '<span>' + username + '<span>&nbsp(' + grade + ')</span></span>';

                $(this).qtip({
                    content: {
                        text: content
                    },
                    position: {
                        my: "left center",
                        at: 'right center',
                        viewport: true
                    },
                    style: {
                        classes: "qtip-seat"
                    },
                    events: {
                        visible: function (event, api) {
                            $(event.originalEvent.target).addClass('open')
                        },
                        hide: function (event, api) {
                            $(event.originalEvent.target).removeClass('open')
                        }
                    }
                });
            } else {
                $(this).addClass('available')
            }
        }
    });

    function showhideform() {
        if ($('input[name="seat"]').val() != seat) {
            $('.seats form#tilmeld').slideDown()
        } else {
            $('.seats form#tilmeld').slideUp()
        }
        $(window).resize();
    }

    var seat = $('.seats h4#current').attr('data-seat');

    if (seat != undefined) {
        $('input[name="seat"]').val(seat);
        $('.seats form#tilmeld').hide()
    }

    tabletd.click(function () {
        if ($(this).hasClass('selected')) {
            $('.seats td').removeClass('selected');
            if (seat) {
                $('input[name="seat"]').val(seat)
            } else {
                $('input[name="seat"]').val('')
            }
        } else {
            $('.seats td').removeClass('selected');
            if ($(this).hasClass('available')) {
                $(this).addClass('selected');
                $('input[name="seat"]').val($(this).text())
            } else if ($(this).hasClass('current')) {
                $('input[name="seat"]').val($(this).text())
            } else {
                $('input[name="seat"]').val(seat);
                if ($(this).hasClass('open')) {
                    window.location.href = $(this).attr('data-url');
                }
            }
        }
        showhideform()
    });

    $('.seats a.button#reset').click(function (e) {
        e.preventDefault();
        $('.seats table td').removeClass('selected');
        $('input[name="seat"]').val('');
        showhideform()
    });

    var paytype = $('.seats form#tilmeld div#paytype');

    function select(input) {
        paytype.find('label').removeClass('selected');
        paytype.find('label[for="' + $(input).attr('id') + '"]').addClass('selected');
    }

    select(paytype.find('input[type=radio]:checked'));

    $(window).resize(function () {
        var inputs = paytype.find('input');
        paytype.find('span').width(paytype.width() / inputs.length - 3);
        inputs.change(function () {
            select(this)
        });
    });
    setTimeout(function () {
        $(window).resize();
    }, 200);

    vex.dialog.buttons.YES.text = 'Ja';
    vex.dialog.buttons.NO.text = 'Nej';

    // Frameld dialog
    $('form#frameld').on('submit', function (e) {
        e.preventDefault();
        vex.dialog.confirm({
            message: 'Er du sikker på at du vil framelde dig fra LAN? Hvis du er på nogle hold der er meldt til turneringer vil de automatisk blive afmeldt, da du ikke længere kommer. Hvis du bare ønsker at skifte plads, skal du trykke på Nej og derefter vælge en ny plads.',
            callback: function (value) {
                if (value) {
                    e.target.submit();
                }
            },
            className: 'vex-theme-plain'
        });
    });
});