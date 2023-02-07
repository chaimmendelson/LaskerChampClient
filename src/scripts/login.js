//submit function
// get the data from the form when the user clicks the submit button
document.querySelector('.form').addEventListener('submit', async (e) => {
    e.preventDefault();
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
    const json = await response.json();
    const status = json.status;
    console.log(status);
    if (status === 'ok') {
        window.location.href = '/';
        return;
    }
});

//show/hide password if the user checks/unchecks the checkbox
function showPassword() {
    let password = document.getElementById("password");
    password.type = password.type === "password" ? "text" : "password";
}
document.getElementById("show_password").addEventListener("click", showPassword);