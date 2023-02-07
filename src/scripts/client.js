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
let board = ChessBoard('myBoard', 'start')
let $board = $('#myBoard')
let color = null
let players_color = 'white'
let game = null
let can_move = false;

let $status = $('#status')
let $fen = $('#fen')
let $pgn = $('#pgn')

let whiteSquareColour = 'mintcream'
let blackSquareColour = 'green'

let whiteSquareGrey = 'grey'
let blackSquareGrey = 'dimgrey'

let whiteSquareHighlight = 'yellow'
let blackSquareHighlight = 'gold'

let moveToHighlight = null
let squareClass = 'square-55d63'
let whiteSquareClass = 'white-1e1d7'
let blackSquareClass = 'black-3c85d'

document.getElementById('quitBtn').style.display = 'none';


function specificSquareClass(square){
    return '.square-' + square;
}

function updateGame(){
    resetSquareColor();
    updateStatus();
    can_move = game.turn() === color;
}

function isWhiteSquare(square){
    return !(square.charCodeAt(0) % 2 === square.charCodeAt(1) % 2);
}

function isPlyersPiece(piece){
    return (piece[0] === players_color[0]);
}

function resetSquareColor(){
    $board.find('.' + whiteSquareClass).css('background', whiteSquareColour)
    $board.find('.' + blackSquareClass).css('background', blackSquareColour)
    if (moveToHighlight) highlightMove();
}

function highlightSquare(square){
    let background = isWhiteSquare(square) ? whiteSquareHighlight : blackSquareHighlight;
    $board.find(specificSquareClass(square)).css('background', background)
}

function highlightMove() {
    highlightSquare(moveToHighlight.from);
    highlightSquare(moveToHighlight.to);
}


function greySquare (square) {
    let background = isWhiteSquare(square) ? whiteSquareGrey : blackSquareGrey;
    $board.find(specificSquareClass(square)).css('background', background)
}

function clear_game(message){
    can_move = false;
    moveToHighlight = null;
    stopClock();
    $status.html(message);
    document.getElementById('startBtn').style.display = 'block';
    document.getElementById('quitBtn').style.display = 'none';
    document.getElementById('startBtn').disabled = false;
}

// control piece movement
function onDragStart (source, piece, position, orientation) {
    if (!can_move) return false;
    // do not pick up pieces if the game is over
    if (game.isCheckmate() || game.isDraw()) return false

    // only pick up pieces for the side to move
    return isPlyersPiece(piece)
}

function validateMove(source, target) {
    let validMoves = game.moves({ verbose: true });
    let move = validMoves.find(move => move.from === source && move.to === target);
    let promotion = '';
    if (!move) return null;
    if ('promotion' in move) {
        let validPromotions = ['q', 'r', 'b', 'n'];
        promotion = prompt(`Please enter a promotion piece (${validPromotions.join(', ')}):`);
        while (!validPromotions.includes(promotion)) {
            promotion = prompt(`Invalid promotion piece. Please enter a valid promotion piece (${validPromotions.join(', ')}):`);
        }
    }
    return { from: source, to: target, promotion: promotion};
}


function moveColor() {
    return game.turn() === 'w' ? 'white' : 'black';
}


function onDrop(source, target) {
    resetSquareColor();
    const move = validateMove(source, target);
    if (!move || !can_move) {
        return 'snapback';
    }
    moveToHighlight = move;
    game.move(move);
    updateGame();
    let move_str = `${move.from}${move.to}${move.promotion}`;
    socket.emit('my_move', {move: move_str});
    nextPlayer();
    return true;
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen())
}
// update status as of turn
function updateStatus () {
    let status = ''

    // checkmate?
    if (game.isCheckmate() || game.isDraw()) {
        stopClock();
    }
    // game still on
    else {
        status = moveColor() + ' to move'

        // check?
        if (game.isCheck()) {
        status += ', ' + moveColor() + ' is in check'
        }
    }
    $status.html(status)
    $fen.html(game.fen())
    $pgn.html(game.pgn())
}

// check legal moves and highlight legal moves
function onMouseoverSquare (square, piece) {
// get list of possible moves for this square
    if (!can_move) {
        return
    }
    let moves = game.moves({
        square: square,
        verbose: true
    })

    // exit if there are no moves available for this square
    if (moves.length === 0) return

    // highlight the square they moused over
    greySquare(square)

    // highlight the possible squares for this piece
    for (let i = 0; i < moves.length; i++) {
        greySquare(moves[i].to)
    }
}


function onMouseoutSquare (square, piece) {
    resetSquareColor()
}

// configure site
let config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onMouseoutSquare: onMouseoutSquare,
    onMouseoverSquare: onMouseoverSquare,
    onSnapEnd: onSnapEnd,
}

// copying logged info to clipboard
//FEN
document.getElementById('copy_fen').addEventListener('click', function() {
    if (game) navigator.clipboard.writeText(game.fen());
});

//PGN
document.getElementById('copy_pgn').addEventListener('click', function() {
    if (game) navigator.clipboard.writeText(game.pgn());
});

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
    if (players_color === 'white') {
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
        move[promotion] = data['promotion']
    }
    game.move(move);
    board.position(game.fen())
    nextPlayer();
    updateGame();
})

socket.on('game_started', (data) => {
    color = data[0];
    board = ChessBoard('myBoard', config);
    if (color == 'b'){
        board.flip();
    }
    game = new Chess();
    currentPlayer = 0;
    players_color = data;
    playerNum = data == 'white' ? 0 : 1;
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('quitBtn').style.display = 'block';
    startClock();
    updateGame();
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
const player1Time = 60;
const player2Time = 60;

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
    board.resize();
};
formatClock();