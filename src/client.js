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
        var piece = game.get(source).type
        if ((piece === 'p' && target[1] === '8') || (piece === 'P' && target[1] === '1')) {
          var promotion = window.prompt('Promote to: (q, r, b, n)')
          var move = game.move({
          from: source,
          to: target,
          promotion: promotion
        })
        }
        else{
          var move = game.move({
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
        var status = ''

        var moveColor = 'White'
        if (game.turn() === 'b') {
          moveColor = 'Black'
        }

        // checkmate?
        if (game.isCheckmate()) {
            let the_winning_color;
          const createImage = document.createElement('img')
          if (moveColor == "White") { createImage.src = '/Users/martinerdfarb/Documents/GitHub/LaskerChampClient/src/chessboardjs-1.0.0/img/chesspieces/wikipedia/bK.png';  the_winning_color = "Black"}
          else if (moveColor == "Black") { createImage.src= '/Users/martinerdfarb/Documents/GitHub/LaskerChampClient/src/chessboardjs-1.0.0/img/chesspieces/wikipedia/wK.png'; the_winning_color = "White"}
          createImage.style.border = '4px gold solid'
          document.body.appendChild(createImage)
          status = 'Game over, ' + moveColor + ' is in checkmate.'
          document.getElementById("startBtn").disabled = false;
          document.getElementById("game_over").innerText = "Game Over!!! Player " + the_winning_color + " Has Won The Game!";
        }

        // draw?
        else if (game.isDraw()) {
          status = 'Game over, drawn position'
          document.getElementById("startBtn").disabled = false;
          document.getElementById("game_over").innerText = "Game Over! Both Players Win (Or in Reality Lose)!";
          
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

      var config = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd
      }



    document.getElementById("copy_fen").addEventListener("click", function() {
        navigator.clipboard.writeText(board.fen())
        console.log(board.fen())
    });