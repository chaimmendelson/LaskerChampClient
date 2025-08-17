// store messages, self and opponent messages

// define message object

const messages = []


const getMessages = () => {
    return messages
}

const clearMessages = () => {
    messages.length = 0
}

const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(text, isSelf = true) {
    const messageData = { message: text, self: isSelf };
    messages.push(messageData);

    const msgDiv = document.createElement('div');
        msgDiv.className = 'message ' + (isSelf ? 'self' : 'other');
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
}

const clearChat = () => {
    chatBox.innerHTML = '';
    clearMessages();
}

sendBtn.addEventListener('click', () => {

  if (!isInGame()){
    alert("You are not in a game. Please start or join a game to chat.");
    return;
  }
    const text = chatInput.value.trim();
    console.log(text);
    if (text) {
      addMessage(text, true);
      console.log("sending message");
      socket.emit("message", text);
      chatInput.value = '';
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendBtn.click();
    }
});