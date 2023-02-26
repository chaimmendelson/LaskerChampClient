let $board = $('#myBoard')
let $status = $('#status')
let $pgn = $('#pgnText')

let board = ChessBoard('myBoard', 'start')
let game = null
let preGame = null
let usePreGame = true;
let autoQueen = true;

let playerColor = null
let PlayersTurn = false;
let GameOver = true;
let waitingForCrowning = false;

let crowningMove = null;
let moveToHighlight = null
let move_stack = [];

const whiteSquareColour = 'mintcream'
const blackSquareColour = 'green'

const whiteSquareGrey = 'grey'
const blackSquareGrey = 'dimgrey'

const whiteSquarePreMove = 'tomato'
const blackSquarePreMove = 'orangered'

const whiteSquareHighlight = 'yellow'
const blackSquareHighlight = 'gold'

const squareClass = 'square-55d63'
const whiteSquareClass = 'white-1e1d7'
const blackSquareClass = 'black-3c85d'

function specificSquareClass(square){
    return '.square-' + square;
}

function isWhiteSquare(square){
    return !(square.charCodeAt(0) % 2 === square.charCodeAt(1) % 2);
}

function isPlyersPiece(piece){
    return (piece[0] === playerColor);
}

function highlightSquare(square){
    let background = isWhiteSquare(square) ? whiteSquareHighlight : blackSquareHighlight;
    $board.find(specificSquareClass(square)).css('background', background)
}

function highlightPreMoveSquare(square){
    let background = isWhiteSquare(square) ? whiteSquarePreMove : blackSquarePreMove;
    $board.find(specificSquareClass(square)).css('background', background)
}

function highlightPreMoves(){
    for (const move of move_stack){
        highlightPreMoveSquare(move.from);
        highlightPreMoveSquare(move.to);
    }
}

function highlightMove() {
    if (moveToHighlight) {
        highlightSquare(moveToHighlight.from);
        highlightSquare(moveToHighlight.to);
    }
}

function greySquare (square) {
    let background = isWhiteSquare(square) ? whiteSquareGrey : blackSquareGrey;
    $board.find(specificSquareClass(square)).css('background', background)
}

function resetSquareColor(){
    $board.find('.' + whiteSquareClass).css('background', whiteSquareColour)
    $board.find('.' + blackSquareClass).css('background', blackSquareColour)
    highlightMove();
    if (usePreGame) highlightPreMoves();
    if (waitingForCrowning) showCrowningOptions();
}

function resetPosition(){
    if (usePreGame){
        board.position(game.fen(), false);
        board.position(makeMovesOnBoard(move_stack), false);
    }
    else board.position(game.fen());
    resetSquareColor();
}


function moveSquaresOnBoard(square, up, left){
    let column = square.charCodeAt(0) + left;
    let row = square.charCodeAt(1) + up;
    if (column < 97 || column > 104 || row < 49 || row > 56) return null;
    return String.fromCharCode(column) + String.fromCharCode(row);
}

function showCrowningOptions(){
    let square = crowningMove.to;
    let position = board.position();
    delete position[crowningMove.from]
    let pieces = ['Q', 'R', 'B', 'N'];
    for (const piece of pieces){
        position[square] = playerColor + piece;
        $board.find(specificSquareClass(square)).css('background', 'white');
        move = playerColor === WHITE ? -1 : 1;
        square = moveSquaresOnBoard(square, move, 0);
    }
    board.position(position, false);
}

function makeMovesOnBoard(moves_l){
    let position = board.position();
    for(const move of moves_l){
        let to = move.to;
        let from = move.from;
        position[to] = position[from];
        delete position[from];
        if ('promotion' in move && move.promotion)
            position[to] = position[to][0] + move.promotion.toUpperCase();
    }
    return position;
}

function updateTurn(){
    PlayersTurn = game.turn() === playerColor;
    updateStatus();
}

function resetBoard(){
    GameOver = true;
    stopClock();
    move_stack = [];
    resetPosition();
    moveToHighlight = null;
    $status.html('');
}

function startGame(color){
    playerColor = color == 'white' ? WHITE : BLACK
    board = ChessBoard('myBoard', config);
    if (playerColor == BLACK) board.flip();
    game = new Chess();
    updateTurn();
    resetPosition();
    GameOver = false;
}

function clear_game(message){
    resetBoard();
    $status.html(message);
    document.getElementById('startBtn').style.display = 'block';
    document.getElementById('quitBtn').style.display = 'none';
    document.getElementById('startBtn').disabled = false;
}

// control piece movement
function onDragStart (source, piece, position, orientation) {
    if (GameOver || !isPlyersPiece(piece)) return false;
    if (waitingForCrowning){
        crowning(piece[1].toLowerCase());
        return false;
    }
    if (!usePreGame && !PlayersTurn) return false;
    return true;
}

function crowning(piece){
    crowningMove.promotion = piece;
    if (!usePreGame) commit_move(crowningMove);
    else
    {
        if(move_stack.length === 0 && PlayersTurn) commit_move(crowningMove);
        else move_stack.push(crowningMove);
    }
    waitingForCrowning = false;
    resetPosition();
}

