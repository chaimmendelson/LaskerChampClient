async function validate_login(){
    cookie = localStorage.getItem('chess-cookie')
    if (cookie) {
        const response  = await fetch('/validate', {
            method: 'POST',
            headers: {
                'chess-cookie': cookie
            }
        });
        console.log(response);
        const data = await response.json();
        if (data.status === 'ok') {
            window.location.href = 'client';
            return;
        };
    }
    window.location.href = 'login';
}
window.onload = validate_login;