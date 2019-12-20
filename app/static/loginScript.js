window.onload = function()
{
	console.log('Готов!');
	document.getElementById("submit").onclick = function()
	{
		password = document.getElementById('password').value;
		//document.cookie = "user="
		//alert('КУКИ:' + document.cookie);
		//alert(password);
	}
}