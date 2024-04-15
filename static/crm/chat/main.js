var url = "http://127.0.0.1:8000/chat/get_bot"
var bot = null;
var bot_token = null;
var last_update = 0;
fetch(url)
    .then(
        function (response) {
            if (response.status !== 200) {
                console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                return;
            }

            response.json().then(function (data) {
                if (data.token === null) {
                    console.log('token nul')
                } else {
                    bot_token = data.token;
                    console.log(bot_token)
                    bot = data.bot;
                    setInterval(get_message,2000);
                }

            });
        }
    )
    .catch(function (err) {
        console.log('Fetch Error :-S', err);
    });


