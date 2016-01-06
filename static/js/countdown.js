    var seconds=10;
    var temp;
 function countdown() {
    if (seconds == 1) {
      temp = document.getElementById('btn-send');
      temp.innerHTML = "重新发送";
	  temp.disabled=false
      seconds=10;
      return;
    }
    seconds--;
    temp = document.getElementById('btn-send');
    temp.innerHTML = "重新发送("+seconds+")";
    temp.disabled=true
    timeoutMyOswego = setTimeout(countdown, 1000);
  }
