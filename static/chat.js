// 从URL中提取 dir 参数

document.getElementById('sendMessage').addEventListener('click', sendMessage);
document.getElementById('messageInput').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

let isProcessing = false;
let chatHistory = []; // 聊天记录数组
const maxMessages = localStorage.getItem('messageCount') || 10; 
const systemPrompt = localStorage.getItem('promptWord') || ''; 
const temperature = localStorage.getItem('temperature') || 0.7;
async function sendMessage() {
    if (isProcessing) return;
    isProcessing = true;

    const messageInput = document.getElementById('messageInput');
    const userMessage = messageInput.value.trim();
    const pathSegments = window.location.pathname.split("/");
    const id = pathSegments[pathSegments.length - 1]; // 假设 dir 在路径的最后一部分

    // 先获取知识库信息
    const contextData = await getContextFromApi(id, userMessage, 8);
    let finalMessage = userMessage;

    if (contextData) {
        // 将知识库信息转成字符串
        const contextString = contextData.join(", "); // 拼接数组为字符串

        // 创建最终消息
        finalMessage = `${userMessage}，可提供的参考<[${contextString}]>`;
    }

    if (userMessage) {
        // 存储用户消息到记录中，包括知识库信息
        chatHistory.push({ role: 'user', content: finalMessage });

        createUserMessageBubble(userMessage); // 创建用户消息气泡
        messageInput.value = ''; // 清空输入框
        scrollToBottom();

        // 限制聊天记录数量
        // if (chatHistory.length > maxMessages + 1) { // +1 为系统提示词
        //     chatHistory.splice(1, 1); // 删除最早的用户消息，保留系统提示词
        // }

        // 构造可发送的消息数组，包括系统提示词
        const messagesToSend = [{ role: 'system', content: localStorage.getItem('promptWord') || '' }, ...chatHistory];

        // 调用后端接口并处理流式响应
        const response = await fetch('/api/chat/completion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'deepseek-chat',
                messages: messagesToSend,
                stream: true
            })
        });

        await processAssistantResponse(response);
        isProcessing = false; // 恢复发送功能
    }
}

function createUserMessageBubble(message) {
    const userMessageContainer = document.createElement('div');
    userMessageContainer.className = 'flex items-start justify-end';

    const userMessageText = document.createElement('div');
    userMessageText.className = 'bg-blue-100 p-3 rounded-lg shadow-sm';
    userMessageText.style.margin = '4px';
    userMessageText.textContent = message;

    const userAvatar = document.createElement('img');
    userAvatar.src = 'https://via.placeholder.com/40';
    userAvatar.alt = 'User Avatar';
    userAvatar.className = 'w-8 h-8 rounded-full ml-2';

    userMessageContainer.appendChild(userMessageText);
    userMessageContainer.appendChild(userAvatar);

    const chatContainer = document.getElementById('chat-box');
    chatContainer.appendChild(userMessageContainer);
    chatContainer.appendChild(document.createElement('br'));
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chat-box');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function getContextFromApi(id, query, num) {
    // 从后端获取上下文信息
    try {
        const response = await fetch('/api/knowledge/search/' + id + '?text=' + query + '&num=' + num);
        const data = await response.json();
        return data.data; // 返回 data.data 的内容
    } catch (error) {
        console.error('Error fetching context:', error);
        return null; // 发生错误时返回 null
    }
}

function getVisibleChatHistory() {
    // 取出当前屏幕上可见的消息
    const chatContainer = document.getElementById('chat-box');
    const messages = Array.from(chatContainer.children);

    return messages.map(msg => {
        const userBubble = msg.querySelector('.bg-blue-100');
        const assistantBubble = msg.querySelector('.bg-white');

        if (userBubble) {
            return { role: 'user', content: userBubble.textContent };
        } else if (assistantBubble) {
            return { role: 'assistant', content: assistantBubble.innerHTML };
        }
    }).filter(Boolean); // 过滤掉空值
}

