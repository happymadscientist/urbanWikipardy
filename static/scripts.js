function $(el) {return document.getElementById(el.replace(/#/,''));};

function sanitizeString(str){
    str = str.replace(/[^a-z0-9áéíóúñü \.,_-]/gim,"");
    return str.trim();
}

function appendChildren(parent,childrenArray){
	for (i=0;i<childrenArray.length;i++){
		parent.appendChild(childrenArray[i]);
	}
}

function ensureOneCheckboxChecked(parentId){
	checkboxChildren = $("#"+parentId).getElementsByTagName("input");
	for  (var i = 0; i < checkboxChildren.length; i++) {
		if (checkboxChildren[i].checked == true) {return;}
	}
	// if you made it through and none were checked,set the last one to be checked
	checkboxChildren[checkboxChildren.length-1].checked = true;
}

function ensureOneCriteriaChecked(){
	ensureOneCheckboxChecked("searchCriteria");
}

function createRadioButtons(optionName,options,checkboxFlag,ensureOneChecked,widthMultiplier){
	if (checkboxFlag == 1){buttonType = "checkbox";}
	else {buttonType = "radio";}

	// document.getElementById("checkDefinition").addEventListener("click", ensureOneCheckboxChecked);
	// document.getElementById("checkExample").addEventListener("click", ensureOneCheckboxChecked);

	var radioElement = createDiv("radio",optionName);

	totalOptionsLength = options.join('').length
	if (!widthMultiplier) {widthMultiplier = 75;}

	for (i = 0; i < options.length ;i++) {
		thisOption = options[i];

		var optionElement = document.createElement("input");
		optionElement.type = buttonType;
		optionElement.id = thisOption;
		optionElement.name = optionName;
		optionElement.value = thisOption;

		var optionLabel = document.createElement("label");
		optionLabel.innerHTML = thisOption;
		labelWidth = widthMultiplier *(thisOption.length/totalOptionsLength);
		optionLabel.style.width = labelWidth + "%";
		optionLabel.setAttribute("for", thisOption);

		if (ensureOneChecked){
			optionElement.addEventListener("click", ensureOneCriteriaChecked);
			// ensureOneCheckboxChecked(optionName);
		}

		radioElement.appendChild(optionElement);
		radioElement.appendChild(optionLabel);
	}

	optionElement.checked = true;

	return radioElement;
}

function getChosenRadioValue(radioButtonId){
	radioInputs = $("#" + radioButtonId).getElementsByTagName('input');

	for (i = 0; i < radioInputs.length; i++) {
		inputDom = radioInputs[i];
		if (inputDom.checked){ return inputDom.id;}
	}
}

function getChosenCheckboxValues(checkboxButtonId){
	checkboxInputs = $("#" + checkboxButtonId).getElementsByTagName('input');

	checkedValues = [];
	for (i = 0; i < checkboxInputs.length; i++) {
		inputDom = checkboxInputs[i];
		if (inputDom.checked){ checkedValues.push(inputDom.id);}
	}
	return checkedValues;
}

function createP(className,innerText){
	var pElement = document.createElement("div");
	pElement.innerHTML = innerText;
	pElement.className = className;
	return pElement;
}

function createDiv(className,id){
	var divElement = document.createElement("div");
	divElement.className = className;
	divElement.id = id;
	return divElement;
}

function createSlider(sliderId,sliderMin,sliderMax){
	var sliderContainer = document.createElement("div");
	// sliderContainer.className = "slider";

	var sliderElement = document.createElement("input");
	sliderElement.className = "slider";
	sliderElement.type = "range";
	sliderElement.min = sliderMin;
	sliderElement.max = sliderMax;
	sliderElement.id = sliderId;

	var oldSliderVal = -1;
    // sliderInput.addEventListener('mousedown', show);
    // sliderInput.addEventListener('mouseup', hide);

    var bubble = document.createElement('div');
    bubble.className = "slider bubble";
    bubble.style.left = sliderElement.clientX-(bubble.offsetWidth/2)+'px';  

	// var sliderValuePrintout = document.createElement("p");
	// sliderValuePrintout.innerHTML =  sliderElement.value; // Display the default slider value
	// sliderValuePrintout.className = "slider";

	sliderWidth = 470;
	valueMultiplier = sliderWidth/sliderMax;
	// Update the current slider value (each time you drag the slider handle)
	sliderElement.oninput = function() {
    	var sliderVal = this.value;
		if(oldSliderVal !== '0' && oldSliderVal !== '100') { 
        	bubble.style.left = (valueMultiplier*(sliderVal-1))+(bubble.offsetWidth/2)+'px';        
    	}
    	bubble.innerHTML = sliderVal;
    	oldSliderVal = sliderVal;

		// sliderValuePrintout.innerHTML = this.value;
	}
	sliderContainer.appendChild(bubble);
	sliderContainer.appendChild(sliderElement);
	return sliderContainer;
}

function createButton(className,innerText,callbackFunction){
	var button = document.createElement("button");
	button.className = className;
	button.innerHTML = innerText;
	button.onclick = callbackFunction;
	return button;
}

function createInput(className,id){
	var inputDom = document.createElement("input");
	inputDom.className = className;
	inputDom.id = id;
	return inputDom;
}

function createDropdown(dropdownName,elements){
	dropdownSelect = document.createElement("select")
	dropdownSelect.className = "select";
	for (i = 0; i < elements.length ;i++) {
			newOption = document.createElement("option");
			newOption.className = "select-items";
			newOption.value = elements[i];
			newOption.innerText = elements[i];
			dropdownSelect.appendChild(newOption);
	  }
	return dropdownSelect;
}

function playBuzzerSound(buzzerFilename){
	console.log(buzzerFilename);
	var audio = new Audio("buzzerSounds\\" + buzzerFilename);
	audio.play();
}


// jquery get/post
function get(url,callbackFunction){
	jQuery.get("../" +url,callbackFunction);
	// jQuery.get(url, 
	// 	function(data, status){
	// 	alert("Data: " + data + "\nStatus: " + status);
	// 	}
	// );
}

function post(url,postData,successCallback,failureCallback){
	jQuery.ajax({
	  url:"../"+url,
	  type:"POST",
	  data:	JSON.stringify(postData),
	  contentType:"application/json; charset=utf-8",
	  success: successCallback,
	  error: failureCallback,
	  // function(jqXHR, textStatus, errorThrown) {
	  	// failureCallback();
        // alert("Error, status = " + textStatus + ", " +
        //    "error thrown: " + errorThrown);
		// }
	});
}

function periodicGet(url,successCallback,periodicCallback) {
	jQuery.ajax({
	url: "../"+url, 
	type:"GET",
	success: successCallback,
	complete: function() {
		// schedule the next request only when the current one is complete
		setTimeout(periodicCallback, refreshInterval);
		}
	});
}