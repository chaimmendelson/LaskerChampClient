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
document.getElementById("submit").addEventListener("click", async function () { // this function will run when the user click on the login button
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let user = {username: username, password: password};
    const response  = await fetch('/login', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user),
    });
    console.log(response);
    if (!response.status === 200) {
        const message = `An error has occured: ${response.status}`;
        throw new Error(message);
    }
    const data = await response.json();
    if (data.status === 'success') {
        localStorage.setItem('chess-cookie', data.cookie);
        let url = data.redirect;
        window.location = url;
    };
    console.log(data.status);
});