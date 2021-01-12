
function allowDecimal(evt, el){ 
    var charCode = evt.which;
        if ((charCode != 46 || $(el).text().indexOf('.') != -1) &&  (charCode < 48 || charCode > 57))
            evt.preventDefault();
};

function allowNumeric(evt){ 
    if (isNaN(String.fromCharCode(evt.which))) evt.preventDefault();
};


function validInput(el){ 
    var value=$(el).text();
    if( value < 1)
      alert('Resource capacity should be greater than 0');
};