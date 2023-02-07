// get the data from the form when the user clicks the submit button
document.querySelector('.form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.querySelector('#username').value;
    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;
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
            document.getElementById("username_box").style.border = '1px solid red';
            break;
        case 2:
            document.getElementById("email_box").style.border = '1px solid red';
            break;
        case 3:
            document.getElementById("password_box").style.border = '1px solid red';
            break;
        default:
            break;
    }
});

//show/hide password if the user checks/unchecks the checkbox
function showPassword() {
    let password = document.getElementById("password");
    password.type = password.type === "password" ? "text" : "password";
}
document.getElementById("show_password").addEventListener("click", showPassword);