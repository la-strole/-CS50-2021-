function ajax_request(){
  let symbol = document.getElementById("symbol-input").value;
  //console.log("run ajax function");

  /* delete all options */
  if (document.getElementById("symbols")){
    document.getElementById("symbols").remove();
  }
    
  if (symbol){
    var aj = new XMLHttpRequest();
    
    /* callback function */
    aj.onreadystatechange = function(){

      if (aj.readyState == 4 && aj.status == 200){
        /* create datalist node */
        let parent = document.createElement("datalist");
        parent.id = "symbols";
        document.getElementById("symbol-input").appendChild(parent);
        /* get json as list of 10 symbols from server */
        let possible_symbols = JSON.parse(aj.responseText);
        /* add options tags to input */
        for (let s of possible_symbols){
          /* create new node */
          let node = document.createElement("option");
          /* set node value to value from json response */
          node.value = s;
          /* put element to document */
          document.getElementById("symbols").appendChild(node);
        }

      };
    
    };
    aj.open("GET", `/quote?symbol=${symbol}`, true);
    aj.send();
  }
}


/* Check if DOM is full loaded - else - can not find elemnt id = symbols */
/* Check if DOM full loaded */


if (document.readyState === 'loading') {  // document still loaded

  console.log("DOM still loading - waiting...");

  document.addEventListener('DOMContentLoaded', function(){
    document.getElementById("symbol-input").addEventListener('input', ajax_request);});  
}
else {  // `DOMContentLoaded` is full loaded
  console.log("Try to add event listener to options block");
  document.getElementById("symbol-input").addEventListener('input',ajax_request);
}
