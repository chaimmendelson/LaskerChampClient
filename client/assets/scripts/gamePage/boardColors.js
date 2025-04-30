function specificSquareClass(square){
    return '.square-' + square;
}

function isWhiteSquare(square) {
    return !(square.charCodeAt(0) % 2 === square.charCodeAt(1) % 2);
}

function highlightSquare(square) {
    const color = isWhiteSquare(square) ? squareColors.white.highlight : squareColors.black.highlight;
    $board.find(specificSquareClass(square)).css('background', color);
}

function highlightPreMoveSquare(square) {
    const color = isWhiteSquare(square) ? squareColors.white.preMove : squareColors.black.preMove;
    $board.find(specificSquareClass(square)).css('background', color);
}

function greySquare(square) {
    const color = isWhiteSquare(square) ? squareColors.white.grey : squareColors.black.grey;
    $board.find(specificSquareClass(square)).css('background', color);
}

function highlightPreMoves() {
    for (const move of move_stack) {
        highlightPreMoveSquare(move.from);
        highlightPreMoveSquare(move.to);
    }
}

function highlightSrcSquare() {
    if (!srcSquare) return;
    const color = isWhiteSquare(srcSquare) ? squareColors.white.srcHighlight : squareColors.black.srcHighlight;
    $board.find(specificSquareClass(srcSquare)).css('background', color);
}

function highlightMove() {
    if (moveToHighlight) {
        highlightSquare(moveToHighlight.from);
        highlightSquare(moveToHighlight.to);
    }
}

function resetSquareColor() {
    const resetColor = (squareClass, color) => $board.find('.' + squareClass).css('background', color);

    resetColor(whiteSquareClass, squareColors.white.background);
    resetColor(blackSquareClass, squareColors.black.background);

    highlightMove();
    if (usePreGame) highlightPreMoves();
    if (waitingForCrowning) showCrowningOptions();
    highlightSrcSquare();
}
