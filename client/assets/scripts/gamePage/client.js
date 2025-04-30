const socket = io({
    auth: {
      token: getCookie()
    }
});

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
    menuSwitch('game');
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