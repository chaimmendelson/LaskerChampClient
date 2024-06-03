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

function menuSwitch(name) {
    let isTheTab = true
    for (let i = 0; i < tabs.length; i++){
        isTheTab = tabs[i] == name;
        document.getElementById(tabs[i] + "_toggle_content").style.display = isTheTab ? 'block' : 'none';
        document.getElementById(tabs[i]).style.backgroundColor = isTheTab ? 'grey': 'black';
    }
}

function gameTypeSwitch(type){
    game_mode = type;
    document.getElementById('engine_display').style.display = type === 'online' ? 'none' : 'block';
    document.getElementById('online_display').style.display = type === 'online' ? 'block' : 'none';

    document.getElementById('Engine').style.backgroundColor = type === 'online' ? 'slategrey' : 'darkslategrey';
    document.getElementById('Online').style.backgroundColor = type === 'online' ? 'darkslategrey' : 'slategrey';
}

function timeSwitch(time){
    choosen_clock = time;
    document.getElementById(`${time}`).style.backgroundColor = 'darkslategrey';
    for (let i = 0; i < clock_options_list.length; i++){
        if (clock_options_list[i] !== time){
            document.getElementById(`${clock_options_list[i]}`).style.backgroundColor = 'slategrey';
        }
    }
}