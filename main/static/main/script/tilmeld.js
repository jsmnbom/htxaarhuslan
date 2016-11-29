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
        if ($(this).attr('data-name') !== undefined) {
            if ($(this).attr('data-name') !== '') {
                $(this).addClass('occupied');
                var url = $(this).attr('data-url');
                var name = $(this).attr('data-name');
                var grade = $(this).attr('data-grade');
                $(this).qtip({
                    content: {
                        text: '<a href="' + url + '">' + name + '</a>' + '<br>' + '<span>' + grade + '</span>'
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
                $(this).addClass('availible')
            }
        }
    });

    function showhideform() {
        if ($('input[name="seat"]').val() != seat) {
            $('.seats form#tilmeld').slideDown()
        } else {
            $('.seats form#tilmeld').slideUp()
        }
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
            if ($(this).hasClass('availible')) {
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
});