// show password button
function showPassword(){
    if (document.getElementById('password').type == 'text'){
        document.getElementById('password').type = 'password';
    }
    else{
        document.getElementById('password').type = 'text';
    }
    
}
document.getElementById('showPassword').addEventListener("click",function(){showPassword()}) // show password calling

// allows me to press enter when needed instead of hitting the actual button
function EnterSubmit(locStart, clicked){
    let placement = document.getElementById(locStart)
    if (locStart == 0) placement = document
    placement.addEventListener("keypress", function(event) {
        if (event.key == "Enter") {
            event.preventDefault();
            document.getElementById(clicked).click();
        }
    })
} 
EnterSubmit('password', 'submit')
EnterSubmit('username', 'submit')

// check username and password inputs
function checkChar(char){
    let charList = ['q', 'r', 'b', 'n']
    for (let i = 0; i < charList.length; i++){
        if (char == charList[i]) return true;
    }
    return false;
}
function checkUsername(char){
    let regex = /^\w{3,32}$/;
    return regex.test(char);
}
function checkPassword(char){
    let regex = /^\w{3,32}$/;
    return regex.test(char);
}

// information to use for initial testing, temporary (but should in theory work with simple switching of the stuff)
let log_in_info = {'test': 'test'}
let rating = 1200

//submit function
document.getElementById('submit').addEventListener("click", function() {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    document.getElementById('username').style.border = '1px solid black';
    document.getElementById('password').style.border = '1px solid black';
    if (!checkUsername(username)){
        document.getElementById('username').style.border = '2px solid red';
        return;
    }
    if (!checkPassword(password)){
        document.getElementById('password').style.border = '2px solid red';
        return;
    }
    if (username in log_in_info){
        if (log_in_info[username] == password){
            console.log('success')
            // window.location.replace('http://192.168.43.133:8000/') // doesn't successfully redirect, it takes far to long
        }
        else {
            console.log('incorrect password');
            document.getElementById('password').style.border = '2px solid red';
        }
    }
    else {
        console.log('incorrect username');
        document.getElementById('username').style.border = '2px solid red';
    }
});