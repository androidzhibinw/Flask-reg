$(document).ready(function (){
var totalSeconds = 60;
var seconds = totalSeconds;
var sendBtn;

    $('#btn-send').click(function countdown(){
        if(seconds == totalSeconds) {
            console.log("btn-send clicked");
            var phoneNumber = $('#phone').val()
            $.ajax({
                  method: "POST",
                  url: "/getcode",
                  data: JSON.stringify({"number":phoneNumber},null,4),
                  contentType:'application/json;charset=UTF-8'
            })
              .done(function( msg ) {
                      console.log( "Data Saved: " + msg );
                        });
        }
        if (seconds == 1) {
          sendBtn.innerHTML = "重新发送";
          sendBtn.disabled = false
          seconds = totalSeconds;
          return;
        }
        seconds--;
        sendBtn = document.getElementById('btn-send');
        sendBtn.innerHTML = "重新发送("+seconds+")";
        sendBtn.disabled=true
        timeoutMyOswego = setTimeout(countdown, 1000);
    });
});
