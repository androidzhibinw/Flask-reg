var totalSeconds = 60;
var seconds = totalSeconds;

var loginBtn;
var sendBtn;
var phoneInput;
var codeInput;
window.onload = function() {
    loginBtn = document.getElementById("btn-login")
    sendBtn = document.getElementById("btn-send")
    phoneInput = document.getElementById("phone")
    codeInput = document.getElementById("code")
    loginBtn.disabled = true;
    sendBtn.disabled = true;
}
window.addEventListener('input', function (e) {
     console.log("keyup event detected! coming from this element:", e.target);
     checkLoginBtn();
}, false);

function checkPhone(phone) {
    var reg = /^1[34578]\d{9}$/;
    if(!reg.test(phone)){
        return false;
    }

    return true;
}

function checkCode(code) {
    return code.length == 6;
}

function checkLoginBtn() {
    var isPhoneValid = checkPhone(phoneInput.value);
    var isCodeValid = checkCode(codeInput.value);
    sendBtn.disabled = !isPhoneValid;
    loginBtn.disabled = !(isPhoneValid && isCodeValid);
}

function countdown() {
    if (seconds == 1) {
      sendBtn.innerHTML = "重新发送";
	  sendBtn.disabled = false
      seconds = totalSeconds;
      return;
    }
    seconds--;
    // TO BE FIXED:
    // test data start
    /*
    if (seconds == 8) {
        generateTestCode()
        return;
    }*/
    // test data end
    sendBtn = document.getElementById('btn-send');
    sendBtn.innerHTML = "重新发送("+seconds+")";
    sendBtn.disabled=true
    timeoutMyOswego = setTimeout(countdown, 1000);
 }

function generateTestCode() {
    seconds = totalSeconds;
    codeInput.value = "123456";
    sendBtn.disabled = false;
    sendBtn.innerHTML = "重新发送";

    checkLoginBtn();
}
