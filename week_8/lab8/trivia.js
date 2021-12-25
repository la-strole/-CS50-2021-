function answer_part1(className, id){
    if (className == "incorrect"){
    document.getElementById(id).style.backgroundColor = "red";
    document.getElementById("answer_part1").innerHTML = "Incorrect";
    }
    else{
        document.getElementById(id).style.backgroundColor = "green";
        document.getElementById("answer_part1").innerHTML = "Correct";
    }
}

function answer_part2(id){
    
    if (document.getElementById("input_text_2").value == 'good answer'){
        document.getElementById(id).style.backgroundColor = "green";
        document.getElementById("answer_part2").innerHTML = "Correct";
    }
    else{
        document.getElementById(id).style.backgroundColor = "red";
    document.getElementById("answer_part2").innerHTML = "Incorrect";
    }
}