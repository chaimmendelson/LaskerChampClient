const $topClockDiv = $('#player1-clock')
const $bottomClockDiv = $('#player2-clock')

const $topClock = $('#player1-time')
const $bottomClock = $('#player2-time')

const $topPlayerInfo = $('#player1-info')
const $bottomPlayerInfo = $('#player2-info')

let clientName = '';
let clientElo = 0;
let opponentName = '';
let opponentElo = 0;


let isClientTop = false;
// Initial time for each player (in seconds)
const InitialTime = 0;

// Variables to keep track of the current time remaining for each player
let clientTimeRemaining = InitialTime;
let opponentTimeRemaining = InitialTime;

// Variable to keep track of which player's turn it is
let currentPlayer = 0;
let clientNum = 0;
// Timer interval variable
let interval;

// Function to start the clock
function startClock() {
    interval = setInterval(() => {
        // Check which player's turn it is
        if (currentPlayer === clientNum) {
            clientTimeRemaining--;
            if (clientTimeRemaining < 0) {
                clearInterval(interval);
                clientTimeRemaining = 0;
            }
        } else {
            opponentTimeRemaining--;
            if (opponentTimeRemaining < 0) {
                clearInterval(interval);
                opponentTimeRemaining = 0;
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
    if (isClientTop) {
        $topClock.text(formatTime(clientTimeRemaining));
        $bottomClock.text(formatTime(opponentTimeRemaining));
    } else {
        $topClock.text(formatTime(opponentTimeRemaining));
        $bottomClock.text(formatTime(clientTimeRemaining));
    }   
}

function setClockColor(client, opponent) {
    if (isClientTop) {
        $topClockDiv.css('background-color', client);  
        $bottomClockDiv.css('background-color', opponent);
    } else {
        $topClockDiv.css('background-color', opponent);
        $bottomClockDiv.css('background-color', client);
    }
}
// Function to reset the clock
function resetClocks() {
    stopClock();
    clientTimeRemaining = InitialTime;
    opponentTimeRemaining = InitialTime;
    currentPlayer = 0;
    formatClock();
    setClockColor('white', 'grey');
    setInfo(); 
}

function InitializeClocks(clientColor, time) {
    clientNum = clientColor === 'w' ? 0 : 1;
    isClientTop = false;
    clientTimeRemaining = time;
    opponentTimeRemaining = time;
    formatClock();
    if (clientNum === 0) setClockColor('white', 'grey');
    else setClockColor('grey', 'white');
    setInfo();
}

function setInfo(){
    if (isClientTop) {
        $topPlayerInfo.text(clientName + ' (' + clientElo + ')');
        $bottomPlayerInfo.text(opponentName + ' (' + opponentElo + ')');
    }
    else {
        $topPlayerInfo.text(opponentName + ' (' + opponentElo + ')');
        $bottomPlayerInfo.text(clientName + ' (' + clientElo + ')');
    }
}

function flipClocks() {
    isClientTop = !isClientTop;
    formatClock();
    if (clientNum === 0) setClockColor('white', 'grey');
    else setClockColor('grey', 'white');
    setInfo();
}

function update_clocks(clocks) {
    /* update the clocks with the clocks sent by the server */
    let white_clock = clocks['w'];
    let black_clock = clocks['b'];
    
    clientTimeRemaining = clientNum === 0 ? white_clock : black_clock;
    opponentTimeRemaining = clientNum === 0 ? black_clock : white_clock;
    
}