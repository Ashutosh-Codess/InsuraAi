const ChatComponent = {
  messages: [],
  init(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    this.render();
    this.bindEvents();
  },
  render() {
    const user = Auth.getUser();
    const isAgent = user && ['agent', 'admin'].includes(user.role);
    const greeting = isAgent
      ? "Hello! I can list every customer claim with its claim number, policy number, amount, status, and fraud-review information."
      : "Hello! I can explain your policy coverage, policy number, claim amount, claim status, and next steps."
    this.container.innerHTML = `
      <div class="flex flex-col h-full bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        <div class="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
            <h3 class="font-bold text-slate-800 dark:text-slate-100">Claims Copilot AI</h3>
          </div>
          <span class="text-xs px-2.5 py-1 bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 rounded-full font-medium">v2.4 Active</span>
        </div>
        <div id="chat-messages" class="flex-1 p-4 overflow-y-auto space-y-4 min-h-[350px] max-h-[500px]">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">AI</div>
            <div class="bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 p-3 rounded-2xl rounded-tl-none max-w-[80%] text-sm">
              ${greeting}
            </div>
          </div>
        </div>
        <form id="chat-form" class="p-3 border-t border-slate-200 dark:border-slate-800 flex gap-2 bg-slate-50 dark:bg-slate-800/30">
          <input type="text" id="chat-input" placeholder="Type your message..." class="flex-1 px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <button type="submit" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl transition-colors shadow-md">
            Send
          </button>
        </form>
      </div>
    `;
  },
  bindEvents() {
    const form = document.getElementById('chat-form');
    if (!form) return;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;
      this.appendMessage('user', text);
      input.value = '';
      this.appendTyping();
      try {
        const response = await API.post('/copilot/contextual-chat', { message: text });
        this.removeTyping();
        this.appendMessage('assistant', response.reply || 'I could not generate a response.');
      } catch (err) {
        this.removeTyping();
        this.appendMessage('assistant', 'Sorry, I am having trouble responding right now.');
      }
    });
  },
  appendMessage(role, text) {
    const list = document.getElementById('chat-messages');
    if (!list) return;
    const isUser = role === 'user';
    const msgEl = document.createElement('div');
    msgEl.className = `flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`;
    const safeText = String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    msgEl.innerHTML = `
      <div class="w-8 h-8 rounded-lg ${isUser ? 'bg-slate-800 text-white' : 'bg-indigo-600 text-white'} flex items-center justify-center font-bold text-sm">
        ${isUser ? 'U' : 'AI'}
      </div>
      <div class="${isUser ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none'} p-3 rounded-2xl max-w-[80%] text-sm whitespace-pre-wrap">
        ${safeText}
      </div>
    `;
    list.appendChild(msgEl);
    list.scrollTop = list.scrollHeight;
  },
  appendTyping() {
    const list = document.getElementById('chat-messages');
    if (!list) return;
    const typing = document.createElement('div');
    typing.id = 'chat-typing';
    typing.className = 'flex items-start gap-3';
    typing.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-sm">AI</div>
      <div class="bg-slate-100 dark:bg-slate-800 p-3 rounded-2xl rounded-tl-none text-sm text-slate-500 animate-pulse">
        Thinking...
      </div>
    `;
    list.appendChild(typing);
    list.scrollTop = list.scrollHeight;
  },
  removeTyping() {
    const typing = document.getElementById('chat-typing');
    if (typing) typing.remove();
  }
};
window.ChatComponent = ChatComponent;
