$(document).ready(function (){
var totalSeconds = 60;
var seconds = totalSeconds;
var sendBtn = $('#btn-send');
var inputPhone = $('#input_phone')
var inputCode = $('#input_code')
var loginBtn = $('#btn-login')
sendBtn.prop('disabled',true)

$('#btn-login').prop('disabled',true)
    $('#btn-send').click(function countdown(){
        if(seconds == totalSeconds) {
            console.log("btn-send clicked");
            var phoneNumber = inputPhone.val()
            $.ajax({
                  method: "POST",
                  url: "/getcode",
                  data: JSON.stringify({"number":phoneNumber}),
                  contentType:'application/json;charset=UTF-8'
            }).done(function( msg ) {
                 console.log( "getcode response " + msg );
            });
        }
        if (seconds == 1) {
          sendBtn.html( "重新发送");
          sendBtn.prop('disabled',false)
          seconds = totalSeconds;
          return;
        }
        seconds--;
        sendBtn.html("重新发送("+seconds+")");
        sendBtn.prop('disabled',true)
        timeoutMyOswego = setTimeout(countdown, 1000);
    });
    function checkPhone(phone) {
        var reg = /^1[34578]\d{9}$/;
        return reg.test(phone);
    }

    function checkCode(code) {
        var reg=/^[0-9]{6}$/;
        return reg.test(code);
    }
    $('input[id^="input"]').on("change keyup paste",function inputListener(){
        console.log("input changed." + inputPhone.val());
        console.log("input changed." + inputCode.val());
        var disableBtnSend = !(checkPhone(inputPhone.val()) && (seconds == totalSeconds));
        sendBtn.prop('disabled',disableBtnSend)
        var disableBtnLogin = !(checkPhone(inputPhone.val())) || !(checkCode(inputCode.val()));
        loginBtn.prop('disabled',disableBtnLogin)
    });
});
