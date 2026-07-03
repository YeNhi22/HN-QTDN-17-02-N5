/**
 * ARIA Chatbot - Floating Bubble
 * Nút tròn góc màn hình, click mở cửa sổ chat với AI
 * Không dùng OWL/registry - dùng DOM thuần để tránh lỗi
 */
(function() {
    'use strict';

    // Chờ Odoo load xong
    function initChatbot() {
        if (document.getElementById('aria-chatbot-bubble')) return;

        // === TẠO HTML CHATBOT ===
        var html = `
        <div id="aria-chatbot-bubble">
            <!-- Nút tròn nổi -->
            <button id="aria-toggle-btn" onclick="ariaChatbot.toggle()" title="Chat với Trợ lý Moi Moi">
                <span id="aria-btn-icon">💬</span>
            </button>

            <!-- Cửa sổ chat -->
            <div id="aria-chat-window" style="display:none;">
                <!-- Header -->
                <div id="aria-chat-header">
                    <div id="aria-header-info">
                        <div id="aria-avatar">🤖</div>
                        <div>
                            <div id="aria-name">Trợ lý Moi Moi</div>
                            <div id="aria-status">● Trực tuyến</div>
                        </div>
                    </div>
                    <button onclick="ariaChatbot.toggle()" id="aria-close-btn">✕</button>
                </div>

                <!-- Messages -->
                <div id="aria-messages"></div>

                <!-- Input -->
                <div id="aria-input-area">
                    <input id="aria-input" type="text"
                           placeholder="Nhắn tin với Moi Moi..."
                           onkeypress="if(event.key==='Enter') ariaChatbot.send()" />
                    <button onclick="ariaChatbot.send()" id="aria-send-btn">➤</button>
                </div>
            </div>
        </div>`;

        var div = document.createElement('div');
        div.innerHTML = html;
        document.body.appendChild(div.firstElementChild);

        // Thêm CSS
        var style = document.createElement('style');
        style.textContent = `
        #aria-chatbot-bubble {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        #aria-toggle-btn {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            cursor: pointer;
            font-size: 24px;
            box-shadow: 0 4px 20px rgba(102,126,234,0.5);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #aria-toggle-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 28px rgba(102,126,234,0.7);
        }
        #aria-chat-window {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 360px;
            height: 520px;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 12px 48px rgba(0,0,0,0.18);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: ariaSlideUp 0.25s ease;
        }
        @keyframes ariaSlideUp {
            from { opacity:0; transform:translateY(16px) scale(0.97); }
            to   { opacity:1; transform:translateY(0) scale(1); }
        }
        #aria-chat-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 14px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #fff;
        }
        #aria-header-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #aria-avatar {
            font-size: 26px;
            background: rgba(255,255,255,0.2);
            width: 40px; height: 40px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
        }
        #aria-name { font-weight: 700; font-size: 15px; }
        #aria-status { font-size: 11px; opacity: 0.85; }
        #aria-close-btn {
            background: rgba(255,255,255,0.2);
            border: none; color: #fff;
            width: 28px; height: 28px;
            border-radius: 50%; cursor: pointer;
            font-size: 13px; font-weight: bold;
            display: flex; align-items: center; justify-content: center;
        }
        #aria-messages {
            flex: 1;
            overflow-y: auto;
            padding: 14px;
            background: #f7f8fc;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .aria-msg {
            max-width: 82%;
            padding: 10px 14px;
            border-radius: 16px;
            font-size: 13.5px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .aria-msg.user {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .aria-msg.bot {
            background: #fff;
            color: #2d3748;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.08);
        }
        .aria-msg.typing {
            background: #fff;
            color: #888;
            align-self: flex-start;
            padding: 12px 16px;
        }
        .aria-typing-dots span {
            display: inline-block;
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #667eea;
            margin: 0 2px;
            animation: ariaBounce 1.2s infinite;
        }
        .aria-typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .aria-typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes ariaBounce {
            0%, 80%, 100% { transform: translateY(0); }
            40%           { transform: translateY(-6px); }
        }
        #aria-input-area {
            padding: 12px;
            background: #fff;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
            align-items: center;
        }
        #aria-input {
            flex: 1;
            border: 1.5px solid #e2e8f0;
            border-radius: 24px;
            padding: 9px 14px;
            font-size: 13.5px;
            outline: none;
            transition: border-color 0.2s;
        }
        #aria-input:focus { border-color: #667eea; }
        #aria-send-btn {
            width: 38px; height: 38px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none; border-radius: 50%;
            color: #fff; font-size: 15px;
            cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: transform 0.15s;
        }
        #aria-send-btn:hover { transform: scale(1.1); }
        `;
        document.head.appendChild(style);

        // Hiện tin chào
        ariaChatbot.addBotMsg("👋 Xin chào! Tôi là <strong>Trợ lý Moi Moi</strong> 🤖<br><br>Tôi có thể giúp bạn về mọi thứ — từ nghiệp vụ hệ thống đến các câu hỏi đời thường!<br><br>• 📦 Tài sản, mượn trả, kiểm kê<br>• 💰 Tài chính, phê duyệt mua<br>• 👥 Nhân sự, phòng ban<br>• 💬 Hỏi bất cứ điều gì khác<br><br>Moi Moi đây, bạn cần gì nào? 😊");
    }

    // === CHATBOT LOGIC ===
    window.ariaChatbot = {
        isOpen: false,

        toggle: function() {
            this.isOpen = !this.isOpen;
            var win = document.getElementById('aria-chat-window');
            var icon = document.getElementById('aria-btn-icon');
            if (this.isOpen) {
                win.style.display = 'flex';
                icon.textContent = '✕';
                document.getElementById('aria-input').focus();
                this.scrollDown();
            } else {
                win.style.display = 'none';
                icon.textContent = '💬';
            }
        },

        send: function() {
            var input = document.getElementById('aria-input');
            var msg = input.value.trim();
            if (!msg) return;
            input.value = '';

            // Hiện tin nhắn user
            this.addUserMsg(msg);
            this.showTyping();

            // Gọi backend
            var self = this;
            fetch('/web/dataset/call_kw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0', method: 'call', id: 1,
                    params: {
                        model: 'chatbot.assistant',
                        method: 'process_message',
                        args: [msg, null],
                        kwargs: {}
                    }
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                self.hideTyping();
                if (data.result && data.result.answer) {
                    self.addBotMsg(data.result.answer);
                    // Hiện suggestions nếu có
                    if (data.result.suggestions && data.result.suggestions.length) {
                        self.addSuggestions(data.result.suggestions);
                    }
                } else {
                    self.addBotMsg("⚠️ Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.");
                }
            })
            .catch(function() {
                self.hideTyping();
                self.addBotMsg("⚠️ Không thể kết nối. Vui lòng thử lại sau.");
            });
        },

        addUserMsg: function(text) {
            var div = document.createElement('div');
            div.className = 'aria-msg user';
            div.textContent = text;
            document.getElementById('aria-messages').appendChild(div);
            this.scrollDown();
        },

        addBotMsg: function(html) {
            var div = document.createElement('div');
            div.className = 'aria-msg bot';
            div.innerHTML = this._format(html);
            document.getElementById('aria-messages').appendChild(div);
            this.scrollDown();
        },

        addSuggestions: function(suggestions) {
            var wrap = document.createElement('div');
            wrap.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-top:4px;';
            var self = this;
            suggestions.slice(0, 3).forEach(function(sug) {
                var btn = document.createElement('button');
                btn.textContent = sug;
                btn.style.cssText = 'background:#f0f4ff;border:1px solid #667eea;color:#667eea;border-radius:16px;padding:5px 11px;font-size:12px;cursor:pointer;';
                btn.onclick = function() {
                    document.getElementById('aria-input').value = sug;
                    self.send();
                };
                wrap.appendChild(btn);
            });
            document.getElementById('aria-messages').appendChild(wrap);
            this.scrollDown();
        },

        showTyping: function() {
            var div = document.createElement('div');
            div.className = 'aria-msg typing';
            div.id = 'aria-typing';
            div.innerHTML = '<div class="aria-typing-dots"><span></span><span></span><span></span></div>';
            document.getElementById('aria-messages').appendChild(div);
            this.scrollDown();
        },

        hideTyping: function() {
            var el = document.getElementById('aria-typing');
            if (el) el.remove();
        },

        scrollDown: function() {
            setTimeout(function() {
                var el = document.getElementById('aria-messages');
                if (el) el.scrollTop = el.scrollHeight;
            }, 50);
        },

        _format: function(text) {
            return String(text || '')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
        }
    };

    // Khởi tạo khi DOM sẵn sàng
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatbot);
    } else {
        initChatbot();
    }

    // Chờ thêm 2s để Odoo load xong rồi init lại (phòng trường hợp SPA)
    setTimeout(initChatbot, 2000);

})();
