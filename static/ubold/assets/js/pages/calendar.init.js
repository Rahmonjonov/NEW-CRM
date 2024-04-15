function getCSRFToken() {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, 10) == ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}
!function (l) {
    $.ajax({
        type: 'get',
        url: '/getcalendar/',
        success: function (data) {
            // console.log(data);
            var events = data['calendars'];
            "use strict";

            function e() {
                this.$body = l("body"),
                this.$modal = l("#event-modal"),
                this.$calendar = l("#calendar"),
                this.$formEvent = l("#form-event"),
                this.$btnNewEvent = l("#btn-new-event"),
                this.$btnDeleteEvent = l("#btn-delete-event"),
                this.$btnSaveEvent = l("#btn-save-event"),
                this.$modalTitle = l("#modal-title"),
                this.$userName = l("#user_name"),
                this.$calendarObj = null,
                this.$selectedEvent = null,
                this.$newEventData = null
            }

            e.prototype.onEventClick = function (e) {
                this.$formEvent[0].reset(),
                this.$formEvent.removeClass("was-validated"),
                this.$newEventData = null,
                this.$btnDeleteEvent.show(),
                this.$modalTitle.text("Hodisalarni taxrirlash"),
                this.$userName.text("Hodisalarni taxrirlash"),
                this.$modal.modal({backdrop: "static"}),
                this.$selectedEvent = e.event,
                title = l("#event-title").val(this.$selectedEvent.title),
                cat = l("#event-category").val(this.$selectedEvent.classNames[0]),

                l(a.$btnSaveEvent.on("click", function (e) {
                    var csrfToken = getCSRFToken();
                    // var id = a.$selectedEvent['_def']['publicId'];
                    var dt = JSON.stringify({
                        id: a.$selectedEvent['_def']['publicId'],
                        user: l("#event-user").val(),
                        title: l("#event-title").val(),
                        start: l("#event-time").val(),
                        className: l("#event-category").val()
                    });
                    // console.log(id);

                    $.ajax({
                        headers: {"X-CSRFToken": csrfToken},
                        type: "POST",
                        url: `/editevent/`,
                        data: dt,
                    });
                    var n = {
                        title: l("#event-title").val(),
                        start: l("#event-time").val(),
                        className: l("#event-category").val()
                    };
                    a.$selectedEvent.remove(),
                    a.$calendarObj.addEvent(n);
                }))
            }, e.prototype.onSelect = function (e) {
                this.$formEvent[0].reset(),
                this.$formEvent.removeClass("was-validated"),
                this.$selectedEvent = null,
                this.$newEventData = e,
                this.$btnDeleteEvent.hide(),
                this.$modalTitle.text("Yangi hodisa qo'shish"),
                this.$modal.modal({backdrop: "static"}),
                this.$calendarObj.unselect()
            }, e.prototype.init = function () {
                var e = new Date(l.now());
                new FullCalendarInteraction.Draggable(document.getElementById("external-events"), {
                    itemSelector: ".external-event",
                    eventData: function (e) {
                        return {title: e.innerText,className: l(e).data("class")}
                    }
                });
                var t = [];
                for (let dt of events) {
                    console.log(dt.user, 'll')
                    var br = {
                        id: String(dt.id),
                        title: String(dt.user) + String(dt.event),
                        start: String(dt.date),
                        className: String(dt.color),
                        // user: String(dt.user)
                    };
                    t.push(br);
                }
                a = this;
                a.$calendarObj = new FullCalendar.Calendar(a.$calendar[0], {
                    plugins: ["bootstrap", "interaction", "dayGrid", "timeGrid", "list"],
                    slotDuration: "00:15:00",
                    minTime: "08:00:00",
                    maxTime: "19:00:00",
                    themeSystem: "bootstrap",
                    bootstrapFontAwesome: !1,
                    buttonText: {
                        today: "Today",
                        month: "Month",
                        week: "Week",
                        day: "Day",
                        list: "List",
                        prev: "Prev",
                        next: "Next"
                    },
                    defaultView: "dayGridMonth",
                    handleWindowResize: !0,
                    height: l(window).height() - 200,
                    header: {
                        left: "prev,next today",
                        center: "title",
                        right: "dayGridMonth,timeGridWeek,timeGridDay,listMonth"
                    },
                    events: t,
                    editable: !0,
                    droppable: !0,
                    eventLimit: !0,
                    selectable: !0,
                    dateClick: function (e) {
                        a.onSelect(e)
                    },
                    eventClick: function (e) {
                        a.onEventClick(e)
                    }
                }), a.$calendarObj.render(), a.$btnNewEvent.on("click", function (e) {
                    a.onSelect({date: new Date, allDay: !0})
                }), a.$formEvent.on("submit", function (e) {
                    e.preventDefault();
                    var t = a.$formEvent[0];
                    if (t.checkValidity()) {
                        if (a.$selectedEvent)
                            a.$selectedEvent.setProp("title", l("#event-title").val()),
                            a.$selectedEvent.setProp("classNames", [l("#event-category").val()]);
                        else {
                            var n = {
                                title: l("#event-title").val(),
                                start: a.$newEventData.date,
                                className: l("#event-category").val()
                            };
                            var csrfToken = getCSRFToken();
                            var dt = JSON.stringify({
                                user: l("#event-user").val(),
                                title: l("#event-title").val(),
                                start: l("#event-time").val(),
                                className: l("#event-category").val()
                            });
                            // location.reload();
                            // console.log('as');
                            // a.$selectedEvent = null,
                            $.ajax({
                                headers: {"X-CSRFToken": csrfToken},
                                type: "POST",
                                url: `/postevent/`,
                                data: dt,
                            });
                            console.log("add")
                            // a.$calendarObj.addEvent(n)
                            location.reload();
                        }
                        // a.$selectedEvent.remove(),
                        a.$modal.modal("hide")
                    } else e.stopPropagation(), t.classList.add("was-validated")
                }), l(a.$btnDeleteEvent.on("click", function (e) {
                    a.$selectedEvent && (a.$selectedEvent.remove(),
                        id = a.$selectedEvent['_def']['publicId'],
                        // console.log(a.$selectedEvent),
                        // console.log(id),
                        // console.log(a.$selectedEvent['defId']),
                        $.ajax({
                            type: 'GET',
                            url: `/delevent/?id=${id}`
                        }),
                        a.$selectedEvent = null,
                        a.$modal.modal("hide"))
                }))
            },
                l.CalendarApp = new e,
                l.CalendarApp.Constructor = e,
                (window.jQuery),
                window.jQuery.CalendarApp.init()
        }
    });
}(window.jQuery);
// function () {
//     "use strict";
//     window.jQuery.CalendarApp.init()
// }();