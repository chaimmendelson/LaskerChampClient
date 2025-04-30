function add_clock_option(){
    let id_l = ['bullet', 'blitz', 'rapid'];
    let time_l = [['1|0', '1|1', '2|1'], ['3|0', '3|2', '5|0'], ['10|5', '15|10', '30|0']];
    for (let i = 0; i < id_l.length; i++){
        for (let j = 0; j < time_l[i].length; j++){
            let div = document.createElement('div');
            div.className = 'clock_time';
            div.innerHTML = time_l[i][j];
            div.id = time_l[i][j];
            div.onclick = function(){timeSwitch(this.id)};
            document.getElementById(id_l[i]).appendChild(div);
        }
    }
    document.getElementById('1|0').style.backgroundColor = 'darkslategrey';
}

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

    // add event listeners
    document.getElementById('engine_level').addEventListener('input', function() {
        engine_level = this.value;
        document.getElementById('level_display').innerHTML = 'Level: ' + engine_level;
    });
    
    document.getElementById('logoutBtn').addEventListener('click', function() {
        document.cookie = 'chess-cookie=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        window.location.href = '/';
    });

    document.getElementById('flipBtn').addEventListener('click', function() {
        board.flip();
        flipClocks();
    });

    document.getElementById('startBtn').addEventListener('click', async function() {
        menuSwitch(gameTab);
        if (in_waiting || started_game || isInGame()) return;
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
        menuSwitch('new_game');
    }); // quit
};