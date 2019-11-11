function valid(form){
	var message = "Вход произведен";
	if(form.name.value == "" || form.password.value == ""){
		message = "Некоторые поля не заполнены";
	}
	else if(form.password.value != "admin" && form.name.value != "admin"){
		message = "Неверный логин или пароль";
	}
		document.getElementById("message").innerHTML = message;
}