// https://www.w3schools.com/howto/howto_js_autocomplete.asp

function makeAutoCompleteTextBox(textBox, stockSymbols) {
    var currentFocus;

    textBox.addEventListener("input", function(e) {
        var divContainer, divItem, i, val = this.value;

        closePopupLists();
        if (!val) {
            return false;
        }

        currentFocus = -1;

        // create a DIV element that will contain the items
        divContainer = document.createElement("DIV");
        divContainer.setAttribute("id", this.id + "autocomplete-list");
        divContainer.setAttribute("class", "autocomplete-items");
        
        // append the DIV element as a child of the autocomplete container
        this.parentNode.appendChild(divContainer);
        
        for (i = 0; i < stockSymbols.length; i++) {
            if (stockSymbols[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                // create a DIV element for each matching element
                divItem = document.createElement("DIV");
                
                // make the matching letters bold 
                divItem.innerHTML = "<strong>" + stockSymbols[i].substr(0, val.length) + "</strong>";
                divItem.innerHTML += stockSymbols[i].substr(val.length);
                
                // insert an input field that will hold the current array item's value 
                divItem.innerHTML += "<input type='hidden' value='" + stockSymbols[i] + "'>";
                
                // execute a function when the user clicks on the item value (DIV element)
                divItem.addEventListener("click", function(e) {
                        textBox.value = this.getElementsByTagName("input")[0].value;
                        closePopupLists();
                    });
                divContainer.appendChild(divItem);
            }
        }
    });

    textBox.addEventListener("keydown", function(e) {
        var divs = document.getElementById(this.id + "autocomplete-list");
        if (divs) {
            divs = divs.getElementsByTagName("div");
        }
        
        if (e.keyCode == 40) { // down arrow key
            currentFocus++;
            setSelected(divs);
        }
        else if (e.keyCode == 38) { // up arrow key
            currentFocus--;
            setSelected(divs);
        }
        else if (e.keyCode == 13) { // enter key
            e.preventDefault();
            if (currentFocus > -1) {
                if (divs) {
                    divs[currentFocus].click();
                }
            }
        }
    });

    function setSelected(divs) {
        if (!divs) {
            return false;
        }
        clearSelected(divs);
        if (currentFocus >= divs.length) { // wrap to the start of the list
            currentFocus = 0;
        }
        if (currentFocus < 0) { // wrap to the end of the list
            currentFocus = (divs.length - 1);
        }
        divs[currentFocus].classList.add("autocomplete-active");
    }

    function clearSelected(divs) {
        for (var i = 0; i < divs.length; i++) {
          divs[i].classList.remove("autocomplete-active");
        }
    }

    function closePopupLists(element) {
        var divContainers = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < divContainers.length; i++) {
            if (element != divContainers[i] && element != textBox) {
                divContainers[i].parentNode.removeChild(divContainers[i]);
            }
        }
    }

    document.addEventListener("click", function (e) {
        closePopupLists(e.target);
    });
}

function onClickReset() {
    document.getElementById('symbol').value = '';
    document.getElementById('quantity').value = '';
    document.getElementById('price').value = '';
}
