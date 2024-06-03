function isPlyersPiece(piece){
    return (piece[0] === clientColor);
}

function showCrowningOptions(){
    let square = crowningMove.to;
    let position = board.position();
    delete position[crowningMove.from]
    let pieces = ['Q', 'R', 'B', 'N'];
    for (const piece of pieces){
        position[square] = clientColor + piece;
        $board.find(specificSquareClass(square)).css('background', 'white');
        move = clientColor === WHITE ? -1 : 1;
        square = moveSquaresOnBoard(square, move, 0);
    }
    board.position(position, false);
}

function crowning(piece){
    crowningMove.promotion = piece;
    if (!usePreGame) commit_move(crowningMove);
    else
    {
        if(move_stack.length === 0 && clientTurn) commit_move(crowningMove);
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