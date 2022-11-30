 const chess_pieces = ['chessboardjs-1.0.0/img/chesspieces/wikipedia/bB.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bK.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bN.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bP.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bQ.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bR.png', 
                       'chessboardjs-1.0.0/img/chesspieces/wikipedia/wB.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wK.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wN.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wP.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wQ.png', 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wR.png']
 let whatPageWeOn = 0;
 function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function EnterSubmit(locStart, clicked){
    let placement = document.getElementById(locStart)
    if (locStart == 0) placement = document
    placement.addEventListener("keypress", function(event) {
        if (event.key == "Enter") {
            event.preventDefault();
            document.getElementById(clicked).click();
        }
    })
}

// addes an image that rotates, is not used
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

 // the submit button that switches between the two screens if the information is correct, and the user info
 let log_in_info = {'test': 'test'}
 let rating = 1200

 document.getElementById('submit').addEventListener("click", function() {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    document.getElementById('username').style.border = '1px solid black';
    document.getElementById('password').style.border = '1px solid black';
    if (!checkUsername(username)){
        document.getElementById('username').style.border = '2px solid red';
        return;
    }
    if (!checkPassword(password)){
        document.getElementById('password').style.border = '2px solid red';
        return;
    }
    if (username in log_in_info){
        if (log_in_info[username] == password){
            console.log('success')
            document.getElementById('rating_value').innerHTML = rating;
            document.getElementById('chess_game').style.display = 'block';
            document.getElementById('main_page').style.display = 'none';
            whatPageWeOn = 1;
            document.getElementById('username_value').innerText = username;
        }
        else {
            console.log('incorrect password');
            document.getElementById('password').style.border = '2px solid red';
        }
    }
    else {
        console.log('incorrect username');
        document.getElementById('username').style.border = '2px solid red';
    }
 });
 if (whatPageWeOn == 0){
    EnterSubmit('password', 'submit')
    EnterSubmit('username', 'submit')
 }

 function showPassword(){
    if (document.getElementById('password').type == 'text'){
        document.getElementById('password').type = 'password';
    }
    else{
        document.getElementById('password').type = 'text';
    }
    
 }

 function checkChar(char){
    let charList = ['q', 'r', 'b', 'n']
    for (let i = 0; i < charList.length; i++){
        if (char == charList[i]) return true;
    }
    return false;
 }

 function checkUsername(char){
    let regex = /^\w{3,32}$/;
    return regex.test(char);
}

function checkPassword(char){
    let regex = /^\w{3,32}$/;
    return regex.test(char);
}
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

    // Control the game - start the game, quit game and keep pgn, restart game
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


    let board = ChessBoard('myBoard', 'start')
    let game = null
    let $status = $('#status')
    let $fen = $('#fen')
    let $pgn = $('#pgn')
    let whiteSquareGrey = 'silver'
    let blackSquareGrey = 'darkgrey'

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
        if (piece === 'p' && (target[1] === '1' || target[1] === '8')){
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
        const createImage = document.createElement('img')
        document.body.appendChild(createImage)
        status = 'Game over, ' + moveColor + ' is in checkmate.'
        document.getElementById("startBtn").disabled = false;
        if (moveColor == "White") document.getElementById('white_king_dsp').src = 'additional_images/wKx.png';
        else document.getElementById('black_king_dsp').src = 'additional_images/bKx.png';
    }
    if (!game.isCheckmate()) {
        document.getElementById('white_king_dsp').src = 'chessboardjs-1.0.0/img/chesspieces/wikipedia/wK.png';
        document.getElementById('black_king_dsp').src = 'chessboardjs-1.0.0/img/chesspieces/wikipedia/bK.png';
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

    function showLasker(){
        confirm_the_process = 'I hereby confirm the process'
        let prompter = prompt('do you wish to learn more about Lasker?\nType "'+confirm_the_process+'" if yes (in exactly the same letter case).')
        if (prompter == confirm_the_process){
            let aLinkToLasker = document.createElement('a');
            aLinkToLasker.target = '_blank';
            aLinkToLasker.href = 'https://en.wikipedia.org/wiki/Emanuel_Lasker';
            aLinkToLasker.click();
        }
    }
    
document.getElementById('username').value = 'test';
document.getElementById('password').value = 'test';
    // allows costomization WIP
    let ChessStyleMode = 0;
    document.getElementById('customizeBtn').addEventListener("click", function(){
        return true;
       if (ChessStyleMode == 3) ChessStyleMode = 0;
       else ChessStyleMode++;
       const white_squares = document.querySelectorAll('.white-1e1d7');
       white_squares.forEach(squareW => {
           if (ChessStyleMode == 0) {
               squareW.style.background = 'azure';
           }
           else if (ChessStyleMode == 1) {
               squareW.style.background = '#f0d9b5';
           }
           else if (ChessStyleMode == 2) {
               squareW.style.background = 'tan';
           }
           else{
               squareW.style.background = 'mintcream';
           }
       });
       const black_squares = document.querySelectorAll('.black-3c85d');
       black_squares.forEach(squareB => {
           if (ChessStyleMode == 0) {
               squareB.style.background = 'lightskyblue';
           }
           else if (ChessStyleMode == 1) {
               squareB.style.background = '#b58863';
           }
           else if (ChessStyleMode == 2) {
               squareB.style.background = 'saddlebrown';
           }
           else {
               squareB.style.background = 'limegreen';
           }
       })
    });

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
console.log('test')
