window.onload = function()
{
	var width = document.getElementById('width');
	var height = document.getElementById('height');
	var widthLeaf1 = document.getElementById('widthLeaf1');
	var widthLeaf2 = document.getElementById('widthLeaf2');
	var widthLeaf3 = document.getElementById('widthLeaf3');
	var typeWindow = document.getElementById('WindowType');
	defaultData();

	width.oninput = function() {
		updateLeafData()
	};

	height.oninput = function() {
		updateLeafData()
	};

	widthLeaf1.oninput = function() {
		//typeWindow = document.getElementById('WindowType').value;
		switch(typeWindow.value)
		{
			case '2':
				widthLeaf2.value = width.value - widthLeaf1.value
				break;
			case '3':
				widthLeaf2.value = (width.value - widthLeaf1.value) / 2
				widthLeaf3.value = (width.value - widthLeaf1.value) / 2
				break;
			case '4':
				widthLeaf2.value = height.value - widthLeaf1.value
				break;
		}
	};

	widthLeaf2.oninput = function() {
		//typeWindow = document.getElementById('WindowType').value;
		switch(typeWindow.value)
		{
			case '2':
				widthLeaf1.value = width.value - widthLeaf2.value
				break;
			case '3':
				widthLeaf1.value = (width.value - widthLeaf2.value) / 2
				widthLeaf3.value = (width.value - widthLeaf2.value) / 2
				break;
			case '4':
				widthLeaf1.value = height.value - widthLeaf2.value
				break;
		}
		console.log(widthLeaf2.value);
	};

	widthLeaf3.oninput = function() {
		//typeWindow = document.getElementById('WindowType').value;
		if (typeWindow.value == '3')
		{
				widthLeaf1.value = (width.value - widthLeaf3.value) / 2
				widthLeaf2.value = (width.value - widthLeaf3.value) / 2
				break;
		}
		console.log(widthLeaf3.value);
	};

	function defaultData()
	{
		width.value = 600;
		height.value = 1000;
		widthLeaf1.value = width.value;
		widthLeaf2.value = 0;
		widthLeaf3.value = 0;
		typeWindow.value = 1;
	}

	function updateLeafData()
	{
		switch(typeWindow.value)
		{
			case '1':
				document.getElementById('fold_1').setAttribute('style', 'display: block;');
				document.getElementById('fold_2').setAttribute('style', 'display: none;');
				document.getElementById('fold_3').setAttribute('style', 'display: none;');
				widthLeaf1.value = width.value;
				widthLeaf2.value = 0;
				widthLeaf3.value = 0;
				break;
			case '2':
				document.getElementById('fold_1').setAttribute('style', 'display: block;');
				document.getElementById('fold_2').setAttribute('style', 'display: block;');
				document.getElementById('fold_3').setAttribute('style', 'display: none;');
				widthLeaf1.value = width.value / 2;
				widthLeaf2.value = width.value / 2;
				widthLeaf3.value = 0;
				break;
			case '3':
				document.getElementById('fold_1').setAttribute('style', 'display: block;');
				document.getElementById('fold_2').setAttribute('style', 'display: block;');
				document.getElementById('fold_3').setAttribute('style', 'display: block;');
				widthLeaf1.value = width.value / 3;
				widthLeaf2.value = width.value / 3;
				widthLeaf3.value = width.value / 3;
				break;
			case '4':
				document.getElementById('fold_1').setAttribute('style', 'display: block;');
				document.getElementById('fold_2').setAttribute('style', 'display: block;');
				document.getElementById('fold_3').setAttribute('style', 'display: none;');
				widthLeaf1.value = height.value / 2;
				widthLeaf2.value = height.value / 2;
				widthLeaf3.value = 0;
				break;
		}
	}

	typeWindow.onclick = function() {
		//typeWindow = document.getElementById('WindowType');
		updateLeafData();
	}

	/*document.getElementById('WindowType').onclick = function()
	{
		updateLeafData();
	}*/
}