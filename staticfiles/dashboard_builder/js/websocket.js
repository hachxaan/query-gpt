document.addEventListener("DOMContentLoaded", function() {
    
    const chatSocket = new WebSocket(`ws://${window.location.host}/ws/dashboard/${dashboardUuid}/`);

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("Message received:", data.message);
        let messageHTML = `<div class="message"><p><strong>${data.sender}:</strong> ${data.message}</p></div>`;
        let chatMessages = document.getElementById('cnt-messages');
        chatMessages.innerHTML += messageHTML;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error("Chat socket closed unexpectedly");
    };

    document.getElementById('send-button').onclick = function() {
        sendMessage(chatSocket);
    };

    document.getElementById('chat-input').onkeypress = function(e) {
        if (e.which == 13) {
            sendMessage(chatSocket);
            e.preventDefault();
        }
    };
});

function sendMessage(chatSocket) {
    const inputElem = document.getElementById('chat-input');
    const message = inputElem.value.trim();

    if (message !== "") {
        chatSocket.send(JSON.stringify({ 'message': message }));
        inputElem.value = '';
    }
}
