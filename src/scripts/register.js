document.querySelector('.form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.querySelector('#username').value;
    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;
    if (!(checkUsername() && checkPassword())) return;
    document.body.style.pointerEvents = 'none';
    document.getElementById('loader').style.display = 'block';
    const response = await fetch('/sign_up', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(
            {username: username, password: password, email: email}
        ),
    });
    await handleResponse(response);
    
});

async function handleResponse(response) {
    let status = response.status;
    if (status === 200) {
        window.location.href = '/';
        return;
    }
    slotL = ['username', 'email', 'password']
    let errorSlot = status%10;
    displayError(slotL[errorSlot-1]);
    let errorType = Math.floor((status%100)/10);
    if (errorType === 8)
        alert(slotL[errorSlot-1] + ' already exists');
    document.getElementById('loader').style.display = 'none';
    document.body.style.pointerEvents = 'auto';
}



function displayError(box) {
    document.getElementById(box).style.border = '3px solid red';
}

function removeError(box) {
    document.getElementById(box).style.border = '3px solid black';
}

function checkUsername() {
    let username = document.getElementById("username").value;
    let usernameRegex = /^[a-zA-Z]\w{2,31}$/;
    let is_valid = usernameRegex.test(username);
    is_valid ? removeError("username") : displayError("username");
    return is_valid ? true : false;
}

function checkPassword(){
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

document.getElementById("email").addEventListener("input", removeError("email"));
