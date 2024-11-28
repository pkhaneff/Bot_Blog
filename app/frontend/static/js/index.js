API_CHAT_URL = `http://127.0.0.1:8090/api/bot/stream_chat/`;

document.addEventListener("DOMContentLoaded", () => {
  const inputField = document.getElementById("input");
  const conversationId = document.getElementById("conversation_id");
  inputField.addEventListener("keydown", (e) => {
    if (e.code === "Enter") {
      let input = inputField.value;
      let conversation_id = conversationId.value
      inputField.value = "";
      output(input, API_CHAT_URL, conversation_id);
    }
  });
});

var textarea = document.getElementById('input');

textarea.addEventListener('input', function () {
    this.style.height = 'auto'; 
    this.style.height = (this.scrollHeight) + 'px'; 
    if (this.scrollHeight > 100) {
        this.style.overflowY = 'scroll';
    } else {
        this.style.overflowY = 'hidden';
    }
});

function output(input, API_CHAT_URL, conversation_id) {
  sendMessage(input, API_CHAT_URL, conversation_id);
}

async function sendMessage(input, API_CHAT_URL, conversation_id) {
    const messagesContainer = document.getElementById("messages");

    // Create a message container div
    let messageDiv = document.createElement("div");
    messageDiv.className = "message-container";

    // Create user message span
    let userSpan = document.createElement("span");
    userSpan.className = "user-message";
    userSpan.innerHTML = `<img src="../static/images/user.jpg" class="avatar"><span>${input}</span>`;
    messageDiv.appendChild(userSpan);

    messagesContainer.appendChild(messageDiv);

    // Fetch bot response
    var response = await fetch(API_CHAT_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'access_token': '123qwe'
        },
        body: JSON.stringify({message: input, conversation_id: conversation_id})
    });
    
    var reader = response.body.getReader();
    var decoder = new TextDecoder('utf-8');

    // Create bot message div
    let botDiv = document.createElement("div");
    let botImg = document.createElement("img");
    let botText = document.createElement("span");
    botDiv.id = "bot";
    botImg.src = "../static/images/bot-mini.png";
    botImg.className = "bot-avatar";
    botDiv.className = "bot response";
    botText.id = "botspan";
    botText.innerText = "Typing...";
    botDiv.appendChild(botImg);
    botDiv.appendChild(botText);
    messagesContainer.appendChild(botDiv);

    let botResponse = ""; // Variable include bot  response

    reader.read().then(function processResult(result) {
        if (result.done) {
            botDiv.appendChild(botImg);
            messagesContainer.appendChild(botDiv);
            return;
        }

        let token = decoder.decode(result.value);

        // Add token into bot response
        botResponse += token;
        botText.innerText = botResponse;
        botDiv.appendChild(botText);
        messagesContainer.appendChild(botDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight - messagesContainer.clientHeight;

        return reader.read().then(processResult);
    });
}