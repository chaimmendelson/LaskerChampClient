 const black_pieces = ['chessboardjs-1.0.0/img/chesspieces/wikipedia/bB.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bK.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bN.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bP.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bQ.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bR.png']
 const white_pieces = ['chessboardjs-1.0.0/img/chesspieces/wikipedia/wB.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wK.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wN.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wP.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wQ.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wR.png']
 let whatPageWeOn = 0;
 function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}
 function rotatingImage(source, posX, posY, Width, speedMode){
    let rotationSpeed = 4;
    if (speedMode == 1) rotationSpeed = getRandomInt(5)
    if (rotationSpeed == 0) rotationSpeed = 4
    const Image = document.createElement('img');
    Image.src = source;
    Image.style.cssText = `
        position: absolute;
        top: `+posY+`px;
        left: `+posX+`px;
        width:`+Width+`px;
        height: auto;
        margin:-60px 0 0 -60px;
        -webkit-animation:spin `+rotationSpeed+`s linear infinite;
        -moz-animation:spin `+rotationSpeed+`s linear infinite;
        animation:spin `+rotationSpeed+`s linear infinite;
    `;
    document.body.appendChild(Image)
 }




 let log_in_info_user = ['test', 'username'];
 let log_in_info_pass = ['test', 'password'];

 document.getElementById('submit').addEventListener("click", function() {
    let user_txt = document.getElementById('username').value;
    let pass_txt = document.getElementById('username').value;
    console.log(user_txt)
    // doesn't work, for some reason always returns 'success' in the console
    if (log_in_info_user.indexOf(user_txt) == log_in_info_user.indexOf(pass_txt)) console.log('success')
 });
 
/* Add the spinning images, because...
for (i=1;i<15;i++){
    if (whatPageWeOn == 0){
     rotatingImage(black_pieces[getRandomInt(6)], i*100, 100, 100, 1)
     rotatingImage(white_pieces[getRandomInt(6)], i*100, 200, 100, 1)
    }
}
if (whatPageWeOn == 0){
    rotatingImage(black_pieces[getRandomInt(6)], 0, 0, 100, 1)
    rotatingImage(white_pieces[getRandomInt(6)], document.body.clientWidth-100, 0, 100, 1)
}
*/
    document.getElementById("startBtn").addEventListener("click", function() {
        document.getElementById("startBtn").disabled = true;
        board = ChessBoard('myBoard', config)
        game = new Chess()
        updateStatus()
    });
    document.getElementById("quitBtn").addEventListener("click", function() {
        if (confirm("Quit?")){
            document.getElementById("startBtn").disabled = false;
            board = ChessBoard('myBoard', 'start');
        }
    });
    document.getElementById("restartBtn").addEventListener("click", function() {
        if (confirm("Restart?")){
            document.getElementById("startBtn").disabled = true;
            board = ChessBoard('myBoard', config)
            game = new Chess()
            updateStatus()
        }
    });
    document.getElementById('switch_to_game').addEventListener("click", function() {
        document.getElementById('chess_game').style.display = 'block';
        document.getElementById('main_page').style.display = 'none';
        whatPageWeOn = 1;
    });
    let board = ChessBoard('myBoard', 'start')
    let game = null
    let $status = $('#status')
    let $fen = $('#fen')
    let $pgn = $('#pgn')
    let whiteSquareGrey = '#d9d95b'
    let blackSquareGrey = '#a6a629'

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


    function onDragStart (source, piece, position, orientation) {
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
        if ((piece === 'p' && target[1] === '8') || (piece === 'P' && target[1] === '1')) {
            let promotion = window.prompt('Promote to: (q, r, b, n)')
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
        updateStatus()
    }

    // update the board position after the piece snap
    // for castling, en passant, pawn promotion
    function onSnapEnd () {
        board.position(game.fen())
    }

    function updateStatus () {
    let status = ''

    let moveColor = 'White'
    if (game.turn() === 'b') {
        moveColor = 'Black'
    }

    // checkmate?
    if (game.isCheckmate()) {
        let the_winning_color;
        const createImage = document.createElement('img')
        document.body.appendChild(createImage)
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


    let config = {
    draggable: true,
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onMouseoutSquare: onMouseoutSquare,
    onMouseoverSquare: onMouseoverSquare,
    onSnapEnd: onSnapEnd
    }



    document.getElementById("copy_fen").addEventListener("click", function() {
        if (game){
            navigator.clipboard.writeText(game.fen())
            console.log(game.fen())
        }
    });

    document.getElementById("copy_pgn").addEventListener("click", function() {
        if (game){
            navigator.clipboard.writeText(game.pgn())
            console.log(game.pgn())
        }
    });