function doesMoveExist(source, target){
    let moves = game.moves({ verbose: true });
    return moves.find(move => move.from === source && move.to === target);
}


function validateMove(source, target, preMove=false) 
{
    let validMoves = null;
    let move = null;
    if (preMove){
        validMoves = get_all_moves(source);
        move = validMoves.find(move => move.to === target);
    }
    else{
        validMoves = game.moves({ verbose: true });
        move = validMoves.find(move => move.from === source && move.to === target);
    }
    if (!move) return null;
    if ('promotion' in move && move.promotion) 
    {
        waitingForCrowning = true;
        crowningMove = {from: source, to: target}
        if (autoQueen) crowning('q');
        resetSquareColor();
        return null;
    }
    return {from: source, to: target, promotion: ''};
}

function moveColor() {
    return game.turn() === WHITE ? 'white' : 'black';
}


function onDrop(source, target) {
    if (!usePreGame || (usePreGame && move_stack.length === 0 && PlayersTurn)){
        const move = validateMove(source, target);
        if (!move) return 'snapback';
        commit_move(move);
    }
    else{
        const move = validateMove(source, target, true);
        if (!move) return 'snapback';
        move_stack.push(move);
    }
}

function commit_move(move){
    moveToHighlight = move;
    game.move(move);
    updateTurn();
    let move_str = `${move.from}${move.to}${move.promotion}`;
    socket.emit('my_move', {move: move_str});
    nextPlayer();
    return true;
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
    resetPosition();
}

// update status as of turn
function updateStatus () {
    let status = ''
    // checkmate?
    if (GameOver) stopClock();
    // game still on
    status = moveColor() + ' to move'
    if (game.isCheck()) status += ', ' + moveColor() + ' is in check'
    $status.html(status)
    update_pgn();
}

function try_pre_move(){
    if (move_stack.length === 0) return;
    let move = move_stack.shift();
    if (doesMoveExist(move.from, move.to)) commit_move(move);
    else reset_pre_moves();
}


function reset_pre_moves(){
    move_stack = [];
    if (waitingForCrowning){
        waitingForCrowning = false;
        crowningMove = null;
    }
    if (game) resetPosition();
}

function update_pgn(){
    // the pgn is a string '1. e2 e4 2. e7 e5'
    // we want to display it as a table
    let pgn = game.pgn();
    let lines = pgn.split(' ');
    let pgn_lines = [];
    let line = '';
    for (let i = 0; i < lines.length; i++)
    {
        if (i % 3 === 0)
        {
            if (i !== 0){
                pgn_lines.push(line);
                line = '';
            }
            line += lines[i].padEnd(4);
        }
        else line += lines[i].padEnd(8);
    }
    pgn_lines.push(line);
    $pgn.html(pgn_lines.join('\n'));
}

// check legal moves and highlight legal moves
function onMouseoverSquare (square, piece) {
// get list of possible moves for this square
    let moves = null;
    if(!isPlyersPiece(piece) || GameOver || waitingForCrowning) return;
    if (!PlayersTurn && usePreGame) 
        moves = get_all_moves(square);
    else 
        moves = game.moves({square: square, verbose: true});
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
//PGN
document.getElementById('pgnBtn').addEventListener('click', function() {
    if (game) navigator.clipboard.writeText(game.pgn());
});

function get_all_moves(square){
    // get all the moves a the piece on the square could have done if the board was empty
    let piece = board.position()[square];
    piece = {type: piece[1].toLowerCase(), color: piece[0]}
    let test_game = new Chess();
    test_game.clear();
    test_game.put(piece, square);
    test_game._turn = piece.color;
    let moves = test_game.moves({square: square, verbose: true});
    // replace each move with only the to square
    for (let i = 0; i < moves.length; i++){
        moves[i] = moves[i].to;
    }
    if (piece.type === 'p'){
        up_or_down = piece.color === 'w' ? 1 : -1;
        if (square.charCodeAt(0) !== 97) 
            moves.push(String.fromCharCode(square.charCodeAt(0) - 1) + (parseInt(square[1]) + up_or_down));
        if (square.charCodeAt(0) !== 104) 
            moves.push(String.fromCharCode(square.charCodeAt(0) + 1) + (parseInt(square[1]) + up_or_down));
    }
    // add castling moves if the piece is a king and its allowed
    if (piece.type === 'k'){
        castling_rights = game.fen().split(' ')[2];
        if (playerColor === 'white'){
            if (castling_rights.includes('K')) moves.push('g1');
            if (castling_rights.includes('Q')) moves.push('c1');
        } else {
            if (castling_rights.includes('k')) moves.push('g8');
            if (castling_rights.includes('q')) moves.push('c8');
        }
    }
    // remove duplicates
    moves = moves.filter((move, index) => moves.indexOf(move) === index);
    let all_moves = [];
    for (let i = 0; i < moves.length; i++){
        let move = moves[i];
        let promotion = null;
        if (piece.type === 'p' && (move[1] === '8' || move[1] === '1')){
            promotion = 'q';
        }
        all_moves.push({from: square, to: move, promotion: promotion});
    }
    return all_moves;
}


document.getElementById('flipBtn').addEventListener('click', function() {
    board.flip();
});