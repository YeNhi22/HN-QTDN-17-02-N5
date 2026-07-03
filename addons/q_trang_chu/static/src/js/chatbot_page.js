/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";

// ─── ChatbotPage: Trang chatbot full-screen ───────────────────────
class ChatbotPage extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.user = useService("user");

        this.state = useState({
            isTyping: false,
            messages: [],
            currentConversationId: null,
            inputValue: "",
            conversations: [],
            showSidebar: true,
        });

        this.welcomeOptions = [
            { icon: "📦", label: "Mượn tài sản",  query: "Làm sao để mượn tài sản?" },
            { icon: "📅", label: "Kiểm tra lịch", query: "Tôi có thể mượn tài sản ngày mai không?" },
            { icon: "🔧", label: "Bảo hành",       query: "Tài sản của tôi còn bảo hành không?" },
            { icon: "📋", label: "Quy trình",      query: "Quy trình thanh lý tài sản như thế nào?" },
        ];

        onMounted(() => {
            this._loadConversations();
            this._addWelcomeMessage();
        });
    }

    _addWelcomeMessage() {
        var userName = (this.user && this.user.name) || "bạn";
        this.state.messages.push({
            id: "welcome_" + Date.now(),
            content: "Xin chào <strong>" + userName + "</strong>! 👋<br><br>Tôi là <strong>ARIA</strong> — AI Assistant của hệ thống.<br><br>Bạn cần hỗ trợ gì?",
            isUser: false,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            showOptions: true,
        });
    }

    async _loadConversations() {
        try {
            var convs = await this.orm.searchRead(
                "chatbot.conversation",
                [["user_id", "=", this.user.userId]],
                ["id", "name", "write_date"],
                { limit: 20, order: "write_date desc" }
            );
            this.state.conversations = convs;
        } catch (e) {
            console.warn("Could not load conversations:", e);
        }
    }

    async startNewConversation() {
        this.state.currentConversationId = null;
        this.state.messages = [];
        this._addWelcomeMessage();
    }

    async loadConversation(conv) {
        try {
            this.state.currentConversationId = conv.id;
            this.state.messages = [];
            var msgs = await this.orm.searchRead(
                "chatbot.message",
                [["conversation_id", "=", conv.id]],
                ["id", "content", "is_user", "timestamp"],
                { order: "create_date asc" }
            );
            for (var m of msgs) {
                this.state.messages.push({
                    id: m.id,
                    content: m.is_user ? this._escape(m.content) : this._format(m.content),
                    isUser: m.is_user,
                    timestamp: m.timestamp ? new Date(m.timestamp).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }) : "",
                });
            }
            this._scrollDown();
        } catch (e) {
            console.warn("Could not load conversation:", e);
        }
    }

    async sendMessage(override) {
        var message = override || this.state.inputValue.trim();
        if (!message || this.state.isTyping) return;

        this.state.inputValue = "";
        this.state.messages.push({
            id: "u_" + Date.now(),
            content: this._escape(message),
            isUser: true,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
        });
        this._scrollDown();
        this.state.isTyping = true;

        try {
            var res = await this.orm.call("chatbot.assistant", "process_message", [message, this.state.currentConversationId]);
            this.state.currentConversationId = res.conversation_id;
            this.state.messages.push({
                id: "b_" + Date.now(),
                content: this._format(res.answer),
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
                suggestions: res.suggestions || [],
                actions: res.actions || [],
            });
            await this._loadConversations();
        } catch (e) {
            console.error("Chatbot error:", e);
            this.state.messages.push({
                id: "e_" + Date.now(),
                content: "⚠️ Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            });
        }
        this.state.isTyping = false;
        this._scrollDown();
    }

    sendQuickOption(opt) { this.sendMessage(opt.query); }
    sendSuggestion(sug)  { this.sendMessage(sug); }

    handleInput(ev)     { this.state.inputValue = ev.target.value; }
    handleKeyPress(ev)  { if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); this.sendMessage(); } }
    handleAction(act)   { if (act && act.action) { this.action.doAction(act.action); } }
    toggleSidebar()     { this.state.showSidebar = !this.state.showSidebar; }

    _scrollDown() {
        setTimeout(function() {
            var el = document.querySelector(".o_chat_messages");
            if (el) el.scrollTop = el.scrollHeight;
        }, 60);
    }

    _escape(t) {
        return String(t || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    _format(t) {
        return String(t || "")
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");
    }

    formatDate(d) {
        if (!d) return "";
        return new Date(d).toLocaleDateString("vi-VN");
    }
}

ChatbotPage.template = "q_trang_chu.ChatbotPage";

// ─── ĐĂNG KÝ VÀO REGISTRY ────────────────────────────────────────
registry.category("actions").add("q_trang_chu.chatbot_page", ChatbotPage);
