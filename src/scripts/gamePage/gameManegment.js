function updateTurn(){
    clientTurn = game.turn() == clientColor;
    updateStatus();
}

function startGame(){
    clearChat()
    board = ChessBoard('myBoard', config);
    if (clientColor == BLACK) board.flip();
    game = new Chess();
    moveToHighlight = null;
    updateTurn();
    resetPosition();
    GameOver = false;
}

function clear_game(message, elo){
    resetBoard();
    $status.html(message);
    clientElo = elo
    setInfo();
    game = null;
}

// update status as of turn
function updateStatus () {
    let status = ''
    // checkmate?
    if (GameOver) stopClock();
    // game still on
    const moveColor = game.turn() === WHITE ? 'white' : 'black';
    status = moveColor + ' to move'
    if (game.isCheck()) status += ', ' + moveColor + ' is in check'
    $status.html(status)
    update_pgn();
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
    $pgn.html(`<pre>${pgn_lines.join('\n')}<pre>`);
}