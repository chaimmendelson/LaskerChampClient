//submit function
// get the data from the form when the user clicks the submit button
document.querySelector('.form').addEventListener('submit', async (e) => {
    e.preventDefault();
    document.body.style.pointerEvents = 'none';
    document.getElementById('loader').style.display = 'block';
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;
    let user = {username: username, password: password};
    const response  = await fetch('/validate', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
    });
    await handleResponse(response);
});

async function handleResponse(response) {
    const json = await response.json()
    let status = json.status;
    switch (status) {
        case 200:
            window.location.href = '/';
            break;
        case 490:
            alert('Username already logged in');
            break;
        case 491:
            displayError('password');
            break;
        case 492:
            displayError('username');
            displayError('password');
            break;
        default:
            alert('Unknown error');
    }
    document.getElementById('loader').style.display = 'none';
    document.body.style.pointerEvents = 'auto';
}

function displayError(box) {
    document.getElementById(box).style.border = '3px solid red';
}

function removeError(box) {
    document.getElementById(box).style.border = '3px solid black';
}

//show/hide password if the user checks/unchecks the checkbox
function showPassword() {
    let password = document.getElementById("password");
    password.type = password.type === "password" ? "text" : "password";
}

document.getElementById("show_password").addEventListener("click", showPassword);

document.getElementById("password").addEventListener("input", removeError("password"));

document.getElementById("username").addEventListener("input", removeError("username"));
