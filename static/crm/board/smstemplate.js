let typingTimer;
let doneTypingInterval = 500;
let $searchbar = $('#searchlead');
let selected_leads = []
let searched_leads = []
let bayramVaBoshqalar = "Bayram va boshqalar"

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function has_element(element) {
    return selected_leads.findIndex(i => i.id === element.id) !== -1
}

function isnull(val) {
    return (val === null) ? '' : val;
}

$(document).ready(function () {
    doneTyping()

    $searchbar.on('keyup', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });

    $searchbar.on('keydown', function () {
        clearTimeout(typingTimer);
    });

    $("#smstype").change(function () {
        if ($(this).val() === bayramVaBoshqalar) {
            $('.sms_optional').slideDown(200)
        } else {
            $('.sms_optional').slideUp(200)
        }
    })

    function doneTyping() {
        search_leads()
    }

    $("button[name=filter]").click(function () {
        filter_leads()
    })

    function add_if_no_1(element) {
        if (!has_element(element)) {
            selected_leads.push(element)
            appent_tbody1(element)
        }
    }

    $("#table1").on('click', '[data-pk]', function () {
        $(this).closest('tr').remove()
        let pk = parseInt($(this).attr('data-pk'))
        let index = selected_leads.findIndex(i => i.id === pk)
        push_if_no(selected_leads[index])
        selected_leads.splice(index, 1)
        update_labels()
        display_table2()
    });

    $("#table2").on('click', '[data-pk]', function () {
        let pk = parseInt($(this).attr('data-pk'))
        let index = searched_leads.findIndex(i => i.id === pk)
        add_if_no_1(searched_leads[index])
        searched_leads.splice(index, 1)
        $(this).closest('tr').remove()
        update_labels()

    });

    function push_if_no(element) {
        let index = searched_leads.findIndex(i => i.id === element.id)
        if (index === -1) {
            searched_leads.unshift(element)
        }
    }

    function update_labels() {
        $('#selected_label').html(`Tanlangan leadlar ${selected_leads.length} ta`)
    }

    function appent_tbody1(element) {
        $("#table1 tbody").append(
            `<tr>
                    <td>${element.name}</td>
                    <td>${isnull(element.surname)}</td>
                    <td>${isnull(element.price)}</td>
                    <td>${isnull(element.phone)}</td>
                    <td> <button data-pk="${element.id}" type="button"
                    class="btn btn-circle btn-danger btn-xs mr-10"><i
                    class="mdi mdi-close mdi-24px"></i></button>
                    </td>
            </tr>`
        );
    }

    function appent_tbody2(element) {
        $("#table2 tbody").append(
            `<tr>
                <td>
                    <button type="button" data-pk="${element.id}"
                    class="btn btn-circle btn-success btn-xs mr-15"><i
                    class="mdi mdi-arrow-left mdi-24px"></i></button>
                    ${element.name}
                </td>
                <td>${isnull(element.phone)}</td>
            </tr>`
        );
    }

    function display_table2() {
        $("#table2 tbody").html("");
        for (const lead of searched_leads) {
            if (!has_element(lead))
                appent_tbody2(lead)
        }
    }

    function filter_leads() {
        let pole_list = []
        let status_list = []

        $("input:checkbox").each(function () {
            if ($(this).is(":checked")) {
                if ($(this).attr('data-type') === "pole")
                    pole_list.push(parseInt($(this).attr('data-pk')))
                else
                    status_list.push(parseInt($(this).attr('data-pk')))
            }
        });

        $.ajax({
            type: "POST",
            url: '/filter_lead/',
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            data: {
                poles: JSON.stringify(pole_list),
                status: JSON.stringify(status_list),
            },
            success: function (response) {
                for (const responseElement of response) {
                    add_if_no_1(responseElement)
                }
                update_labels()
            },
        });

    }

    function search_leads() {
        let text = $searchbar.val()

        $.ajax({
            type: "GET",
            url: '/search_lead/?text=' + text,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            success: function (response) {
                searched_leads = response
                display_table2()
            }
        });
    }

    $('#save').on('click', function () {
        save_template()
    })

    function save_template() {
        let name = $("#smsname").val().toString().trim()
        let sms_type = $("#smstype").val()
        let smstext = $("#smstext").val()
        let smsdate = $("#smsdate").val()

        if (name === "" || smstext === "") {
            if (name === "") {
                toast_error("Shablon nomini kiriting")
            } else {
                toast_error("SMS xabarni kiriting")
            }
        }

        if (sms_type !== bayramVaBoshqalar) {
            $.ajax({
                type: "POST",
                url: '/save_sms_template/',
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                data: {
                    name: name,
                    smstext: smstext,
                    sms_type: sms_type,
                    date: ``,
                    leads: "[]",
                },
                success: function (response) {
                    location.href = '/sms/'
                },
            });
        } else {
            let date = new Date(smsdate);
            let day = date.getDate();
            let month = date.getMonth() + 1;
            let year = date.getFullYear();

            if (isNaN(day) || isNaN(month) || isNaN(year)) {
                toast_error("Jo'natish vaqti xato")
            } else {
                if (selected_leads.length === 0) {
                    toast_error("Birorta ham lead tanlanmadi. Lead tanlang")
                } else {
                    let lead_ids = []
                    for (const item of selected_leads) {
                        lead_ids.push(parseInt(item.id))
                    }

                    $.ajax({
                        type: "POST",
                        url: '/save_sms_template/',
                        headers: {
                            "X-CSRFToken": getCookie("csrftoken")
                        },
                        data: {
                            name: name,
                            smstext: smstext,
                            sms_type: sms_type,
                            date: `${year}-${month}-${day}`,
                            leads: JSON.stringify(lead_ids),
                        },
                        success: function (response) {
                            location.href = '/sms/'
                        },
                    });

                }
            }

        }
    }

    function toast_error(message) {
        $.toast({
            heading: 'Qiymatlarda xaolik',
            text: message,
            position: 'top-right',
            loaderBg: '#ff6849',
            icon: 'error',
            hideAfter: 3500
        });
    }

})
