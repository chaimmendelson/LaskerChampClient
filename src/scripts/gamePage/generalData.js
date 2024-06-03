const USERNAME = 'username';
const ELO = 'elo';
const CLOCKS = 'clock';

let in_waiting = false;
let started_game = false;
let game_mode = 'online';

const clock_options_list = ['1|0', '1|1', '2|1', '3|0', '3|2', '5|0', '10|5', '15|10', '30|0'];
let choosen_clock = '1|0';

let start = null;
let delay_time = 0;

let $board = $('#myBoard')
let $pgn = $('#pgnText')
let $status = $('#status')

let board = ChessBoard('myBoard', 'start')
let game = null
let usePreGame = true;
let clickToMove = true;
let autoQueen = true;

let clientColor = null
let clientTurn = false;
let GameOver = true;
let waitingForCrowning = false;

let crowningMove = null;
let srcSquare = null;
let moveToHighlight = null;
let move_stack = [];

const squareClass = 'square-55d63'
const whiteSquareClass = 'white-1e1d7'
const blackSquareClass = 'black-3c85d'

const gameTab = 'game'
const newGameTab = 'new_game'
const settingsTab = 'settings'
const tabs = [gameTab, newGameTab, settingsTab]

const squareColors = {
    white: { background: 'mintcream', grey: 'grey', preMove: 'tomato', highlight: 'yellow', srcHighlight: 'lightblue' },
    black: { background: 'green', grey: 'dimgrey', preMove: 'orangered', highlight: 'gold', srcHighlight: 'deepskyblue' },
};

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function write_status(msg){
    document.getElementById('status').innerHTML = msg;
}

function isInGame(){
    return game != null;
}

function getCookie(){
    cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++){
        cookie = cookies[i].split('=')
        if (cookie[0] === 'chess-cookie'){
            return cookie[1];
        }
    }
    return null;
}
