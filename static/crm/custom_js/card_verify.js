let url = "https://checkout.test.paycom.uz/api";
let token = ""
let sms_expire_time = 60;
let sms_time_is_active = false;
let sms_code = ""

let card_create_errors = [
    {
        code: -31301,
        header: "SMS-xabar ulanmagan"
    }, {
        code: -31302,
        header: "Karta qoldig'ini olish imkonsiz. Keyinroq urinib ko'ring"
    }, {
        code: -31303,
        header: "Kartadagi mablag 'yetarli emas"
    }, {
        code: -31002,
        header: "Jarayon markazi serveri mavjud emas"
    }, {
        code: -31300,
        header: "Karta raqami yaroqsiz"
    }, {
        code: -31001,
        header: "SMS-xabar ulanmagan"
    }
]

let card_get_verify_errors = [
    {
        code: -31400,
        header: "Karta topilmadi"
    }, {
        code: -31301,
        header: "SMS-xabar ulanmagan"
    }
]

let card_verify_errors = [
    {
        code: -31400,
        header: "Karta topilmadi"
    }, {
        code: 31301,
        header: "SMS-xabar ulanmagan"
    }, {
        code: 31101,
        header: "Kod muddati tugagan. Yangi kodni talab qiling"
    }, {
        code: 31102,
        header: "Kodni kiritishga urinishlar soni oshib ketdi. Yangi kodni talab qiling"
    }, {
        code: 31103,
        header: "Noto'g'ri kod kiritildi"
    }
]

$(document).ready(function () {
    let header = {
        'X-Auth': mer_id
        // 'X-Auth': "60ae15c4a44459bf07890f7f"
    }
    if (paycom_is_test) {
        url = "https://checkout.test.paycom.uz/api";
    } else {
        url = "https://checkout.paycom.uz/api";
    }
    $('#card_step_2').hide();
    $('#sms_refresh').hide();
    $('#card_number').mask('0000 0000 0000 0000');
    $('#card_expire').mask('00/00');

    $('#btn_next').on('click', function (e) {
        if (check_card_number() && check_card_expire()) {
            card_create()
        } else {
            let animation = "tada";
            $(this).parents('.box').addClass('animated ' + animation).one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function () {
                $(this).removeClass('animated ' + animation);
            });
            e.preventDefault();
        }
    })

    $('#btn_tasdiqlash').on('click', function (e) {
        if (sms_time_is_active) {
            sms_code = $('#sms_code').val()
            card_verify()
        }
    })

    function get_card_number() {
        let number = $('#card_number').val();
        return number.replaceAll(" ", "");
    }

    function get_card_expire() {
        let expire = $('#card_expire').val();
        return expire.replaceAll("/", "");
    }

    function check_card_number() {
        let number = get_card_number();
        return number.length === 16;
    }

    function check_card_expire() {
        let expire = get_card_expire();
        return expire.length === 4;
    }

    function card_create() {
        $.ajax({
            method: "POST",
            url: url,
            dataType: "json",
            crossDomain: true,
            format: "json",
            headers: header,
            data: JSON.stringify({
                "method": "cards.create",
                "params": {
                    "card": {"number": get_card_number(), "expire": get_card_expire()},
                    "save": true
                }
            }),
            success: function (response) {
                if ("result" in response) {
                    $('#card_step_2').show();
                    $('#card_step_1').hide();
                    token = response['result']['card']['token'];
                    card_get_verify_code();
                } else {
                    define_error(response, card_create_errors)
                }
            },
        });
    }

    function card_get_verify_code() {
        $.ajax({
            method: "POST",
            url: url,
            dataType: "json",
            crossDomain: true,
            format: "json",
            headers: header,
            data: JSON.stringify({
                "method": "cards.get_verify_code",
                "params": {
                    "token": token,
                }
            }),
            success: function (response) {
                if ("result" in response) {
                    $('#phone_number').html(response['result']['phone'])
                    sms_time_is_active = true
                    timestart()
                } else {
                    define_error(response, card_get_verify_errors)
                }
            },
        });
    }

    function card_verify() {
        $.ajax({
            method: "POST",
            url: url,
            dataType: "json",
            crossDomain: true,
            format: "json",
            headers: header,
            data: JSON.stringify({
                "method": "cards.verify",
                "params": {
                    "token": token,
                    "code": sms_code
                }
            }),
            success: function (response) {
                if ("result" in response) {
                    token = response['result']['card']['token'];
                    $.ajax({
                        method: "POST",
                        url: url_f,
                        data: {
                            name: $('#card_name').val(),
                            number: get_card_number(),
                            expire: get_card_expire(),
                            token: token,
                            verify: response['result']['card']['verify'],
                            csrfmiddlewaretoken: getCookie('csrftoken')
                        },
                        success: function (response) {
                            if (response.message === "Success") {
                                window.location.href = url_ff;
                            }
                        }
                    });
                } else {
                    define_error(response, card_verify_errors)
                }
            }
        });
    }

    function startTimer(duration, display) {
        let timer = duration, minutes, seconds;
        let counter_timer = setInterval(function () {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;
            display.textContent = minutes + ":" + seconds;

            if (--timer < 0) {
                clearInterval(counter_timer)
                sms_time_is_active = false
                $('#sms_refresh').show();
            }
        }, 1000);
    }

    let timestart = function () {
        $('#sms_refresh').hide();
        let display = document.querySelector('#sms_time');
        startTimer(sms_expire_time, display);
    };

    $('#sms_refresh').on('click', function (e) {
        card_get_verify_code()
    })

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function define_error(response, array) {
        let code = response['error']['code'];
        let bor = false;
        for (let item of array) {
            if (code === item['code']) {
                toast(item['header'], '')
                bor = true;
                break;
            }
        }
        if (!bor) {
            toast("Qandaydir xatolik", '')
        }
    }

    function toast(header, text) {
        $.toast({
            heading: '<h4 style="color:#fff;">' + header + '</h4>',
            text: text,
            position: 'top-right',
            loaderBg: '#ffbb00',
            icon: 'error',
            hideAfter: 3500

        });
    }

});

