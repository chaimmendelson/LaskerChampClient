function resetBoard(){
    GameOver = true;
    stopClock();
    move_stack = [];
    resetPosition();
    $status.html('');
}

// check legal moves and highlight legal moves
function onMouseoverSquare (square, piece) {
// get list of possible moves for this square
    let moves = null;
    if(!isPlyersPiece(piece) || GameOver || waitingForCrowning) return;
    if (!clientTurn && usePreGame) 
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

function onDragStart (source, piece, position, orientation) {
    if (GameOver || !isPlyersPiece(piece)) return false;
    if (waitingForCrowning){
        crowning(piece[1].toLowerCase());
        return false;
    }
    if (!usePreGame && !clientTurn) return false;
    return true;
}

function onDrop(source, target) {
    if (!usePreGame || (usePreGame && move_stack.length === 0 && clientTurn)){
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

function onSnapEnd () {
    resetPosition();
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
// document.getElementById('pgnBtn').addEventListener('click', function() {
//     if (game) navigator.clipboard.writeText(game.pgn());
// });

function resizeBoard(){
    let screen_height = window.innerHeight * 0.90;
    let screen_width = window.innerWidth;
    let size = Math.min(screen_height, screen_width) - 25;
    let con_width, con_height;
    if ((size + 300) < screen_width){
        document.getElementById('container').style.flexDirection = 'row';
        con_width = Math.min(screen_width - screen_height, 500);
        con_height = Math.min(screen_height, size);
    }
    else{
        document.getElementById('container').style.flexDirection = 'column';
        con_width = Math.min(screen_width, size);
        con_height = Math.min(size - screen.height, size);
    }
    con_width = Math.max(con_width, 300);
    size = Math.max(size, 300)
    document.getElementById('con').style.width = `${con_width}px`;

    document.getElementById('game_container').style.width = size + 'px';
    document.getElementById('game_container').style.maxWidth = size + 'px';

    document.getElementById('con').style.height = con_height + 'px';
    document.getElementById('con').style.maxHeight = con_height + 'px';
    board.resize();
};