console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
    console.log(textField.value)
    textField.value = null
})

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    console.log(e.data);
    const text = e.data;

    const elMsg = document.createElement('div');
    console.log(text)
    elMsg.textContent = text;
    messageWindow.insertBefore(elMsg, messageWindow.firstChild);
    messageWindow.scrollTop = messageWindow.scrollHeight;
};
