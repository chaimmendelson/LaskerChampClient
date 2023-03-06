//Game control btns
document.getElementById('startBtn').addEventListener('click', async function() {
    resetClock();
    document.getElementById('startBtn').disabled = true;
    //get the selected game mode from the radio buttons
    let game_mode = document.querySelector('input[name="game_mode"]:checked').value;
    //get the selected level from the slider
    let level = document.getElementById('engine_level').value;
    await socket.emit('start_game', {game_mode: game_mode, level: level});
}); // start

document.getElementById('quitBtn').addEventListener('click', function(){ 
    quit_game()
}); // quit

// variables for the information on the board and of the board

const socket = io({
    auth: {
      token: get_cookie()
    }
});

let start = null;
let delay_time = 0;
socket.on('connect', () => {
   console.log('Connected to server');
   start = Date.now();
   socket.emit('ping')
});

socket.on('pong', () => {
    delay_time = Math.round((Date.now() - start) / 1000);
    console.log('ping: ' + delay_time);
});


socket.on('clock_update', (data) => {
    // the format is {white: seconds, black: seconds}
    // change the clocks to reflect the new time
    if (playerColor === WHITE) {
        player1TimeRemaining = data['white'];
        player2TimeRemaining = data['black'];
    }
    else {
        player1TimeRemaining = data['black'];
        player2TimeRemaining = data['white'];
    }
});

socket.on('connect_error', (error) => {
   console.log('Connection error: ' + error);
});

socket.on('disconnect', () => {
   console.log('Disconnected from server');
});

socket.on('login_error', (data) => {
   console.log('login error: ' + data);
});

socket.on('update_elo', (data) => {
    document.getElementById('elo').innerHTML = data['elo'];
});


socket.on('user_data', (data) => {
   document.getElementById('username').innerHTML = data['username'];
   document.getElementById('elo').innerHTML = data['elo'];
});

socket.on('opponent_move', (data) => {
    let move = {from: data['src'], to: data['dst']};
    moveToHighlight = move;
    if (data['promotion']){
        move['promotion'] = data['promotion']
    }
    game.move(move);
    nextPlayer();
    updateTurn();
    resetPosition();
    if (usePreGame) try_pre_move();
})

socket.on('game_started', (data) => {
    playerNum = data == 'white' ? 0 : 1;
    currentPlayer = 0;
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('quitBtn').style.display = 'block';
    startGame(data);
    if (playerColor === WHITE)
        document.getElementById('player1-clock').style.backgroundColor = 'white';
    else
        document.getElementById('player2-clock').style.backgroundColor = 'white';
    startClock();
})

socket.on('timeout', () => clear_game('you have run out of time'));

socket.on('game_over', (resault) => clear_game({0: 'you have lost', 0.5: 'its a tie', 1: 'you have won'}[resault]));

socket.on('opponent_quit', () => clear_game('your opponent quit the match'));

socket.on('opponent_timeout', () => clear_game('your opponent ran out of time'));


async function quit_game(){
    await socket.emit('quit_game');
    clear_game('you lost');
}

// Initial time for each player (in seconds)
const player1Time = 0;
const player2Time = 0;

// Variables to keep track of the current time remaining for each player
let player1TimeRemaining = player1Time;
let player2TimeRemaining = player2Time;

// Variable to keep track of which player's turn it is
let currentPlayer = 0;
let playerNum = 0;
// Timer interval variable
let interval;

// Function to start the clock
function startClock() {
    interval = setInterval(() => {
        // Check which player's turn it is
        if (currentPlayer === playerNum) {
            player1TimeRemaining--;
            if (player1TimeRemaining < 0) {
                clearInterval(interval);
                player1TimeRemaining = 0;
            }
        } else {
            player2TimeRemaining--;
            if (player2TimeRemaining < 0) {
                clearInterval(interval);
                player2TimeRemaining = 0;
            }
        }
        formatClock();
    }, 1000);
}


// Function to stop the clock
function stopClock() {
    clearInterval(interval);
}

// Function to switch to the next player
function nextPlayer() {
    stopClock();
    currentPlayer = 1 - currentPlayer;
    startClock();
}

// Function to format the clock

function formatTime(time) {
    let minutes = Math.floor(time / 60);
    let seconds = time % 60;
    return (minutes < 10 ? '0': '') + minutes + ' : ' + (seconds < 10 ? '0' : '') + seconds;
}

function formatClock() {
    document.getElementById('player1-time').innerHTML = formatTime(player1TimeRemaining);
    document.getElementById('player2-time').innerHTML = formatTime(player2TimeRemaining);
}

// Function to reset the clock
function resetClock() {
    stopClock();
    player1TimeRemaining = player1Time;
    player2TimeRemaining = player2Time;
    currentPlayer = 0;
    formatClock();
    document.getElementById('player1-clock').style.backgroundColor = 'grey';
    document.getElementById('player2-clock').style.backgroundColor = 'grey';
}


function get_cookie(){
    cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++){
        cookie = cookies[i].split('=')
        if (cookie[0] === 'chess-cookie'){
            return cookie[1];
        }
    }
    return null;
}

// get the value of the slide bar engine_level upon sliding it and log it
document.getElementById('engine_level').addEventListener('input', function() {
    engine_level = this.value;
    document.getElementById('level_display').innerHTML = 'Level: ' + engine_level;
});


document.getElementById('logoutBtn').addEventListener('click', function() {
    document.cookie = 'chess-cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/';
});

function resizeBoard(){
    if (screen.width < 1000){
        let screen_height = screen.height - 100;
        let screen_width = screen.width;
        let board_size = (Math.min(screen_height, screen_width)) / screen_width * 100 - 5;
        console.log(board_size);
        document.getElementById('game_container').style.width = board_size + '%';
    }
    board.resize();
};

function show_copy_btn(){
    document.getElementById('pgnBtn').style.display = 'block';
}

function hide_copy_btn(){
    document.getElementById('pgnBtn').style.display = 'none';
}

// add an event listener to preMove checkbox
document.getElementById('preMove').addEventListener('change', function() {
    usePreGame = this.checked;
    if (!usePreGame) reset_pre_moves();
});

document.getElementById('autoQueen').addEventListener('change', function() {
    autoQueen = this.checked;
    if (waitingForCrowning) crowning('q');
});


window.onload = (e) => {
    formatClock();
    resetSquareColor();
    document.body.style.display = 'block';
    resizeBoard();
};
