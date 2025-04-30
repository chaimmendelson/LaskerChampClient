function resetPosition(){
    if (usePreGame)
    {
        board.position(game.fen(), false);
        board.position(makeMovesOnBoard(move_stack), false);
    }
    else
    {
        board.position(game.fen());
    }
    resetSquareColor();
}


function moveSquaresOnBoard(square, up, left){
    let column = square.charCodeAt(0) + left;
    let row = square.charCodeAt(1) + up;
    if (column < 97 || column > 104 || row < 49 || row > 56) return null;
    return String.fromCharCode(column) + String.fromCharCode(row);
}

function movePieceOnBoard(position, from, to){
    position[to] = position[from];
    delete position[from];
    return position;
}

function commit_opponent_move(move){
    /* commit the move made by the opponent to the board */
    let move_d = {from: move.slice(0, 2), to: move.slice(2, 4)};
    moveToHighlight = move_d;
    if (move.length == 5){
        move_d['promotion'] = move[4];
    }
    game.move(move_d);
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

function makeMovesOnBoard(moves_l){
    let position = board.position();
    for(const move of moves_l){
        let to = move.to;
        let from = move.from;
        position = movePieceOnBoard(position, from, to);
        if ('promotion' in move && move.promotion)
            position[to] = position[to][0] + move.promotion.toUpperCase();
        else if (position[to] === 'wK' && from === 'e1'){
            if (to === 'g1') position = movePieceOnBoard(position, 'h1', 'f1');
            if (to === 'c1') position = movePieceOnBoard(position, 'a1', 'd1');
        }
        else if (position[to] === 'bK' && from === 'e8'){
            if (to === 'g8') position = movePieceOnBoard(position, 'h8', 'f8');
            if (to === 'c8') position = movePieceOnBoard(position, 'a8', 'd8');
        }
    }
    return position;
}

