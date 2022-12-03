//Game control btns
document.getElementById("startBtn").addEventListener("click", function() {
    start_game();
}); // start
document.getElementById("quitBtn").addEventListener("click", function() {
    if (confirm("Quit?")){
        document.getElementById("startBtn").disabled = false;
        board = ChessBoard('myBoard', 'start');
    }
}); // quit
document.getElementById("restartBtn").addEventListener("click", function() {
    if (confirm("Restart?")){
        start_game();
    }
}); // restart

async function start_game(){
    document.getElementById("startBtn").disabled = true;
    board = ChessBoard('myBoard', config)
    game = new Chess()
    color = await socket.emit('start_game')
    console.log(color)
    updateStatus()
}

// variables for the information on the board and of the board
let board = ChessBoard('myBoard', 'start')
let game = null
let can_move = false;
let $status = $('#status')
let $fen = $('#fen')
let $pgn = $('#pgn')
let whiteSquareGrey = 'silver'
let blackSquareGrey = 'darkgrey'

// highlight
function removeGreySquares () {
    $('#myBoard .square-55d63').css('background', '')
}
function greySquare (square) {
let $square = $('#myBoard .square-' + square)

let background = whiteSquareGrey
if ($square.hasClass('black-3c85d')) {
    background = blackSquareGrey
}

$square.css('background', background)
}

// control piece movement
function onDragStart (source, piece, position, orientation) {
    if (!can_move) return false;
    // do not pick up pieces if the game is over
    if (game.isCheckmate() || game.isDraw()) return false

    // only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false
    }
}
function onDrop (source, target) {
    // see if the move is legal
    removeGreySquares()
    let piece = game.get(source).type
    let move = null;
    let promotion = null;
    if (piece === 'p' && (target[1] === '1' || target[1] === '8')){
        promotion = window.prompt('Promote to: (q, r, b, n)')
        move = game.move({
            from: source,
            to: target,
            promotion: promotion
        })
    }
    else{
        move = game.move({
            from: source,
            to: target
        })
    }
    // illegal move
    if (move === null) return 'snapback'
    let move_str = move.from + move.to
    if (move.promotion){
        move_str += move.promotion
    }
    console.log(move_str)
    updateStatus()
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    board.position(game.fen())
}
// update status as of turn
function updateStatus () {
    let status = ''

    let moveColor = 'White'
    if (game.turn() === 'b') {
        moveColor = 'Black'
    }

    // checkmate?
    if (game.isCheckmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.'
        document.getElementById("startBtn").disabled = false;
    }

    // draw?
    else if (game.isDraw()) {
        status = 'Game over, drawn position'
        document.getElementById("startBtn").disabled = false;
    }

    // game still on
    else {
        status = moveColor + ' to move'

        // check?
        if (game.isCheck()) {
        status += ', ' + moveColor + ' is in check'
        }
}

$status.html(status)
$fen.html(game.fen())
$pgn.html(game.pgn())
}
// check legal moves and highlight legal moves
function onMouseoverSquare (square, piece) {
// get list of possible moves for this square
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
    removeGreySquares()
}

// configure site
let config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onMouseoutSquare: onMouseoutSquare,
    onMouseoverSquare: onMouseoverSquare,
    onSnapEnd: onSnapEnd
}

// copying logged info to clipboard
    //FEN
document.getElementById("copy_fen").addEventListener("click", function() {
    if (game){
        navigator.clipboard.writeText(game.fen())
        console.log(game.fen())
    }
});
    //PGN
document.getElementById("copy_pgn").addEventListener("click", function() {
    if (game){
        navigator.clipboard.writeText(game.pgn())
        console.log(game.pgn())
    }
});
const socket = io({
    auth: {
      token: localStorage.getItem('chess-cookie')
    }
});
 socket.on('connect', () => {
    console.log('Connected to server');
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
 socket.on('opponent_ move', (data) => {
    console.log('opponent move: ' + data);
 })
async function validate_login(){
    cookie = localStorage.getItem('chess-cookie')
    console.log(cookie)
    if (cookie) {
        const response  = await fetch('/validate', {
            method: 'GET',
            headers: {
                'chess-cookie': cookie
            }
        })
        if (response.status === 200){
            console.log('logged in');
            return true;
        }
    }
    window.location.href = '/login';
}
window.onload = validate_login