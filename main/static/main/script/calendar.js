$(document).ready(function () {
    var calendar = $('#calendar');
    calendar.fullCalendar({
        eventSources: [
            {
                url: '/calendar/tournament.json',
                color: '#4fb0d7'
            },
            {
                url: '/calendar/misc.json',
                color: '#d33e20'
            }
        ],
        loading: function (bool) {
            $('#calendar_loading').toggle(bool);
        },
        defaultView: 'lan',
        views: {
            lan: {
                type: 'list',
                duration: {days: 3},
                buttonText: 'lan'
            }
        },
        defaultDate: calendar.attr('data-date'),
        header: false,
        firstDay: 1,
        timezone: 'local'
    });
});