function showPassword(){
    if (document.getElementById('password').type == 'text'){
        document.getElementById('password').type = 'password';
    }
    else{
        document.getElementById('password').type = 'text';
    }
    
}
document.getElementById('showPassword').addEventListener("click",function(){showPassword()})

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