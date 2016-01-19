$(document).ready(function (){
var totalSeconds = 60;
var seconds = totalSeconds;
var sendBtn;

    $('#btn-send').click(function countdown(){
        console.log("btn-send clicked");
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
