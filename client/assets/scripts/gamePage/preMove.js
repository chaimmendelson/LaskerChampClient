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
        if (square.charCodeAt(0) !== 97) moves.push(moveSquaresOnBoard(square, up_or_down, -1));
        if (square.charCodeAt(0) !== 104) moves.push(moveSquaresOnBoard(square, up_or_down, 1));
    }
    // add castling moves if the piece is a king and its allowed
    if (piece.type === 'k') moves = moves.concat(getCastlingPreMoves());
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

function getCastlingPreMoves(){
    let moves = [];
    let castling_rights = game.fen().split(' ')[2];
    if (castling_rights === '-') return moves;
    if (clientColor === 'white'){
        for (const move of move_stack){
            if (move.from === 'e1') return moves;
            if (move.from === 'a1') castling_rights = castling_rights.replace('Q', '');
            if (move.from === 'h1') castling_rights = castling_rights.replace('K', '');
        }
        if (castling_rights.split('-')[0] === '') return moves;
        if (castling_rights.includes('K')) moves.push('g1');
        if (castling_rights.includes('Q')) moves.push('c1');
    } else {
        for (const move of move_stack){
            if (move.from === 'e8') return moves;
            if (move.from === 'a8') castling_rights = castling_rights.replace('q', '');
            if (move.from === 'h8') castling_rights = castling_rights.replace('k', '');
        }
        if (castling_rights.split('-')[1] === '') return moves;
        if (castling_rights.includes('k')) moves.push('g8');
        if (castling_rights.includes('q')) moves.push('c8');
    }
    return moves;
}