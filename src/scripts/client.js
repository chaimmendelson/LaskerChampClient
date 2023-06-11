const USERNAME = 'username';
const ELO = 'elo';
const CLOCKS = 'clock';

let in_waiting = false;
let started_game = false;
let game_mode = 'online';
let choosen_clock = '1|0';

const clock_options_list = ['1|0', '1|1', '2|1', '3|0', '3|2', '5|0', '10|5', '15|10', '30|0'];

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }


function write_status(msg){
    document.getElementById('status').innerHTML = msg;
}

//Game control btns
document.getElementById('startBtn').addEventListener('click', async function() {
    if (in_waiting || started_game) return;
    started_game = true;
    resetClocks();
    game = null;
    data = {game_mode: game_mode}

    if (game_mode === 'online'){
        data['clock'] = choosen_clock;
    }

    else{
        data['level'] = document.getElementById('level_display').value;
    }

    socket.emit('start_game', data, async (data) => {
        switch (data['status']){
            case 0:
                // there was a problem
                break;
            case 1:
                // the game is starting
                break;
            case 2:
                // searching for an opponent
                searching_for_opponent();
                in_waiting = true;
                started_game = false;
                break;
        }       
    });
}); // start

function isInGame(){
    return game != null;
}

document.getElementById('quitBtn').addEventListener('click', function(){
    if (started_game || !(isInGame() || in_waiting)) return;
    if (game != null){
        quit_game()
    }
    else{
        socket.emit('quit_waiting', (data) => {
            if (data['success']){
                searching_for_opponent(false);
                in_waiting = false;
            }
        });
    }
    toggleSet('new_game');
}); // quit

// variables for the information on the board and of the board

const socket = io({
    auth: {
      token: get_cookie()
    }
});

let start = null;
let delay_time = 0;
socket.on('connect', () => {
    console.log('Connected to server');
    start = Date.now();
    socket.emit('ping', (data) => {
        delay_time = Math.round((Date.now() - start) / 1000);
    }); 
});

socket.on('connect_error', (error) => {
   console.log('Connection error: ' + error);
   window.location.href = '/login';
});

socket.on('disconnect', () => {
   console.log('Disconnected from server');
});

socket.on('login_error', (data) => {
   console.log('login error: ' + data);
});


socket.on('user', (data) => {
    clientName = data[USERNAME];
    clientElo = data[ELO];
    setInfo();
});

socket.on('opponent_move', (data) => {
    /* when the opponent makes a move, update the board and the clocks */
    commit_opponent_move(data['move']);
    update_clocks(data[CLOCKS]);
    nextPlayer();
    updateTurn();
    resetPosition();
    if (usePreGame) try_pre_move();
})


function commit_opponent_move(move){
    /* commit the move made by the opponent to the board */
    let move_d = {from: move.slice(0, 2), to: move.slice(2, 4)};
    moveToHighlight = move_d;
    if (move.length == 5){
        move_d['promotion'] = move[4];
    }
    game.move(move_d);
}

socket.on('game_started', (data) => {
    /* when the game starts, update the clocks and the board and all the other information */
    clientColor = data.color
    searching_for_opponent(false);
    startGame();

    let opponent = data.opponent;
    opponentName = opponent[USERNAME];
    opponentElo = opponent[ELO];
    InitializeClocks(clientColor, data['clock'][clientColor]);

    startClock();
    started_game = false;
    in_waiting = false;
    toggleSet('game');
})

socket.on('timeout', (data) => {
    clear_game('you have run out of time', data['elo']);
    update_clocks(data['clock']);
});

socket.on('game_over', (data) => {
    /* call the clear_game function with the appropriate message */
    commit_opponent_move(data['move']);
    update_clocks(data['clock']);
    let msg = {'-1': 'you have lost', '0': 'its a tie', '1': 'you have won'}[data['resault']];
    clear_game(msg, data['elo']);
});

socket.on('opponent_quit', (data) => {
    clear_game('your opponent quit the match', data['elo']);
    update_clocks(data['clock']);
});

socket.on('opponent_timeout', (data) => {
    clear_game('your opponent ran out of time', data['elo']);
    update_clocks(data['clock']);
});


socket.on('move_received', (data) => {
    update_clocks(data['clock']);
});

async function quit_game(){
    await socket.emit('quit_game', (data) => {
        clear_game('you have quit the match', data['elo']);
    });
}


function get_cookie(){
    cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++){
        cookie = cookies[i].split('=')
        if (cookie[0] === 'chess-cookie'){
            return cookie[1];
        }
    }
    return null;
}

