function send_message(bot_token, text, chat_id) {
    var url = "https://api.telegram.org/bot" + bot_token + "/sendMessage?chat_id="+String(chat_id)+"&text="+text;
    fetch(url)
        .then(
            function (response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                        response.status);
                    return;
                }

                // Examine the text in the response
                response.json().then(function (data) {
                });
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}


function get_message() {
    var url = "https://api.telegram.org/bot" + bot_token + "/getUpdates?offset="+String(last_update);
    fetch(url)
        .then(
            function (response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                        response.status);
                    return;
                }

                // Examine the text in the response
                response.json().then(function (data) {
                    console.log(data)
                    if (last_update < data.result[data.result.length - 1].update_id) {
                        for(var dt of data.result ) {
                            if (dt.update_id > last_update) {
                                var first_name = dt.message.from.first_name
                                var username = dt.message.from.username
                                var chat_id = dt.message.from.id
                                var message = dt.message.text
                                var text
                                if (dt.message.text === "/start") {
                                    send_message(bot_token, 'salom', dt.message.chat.id)
                                }
                            }
                        }
                        last_update = data.result[data.result.length - 1].update_id
                    }
                });
            }
        )
        .catch(function (err) {
            console.log('Fetch Error :-S', err);
        });
}