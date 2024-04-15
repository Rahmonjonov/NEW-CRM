var today = new Date();
var yil = today.getFullYear();
var oy = today.getMonth();
var goal_type_global = document.getElementById("goal-type").value;
var data_user = [];

$.ajax({
    type: 'get',
    url: '/goal/get_users',
    success: function (data) {
        data_user = data;
    }
});

function setDateInput() {
    if (oy + 1 < 10) {
        document.getElementById("filter-date-goal").value = String(yil) + "-0" + String(oy + 1)
    } else {
        document.getElementById("filter-date-goal").value = String(yil) + "-" + String(oy + 1)
    }
}

setDateInput()

function insertGoalToTable(data, goal_type) {
    var table_body = document.getElementById("table_body")
    table_body.empty;
    var row_data = ""
    var i = 1
    var months = ["Yanvar", "Fevral", 'Mart', "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentiyabr", "Oktiyabr", "Noyabr", "Dekabr"];
    var sana = ""
    for (var dt of data) {
        if (goal_type === "Yillik") {
            sana = String(dt.yil)
        } else {
            sana = months[dt.oy] + " , " + String(dt.yil)
        }
        row_data += '<tr>\
                                <th scope="row">' + String(i) + '</th>\
                                <td>' + dt.user + '</td>\
                                <td>\
                                    <div class="progress">\
                                        <div class="progress-bar progress-bar-success progress-bar-striped progress-bar-animated"\
                                             role="progressbar" aria-valuenow="' + String(dt.foiz) + '" aria-valuemin="0" aria-valuemax="100"\
                                             style="width: ' + String(dt.foiz) + '%">\
                                            ' + String(dt.foiz) + '%\
                                        </div>\
                                    </div>\
                                </td>\
                                <td>' + String(dt.bajardi) + '</td>\
                                <td>' + String(dt.maqsad) + '</td>\
                                <td>' + sana + '</td>\
                            </tr>'

        i = i + 1
    }
    table_body.innerHTML = row_data
}

function get_goals_table() {
    var goal_type_yillik = document.getElementById("radio_4").checked;
    var goal_data_type_mijoz = document.getElementById("radio_6").checked;
    var goal_type = "Oylik"
    var goal_data_type = "Savdo"
    if (goal_type_yillik === true) {
        goal_type = "Yillik"
    }
    if (goal_data_type_mijoz === true) {
        goal_data_type = "Mijoz"
    }
    var sana = document.getElementById("filter-date-goal").value;
    var data = {
        goal_type: goal_type,
        goal_data_type: goal_data_type,
        sana: sana
    }
    $.ajax({
        type: "get",
        url: "/goal/get_goal_table",
        data: data,
        success: function (data) {
            insertGoalToTable(data, goal_type)
        }
    });

}

get_goals_table();

function sum_data_input() {
    var mijoz_summa = 0;
    var savdo_summa = 0;
    for (var dt of data_user) {
        var savdo = document.getElementById("savdo_input_" + String(dt.id)).value;
        var mijoz = document.getElementById("mijoz_input_" + String(dt.id)).value;
        if (mijoz === "") {
            mijoz = "0";
        }
        if (savdo === "") {
            savdo = "0";
        }
        mijoz_summa = mijoz_summa + parseInt(mijoz);
        savdo_summa = savdo_summa + parseInt(savdo);

    }
    document.getElementById("savdo-summa").innerHTML = String(savdo_summa);
    document.getElementById("client-count").innerHTML = String(mijoz_summa);
}

function number_input(e) {
    var text = e.value;
    if (isNaN(text)) {
        text = text.substring(0, text.length - 1);
        e.value = text;
    }
    sum_data_input();
}

function get_goals(goal_type, yil, oy) {
    $.ajax({
        type: "get",
        url: "/goal/get_goal",
        data: {goal_type: goal_type, yil: yil, oy: oy},
        success: function (data) {
            if (data.length > 0) {
                for (var dt of data) {
                    document.getElementById("savdo_input_" + String(dt.user)).value = dt.savdo;
                    document.getElementById("mijoz_input_" + String(dt.user)).value = dt.mijoz;
                }
                sum_data_input();
            } else {
                for (var dt2 of data_user) {
                    document.getElementById("savdo_input_" + String(dt2.id)).value = "0";
                    document.getElementById("mijoz_input_" + String(dt2.id)).value = "0";
                }
                sum_data_input();
            }
        },
        error: function (er) {

        }


    });

}

function submitHandler() {
    var goal_type = document.getElementById("goal-type").value;
    var data_send = [];
    for (var dt of data_user) {
        var savdo = document.getElementById("savdo_input_" + String(dt.id)).value;
        var mijoz = document.getElementById("mijoz_input_" + String(dt.id)).value;
        dt = {
            "user": dt.id,
            "gaol_type": goal_type,
            "savdo": savdo,
            "mijoz": mijoz,
            "yil": yil,
            "oy": oy
        };
        data_send.push(dt);
    }
    var dt_json = JSON.stringify(data_send);
    $.ajax({
        type: "post",
        url: "/goal/add_goal",
        data_type: 'json',
        data: {csrfmiddlewaretoken: csrftoken, data: dt_json},
        success: function (data) {
            if (data.status === 1) {
                $(".alerttop").fadeToggle(350);
                setTimeout(function () {
                    $(".alerttop").fadeToggle(350);
                }, 5000);
            }
        },
        error: function (err) {
            console.log(err);
        }
    });

}

get_goals(goal_type_global, yil, oy);

function date_minus() {
    var months = ["Yanvar", "Febvral", 'Mart', "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentiyabr", "Oktiyabr", "Noyabr", "Dekabr"];
    var goal_type = document.getElementById("goal-type").value;
    var date_input = document.getElementById("date_input");
    if (goal_type === "1") {
        if (today.getFullYear() < yil) {
            yil = yil - 1;
            date_input.value = String(yil);
            get_goals(goal_type, yil, oy);
        }
    } else {
        if ((today.getFullYear() === yil && today.getMonth() < oy) || (today.getFullYear() < yil)) {
            oy = oy - 1;
            if (oy === -1) {
                oy = 11;
                yil = yil - 1;
            }
            date_input.value = String(months[oy]) + " , " + String(yil);
            get_goals(goal_type, yil, oy);
        }
    }


}

function date_plus() {
    var months = ["Yanvar", "Febvral", 'Mart', "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentiyabr", "Oktiyabr", "Noyabr", "Dekabr"];
    var goal_type = document.getElementById("goal-type").value;
    var date_input = document.getElementById("date_input");
    if (goal_type === "1") {
        if (today.getFullYear() <= yil) {
            yil = yil + 1;
            date_input.value = String(yil);
            get_goals(goal_type, yil, oy);
        }
    } else {
        if ((today.getFullYear() === yil && today.getMonth() <= oy) || (today.getFullYear() < yil)) {
            oy = oy + 1;
            if (oy === 12) {
                oy = 0;
                yil = yil + 1;
            }
            date_input.value = String(months[oy]) + " , " + String(yil);
            get_goals(goal_type, yil, oy);
        }
    }


}

function change_goal_type() {
    var goal_type = document.getElementById("goal-type").value;
    var months = ["Yanvar", "Febvral", 'Mart', "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentiyabr", "Oktiyabr", "Noyabr", "Dekabr"];
    var date_input = document.getElementById("date_input");
    if (goal_type === "1") {
        date_input.value = String(yil);
        get_goals(goal_type, yil, oy);
    } else {
        date_input.value = String(months[oy]) + " , " + String(yil);
        get_goals(goal_type, yil, oy);
    }


}