// get the value of the slide bar engine_level upon sliding it and log it
document.getElementById('engine_level').addEventListener('input', function() {
    engine_level = this.value;
    document.getElementById('level_display').innerHTML = 'Level: ' + engine_level;
});


document.getElementById('logoutBtn').addEventListener('click', function() {
    document.cookie = 'chess-cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = '/';
});

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

function show_copy_btn(){
    document.getElementById('pgnBtn').style.display = 'block';
}

function hide_copy_btn(){
    document.getElementById('pgnBtn').style.display = 'none';
}




function set_msg_box(){
    let board_height = document.getElementById('myBoard').offsetHeight;
    document.getElementById('msg_box').style.top = (board_height) * (0.55) + 'px';
}

function searching_for_opponent(display=true){
    if (display){
        document.getElementById('msg_box').innerHTML = 'searching for an opponent...';
        set_msg_box();
        document.getElementById('msg_box').style.display = 'block';
        document.getElementById('myBoard').style.opacity = '0.5';
    }
    else{
        document.getElementById('msg_box').style.display = 'none';
        document.getElementById('myBoard').style.opacity = '1';
    }
}


function on_resize(){
    resizeBoard();
    set_msg_box();
}

document.getElementById('flipBtn').addEventListener('click', function() {
    board.flip();
    flipClocks();
});

function addSettingRow(name) {
    const tableBody = document.querySelector("#settings_t tbody");
  
    const newRow = document.createElement("tr");
    newRow.innerHTML = `
      <td><span class="settings-name">${name}</span></td>
      <td>
        <label class="switch">
          <input type="checkbox" id="${name}-slider" checked>
          <span class="settingsSlider round"></span>
        </label>
      </td>
    `;
  
    tableBody.appendChild(newRow);
  }  


function toggleSet(name) {
    let toggles = ['game', 'new_game', 'settings']
    for (let i = 0; i < toggles.length; i++){
        if (toggles[i] === name){
            document.getElementById(toggles[i] + "_toggle_content").style.display = 'block';
            document.getElementById(toggles[i]).style.backgroundColor = 'grey';
        }
        else{
            document.getElementById(toggles[i] + "_toggle_content").style.display = 'none';
            document.getElementById(toggles[i]).style.backgroundColor = 'black';
        }
    }
}

function game_type(type){
    game_mode = type;

    document.getElementById('engine_display').style.display = type === 'online' ? 'none' : 'block';
    document.getElementById('online_display').style.display = type === 'online' ? 'block' : 'none';

    document.getElementById('Engine').style.backgroundColor = type === 'online' ? 'slategrey' : 'darkslategrey';
    document.getElementById('Online').style.backgroundColor = type === 'online' ? 'darkslategrey' : 'slategrey';
}

function select_time(time){
    choosen_clock = time;
    document.getElementById(`${time}`).style.backgroundColor = 'darkslategrey';
    for (let i = 0; i < clock_options_list.length; i++){
        if (clock_options_list[i] !== time){
            document.getElementById(`${clock_options_list[i]}`).style.backgroundColor = 'slategrey';
        }
    }
}

function add_clock_option(){
    let id_l = ['bullet', 'blitz', 'rapid'];
    let time_l = [['1|0', '1|1', '2|1'], ['3|0', '3|2', '5|0'], ['10|5', '15|10', '30|0']];
    for (let i = 0; i < id_l.length; i++){
        for (let j = 0; j < time_l[i].length; j++){
            let div = document.createElement('div');
            div.className = 'clock_time';
            div.innerHTML = time_l[i][j];
            div.id = time_l[i][j];
            div.onclick = function(){select_time(this.id)};
            document.getElementById(id_l[i]).appendChild(div);
        }
    }
    document.getElementById('1|0').style.backgroundColor = 'darkslategrey';
}

window.onload = (event) => {
    resetClocks();
    resetSquareColor();
    add_clock_option();
    addSettingRow('Premove');
    addSettingRow('Auto-Queen');
    document.body.style.display = 'block';
    on_resize();
  
    document.getElementById('Premove-slider').addEventListener('change', (event) => {
      usePreGame = event.currentTarget.checked;
      if (!usePreGame) reset_pre_moves();
    });
  
    document.getElementById('Auto-Queen-slider').addEventListener('change', (event) => {
      autoQueen = event.currentTarget.checked;
      if (waitingForCrowning) crowning('q');
    });
  };
  
  
  


