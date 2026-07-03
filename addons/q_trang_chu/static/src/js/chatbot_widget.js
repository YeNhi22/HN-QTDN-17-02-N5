/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";

export class ChatbotWidget extends Component {
    static template = "q_trang_chu.ChatbotWidget";

    setup() {
        this.orm = useService("orm");
        this.user = useService("user");

        this.state = useState({
            isOpen: false,
            messages: [],
            inputValue: "",
            isTyping: false,
            conversationId: null,
            suggestions: [
                "Làm sao để mượn máy chiếu?",
                "Kiểm tra tài sản còn trống",
                "Thống kê tổng quan",
            ],
        });

        this.messagesEl = null; // sẽ set sau khi mounted

        onMounted(() => {
            this.messagesEl = document.querySelector(".o_chatbot_messages");
            this.addWelcomeMessage();
        });
    }

    addWelcomeMessage() {
        const userName = this.user.name || "bạn";
        this.state.messages.push({
            id: Date.now(),
            content: `👋 **Xin chào ${userName}!**\n\nTôi là **AI Assistant** - trợ lý thông minh của hệ thống Quản lý Tài sản.\n\nTôi có thể giúp bạn:\n• 📦 Hướng dẫn mượn/trả tài sản\n• 📅 Kiểm tra lịch trình tài sản\n• 🔧 Tra cứu thông tin bảo hành\n• 📋 Giải thích quy trình, quy định\n• 📊 Cung cấp thống kê nhanh\n\n❓ Bạn cần hỗ trợ gì hôm nay?`,
            isUser: false,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
        });
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
    }

    closeChat() {
        this.state.isOpen = false;
    }

    async sendMessage() {
        const message = this.state.inputValue.trim();
        if (!message) return;

        // Add user message
        this.state.messages.push({
            id: Date.now(),
            content: message,
            isUser: true,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
        });

        this.state.inputValue = "";
        this.state.isTyping = true;
        this.scrollToBottom();

        try {
            // Call backend API
            const response = await this.orm.call(
                "chatbot.assistant",
                "process_message",
                [message, this.state.conversationId]
            );

            this.state.conversationId = response.conversation_id;

            // Add bot response
            this.state.messages.push({
                id: Date.now() + 1,
                content: this.formatMarkdown(response.answer),
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
                suggestions: response.suggestions || [],
                actions: response.actions || [],
            });

            if (response.suggestions && response.suggestions.length > 0) {
                this.state.suggestions = response.suggestions;
            }

        } catch (error) {
            console.error("Chatbot error:", error);
            this.state.messages.push({
                id: Date.now() + 1,
                content: "❌ Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            });
        }

        this.state.isTyping = false;
        this.scrollToBottom();
    }

    handleKeyPress(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    handleInput(event) {
        this.state.inputValue = event.target.value;
    }

    sendQuickReply(text) {
        this.state.inputValue = text;
        this.sendMessage();
    }

    handleAction(action) {
        if (action.type === "link" && action.action) {
            // Navigate to Odoo action
            this.env.services.action.doAction(action.action);
            this.closeChat();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            const el = document.querySelector(".o_chatbot_messages");
            if (el) el.scrollTop = el.scrollHeight;
        }, 100);
    }

    formatMarkdown(text) {
        if (!text) return "";

        // Convert markdown to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/^\• /gm, "• ")
            .replace(/\n/g, "<br>");
    }
}

ChatbotWidget.template = "q_trang_chu.ChatbotWidget";

// Register as a systray item to show on all pages
export class ChatbotSystray extends Component {
    static template = "q_trang_chu.ChatbotSystray";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            isOpen: false,
            messages: [],
            inputValue: "",
            isTyping: false,
            conversationId: null,
            suggestions: [
                "Làm sao để mượn máy chiếu?",
                "Kiểm tra tài sản còn trống",
                "Thống kê tổng quan",
            ],
        });
        // Không dùng useRef — dùng querySelector thay thế
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen && this.state.messages.length === 0) {
            this.addWelcomeMessage();
        }
    }

    addWelcomeMessage() {
        this.state.messages.push({
            id: Date.now(),
            content: `👋 <strong>Xin chào!</strong><br><br>Tôi là <strong>ARIA</strong> - AI Assistant của hệ thống Quản lý Tài sản.<br><br>Bạn cần hỗ trợ gì?`,
            isUser: false,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
        });
    }

    closeChat() {
        this.state.isOpen = false;
    }

    async sendMessage() {
        const message = this.state.inputValue.trim();
        if (!message) return;

        this.state.messages.push({
            id: Date.now(),
            content: message,
            isUser: true,
            timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
        });

        this.state.inputValue = "";
        this.state.isTyping = true;
        this.scrollToBottom();

        try {
            const response = await this.orm.call(
                "chatbot.assistant",
                "process_message",
                [message, this.state.conversationId]
            );
            this.state.conversationId = response.conversation_id;
            this.state.messages.push({
                id: Date.now() + 1,
                content: this.formatMarkdown(response.answer),
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
                suggestions: response.suggestions || [],
            });
            if (response.suggestions && response.suggestions.length > 0) {
                this.state.suggestions = response.suggestions;
            }
        } catch (error) {
            console.error("Chatbot error:", error);
            this.state.messages.push({
                id: Date.now() + 1,
                content: "❌ Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
                isUser: false,
                timestamp: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" }),
            });
        }
        this.state.isTyping = false;
        this.scrollToBottom();
    }

    handleKeyPress(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendMessage();
        }
    }

    handleInput(event) {
        this.state.inputValue = event.target.value;
    }

    sendQuickReply(text) {
        this.state.inputValue = text;
        this.sendMessage();
    }

    scrollToBottom() {
        setTimeout(() => {
            const el = document.querySelector(".o_chatbot_systray_container .o_chatbot_messages");
            if (el) el.scrollTop = el.scrollHeight;
        }, 100);
    }

    formatMarkdown(text) {
        if (!text) return "";
        return text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/\n/g, "<br>");
    }
}

// Register chatbot in systray (floating button)
registry.category("main_components").add("ChatbotWidget", {
    Component: ChatbotSystray,
});
