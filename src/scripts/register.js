// get the data from the form when the user clicks the submit button
document.querySelector('.form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.querySelector('#username').value;
    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;
    console.log(checkUsername())
    if (!(checkUsername() && checkPassword())) {
        return;
    }
    let user = {username: username, password: password, email: email};
    const response  = await fetch('/sign_up', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
    });
    //extract the json from the response
    const json = await response.json();
    const status = json.status;
    if (status === 200) {
        window.location.href = '/';
        return;
    }
    let type = status % 10;
    switch (type) {
        case 1:
            displayError("username");
            alert("Username already exists");
            break;
        case 2:
            displayError("email");
            alert("Email already exists");
            break;
        case 3:
            displayError("password")
            break;
        default:
            break;
    }
});



function displayError(box) {
    document.getElementById(box).style.border = '3px solid red';
}

function removeError(box) {
    document.getElementById(box).style.border = '3px solid black';
}

function checkUsername() {
    // check if the username is valid by the rules specified:
    // 1 - username must be at least 3 characters and at most the length specified.
    // 2 - username must contain only letters and numbers.
    // 3 - the first character must be a letter.
    let username = document.getElementById("username").value;
    let usernameRegex = /^[a-zA-Z]\w{2,31}$/;
    let is_valid = usernameRegex.test(username);
    is_valid ? removeError("username") : displayError("username");
    return is_valid ? true : false;
}

function checkPassword(){
    // 1 - password must be at least 8 characters long and at most 32.
    // 2 - password must contain only letters and numbers.
    // 3 - password must containe at least one number and one lower case letter.
    let password = document.getElementById("password").value;
    let passwordRegex = /^(?=.*[a-z])(?=.*[0-9])\w{8,32}$/;
    let is_valid = passwordRegex.test(password);
    is_valid ? removeError("password") : displayError("password");
    return is_valid ? true : false;
}

//show/hide password if the user checks/unchecks the checkbox
function showPassword() {
    let password = document.getElementById("password");
    password.type = password.type === "password" ? "text" : "password";
}
document.getElementById("show_password").addEventListener("click", showPassword);

document.getElementById("password").addEventListener("input", checkPassword);

document.getElementById("username").addEventListener("input", checkUsername);

document.getElementById("email").addEventListener("input", function() {
    removeError("email");
});