async function processAssistantResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let accumulatedContent = '';
    const assistantMessageContainer = document.createElement('div');
    assistantMessageContainer.className = 'flex items-start';

    const assistantAvatar = document.createElement('img');
    assistantAvatar.src = 'https://via.placeholder.com/40';
    assistantAvatar.alt = 'Assistant Avatar';
    assistantAvatar.className = 'w-8 h-8 rounded-full mr-2';

    const assistantMessageText = document.createElement('div');
    assistantMessageText.className = 'bg-white p-3 rounded-lg shadow-sm';
    assistantMessageText.style.margin = '4px';

    assistantMessageContainer.appendChild(assistantAvatar);
    assistantMessageContainer.appendChild(assistantMessageText);
    const chatContainer = document.getElementById('chat-box');
    chatContainer.appendChild(assistantMessageContainer);
    chatContainer.appendChild(document.createElement('br'));

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop();

        for (let line of lines) {
            if (line.startsWith('data: ')) {
                let data = line.slice(6);
                if (data === '[DONE]') break;
                try {
                    let json = JSON.parse(data);
                    let content = json.choices[0].delta.content;
                    if (content) {
                        accumulatedContent += content;
                        assistantMessageText.innerHTML = marked.parse(accumulatedContent);
                        scrollToBottom();
                    }
                } catch (e) {
                    console.error('Error parsing JSON:', e);
                }
            }
        }
    }

    chatHistory.push({ role: 'assistant', content: accumulatedContent });
}
// Initialize modal and knowledge base display
const settingsButton = document.getElementById('settingsButton');
const settingsModal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const pathSegments = window.location.pathname.split("/");
const id = pathSegments[pathSegments.length - 1]; // 假设 dir 在路径的最后一部分
const currentKnowledge = id;

settingsButton.addEventListener('click', async () => {
    // Make sure currentKnowledge exists
    if (!currentKnowledge) {
        console.error('currentKnowledge element does not exist!');
        return;
    }

    try {
        // Fetch knowledge base info
        const response = await fetch('/api/knowledge/list');

        // Check response status
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Ensure data structure is correct
        if (data && data.data) {
            const knowledgeList = data.data.map(db => db.name).join(", ");
            currentKnowledge.textContent = `当前知识库: ${knowledgeList}`;
        } else {
            console.error('Data format is incorrect:', data);
        }

        settingsModal.classList.remove('hidden');
    } catch (error) {
        console.error('Failed to fetch knowledge base:', error);
    }
});

closeModal.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
});

document.getElementById('saveSettings').addEventListener('click', () => {
    const messageCount = document.getElementById('messageCount').value;
    const promptWord = document.getElementById('promptWord').value;
    const temperature = document.getElementById('temperature').value;

    // Save settings to local storage or handle them as needed
    localStorage.setItem('messageCount', messageCount);
    localStorage.setItem('promptWord', promptWord);
    localStorage.setItem('temperature', temperature);
    alert('设置已保存！');
    settingsModal.classList.add('hidden');
});

// function loadChatHistory(savedHistory) {
//     // 从本地存储加载聊天记录
//     if (savedHistory) {
//         chatHistory = JSON.parse(savedHistory);
//         chatHistory.forEach(msg => {
//             const messageContainer = document.createElement('div');
//             messageContainer.className = 'flex items-start';

//             const avatar = document.createElement('img');
//             avatar.src = msg.role === 'user'? 'URL_ADDRESS' : 'URL_ADDRESS'; // 根据消息角色设置头像
//             avatar.alt = msg.role === 'user'? 'User Avatar' : 'Assistant Avatar';
//             avatar.className = 'w-8 h-8 rounded-full mr-2';

//             const messageText = document.createElement('div');
//             messageText.className = 'bg-white p-3 rounded-lg shadow-sm';
//             messageText.style.margin = '4px';
//             messageText.innerHTML = msg.content;

//             messageContainer.appendChild(avatar);
//             messageContainer.appendChild(messageText);

//             const historyBox = document.getElementById('history-box');
//             historyBox.appendChild(messageContainer);
//         });
//     }
// }



// function saveChatHistory() {
//     // 保存聊天记录到本地存储
//     const visibleHistory = getVisibleChatHistory();
//     const allChatHistoryList = localStorage.getItem('allChatHistoryList') || [];
// }