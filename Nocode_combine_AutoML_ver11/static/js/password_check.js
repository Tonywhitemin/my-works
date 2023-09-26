/*230626新增密碼讓使用者檢視的功能*/
function togglePasswordVisibility() {
    var passwordInput = document.getElementById("password");
    var button = document.getElementById("toggleBtn");

    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      button.textContent = "隱藏密碼";
    } else {
      passwordInput.type = "password";
      button.textContent = "顯示密碼";
    }
  }

function togglePasswordVisibility2() {
var passwordInput = document.getElementById("password2");
var button = document.getElementById("toggleBtn2");

if (passwordInput.type === "password") {
    passwordInput.type = "text";
    button.textContent = "隱藏密碼";
} else {
    passwordInput.type = "password";
    button.textContent = "顯示密碼";
}
}