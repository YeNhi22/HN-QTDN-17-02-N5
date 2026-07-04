# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import os
import re
import requests
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

# Gemini API Configuration
# Key lấy từ biến môi trường hoặc Odoo Settings
# KHÔNG hardcode key vào đây – đặt trong .env hoặc qua giao diện Thiết lập
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Groq API Configuration (tùy chọn – fallback cho chatbot)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


class ChatbotConversation(models.Model):
    """Lưu trữ cuộc hội thoại với chatbot"""
    _name = 'chatbot.conversation'
    _description = 'Cuộc hội thoại Chatbot'
    _order = 'create_date desc'

    name = fields.Char('Tiêu đề', compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='Người dùng', default=lambda self: self.env.user)
    message_ids = fields.One2many('chatbot.message', 'conversation_id', string='Tin nhắn')
    active = fields.Boolean(default=True)
    
    @api.depends('message_ids')
    def _compute_name(self):
        for record in self:
            first_msg = record.message_ids.filtered(lambda m: m.is_user).sorted('create_date')[:1]
            if first_msg:
                record.name = first_msg.content[:50] + '...' if len(first_msg.content) > 50 else first_msg.content
            else:
                record.name = f'Cuộc hội thoại #{record.id}'


class ChatbotMessage(models.Model):
    """Tin nhắn trong cuộc hội thoại"""
    _name = 'chatbot.message'
    _description = 'Tin nhắn Chatbot'
    _order = 'create_date asc'

    conversation_id = fields.Many2one('chatbot.conversation', string='Cuộc hội thoại', ondelete='cascade')
    content = fields.Text('Nội dung', required=True)
    is_user = fields.Boolean('Từ người dùng', default=True)
    timestamp = fields.Datetime('Thời gian', default=fields.Datetime.now)
    
    # Metadata
    intent = fields.Char('Intent phát hiện')
    confidence = fields.Float('Độ tin cậy')
    sources = fields.Text('Nguồn tham khảo')


class ChatbotAssistant(models.Model):
    """AI Chatbot Assistant - Trợ lý thông minh sử dụng Gemini API"""
    _name = 'chatbot.assistant'
    _description = 'AI Chatbot Assistant'

    name = fields.Char('Tên', default='AI Assistant')
    active = fields.Boolean(default=True)
    
    # Cấu hình Gemini
    gemini_api_key = fields.Char('Gemini API Key', default=GEMINI_API_KEY)
    use_gemini = fields.Boolean('Sử dụng Gemini AI', default=True,
        help='Bật để sử dụng Gemini AI cho các câu trả lời thông minh hơn')
    temperature = fields.Float('Temperature', default=0.7)
    max_tokens = fields.Integer('Max Tokens', default=1000)

    def _get_system_prompt(self):
        """System prompt cho Moi Moi — trợ lý AI toàn năng"""
        today = fields.Date.today().strftime('%d/%m/%Y')
        try:
            total_ts = self.env['tai_san'].search_count([])
            don_cho_duyet = self.env['don_muon_tai_san'].search_count([('trang_thai', '=', 'cho_duyet')])
            dang_muon = self.env['muon_tra_tai_san'].search_count([('trang_thai', '=', 'dang_muon')])
            tong_nv = self.env['nhan_vien'].search_count([])
        except Exception:
            total_ts = don_cho_duyet = dang_muon = tong_nv = 0

        return f"""Bạn là Moi Moi — trợ lý AI thân thiện, thông minh và hữu ích.
Ngày hôm nay: {today}

TÍNH CÁCH:
- Thân thiện, vui vẻ, dễ gần như người bạn thật sự
- Trả lời mọi câu hỏi không giới hạn chủ đề
- Ngắn gọn, đúng trọng tâm, dùng emoji cho sinh động
- Nếu không biết thì thành thật nói và gợi ý cách tìm

HỆ THỐNG ERP (Odoo 15) đang quản lý:
- Tổng tài sản: {total_ts} | Đơn chờ duyệt: {don_cho_duyet} | Đang mượn: {dang_muon} | Nhân viên: {tong_nv}
- Module Nhân sự: nhân viên, phòng ban, chức vụ, lịch sử công tác
- Module Tài sản: quản lý, phân bổ, mượn trả, kiểm kê, thanh lý, đề xuất mua
- Module Tài chính: phê duyệt mua, khấu hao, bút toán, báo cáo

QUY TẮC:
- Câu hỏi về hệ thống → hướng dẫn chi tiết từng bước
- Câu hỏi khác (thời tiết, nấu ăn, code, toán...) → trả lời bình thường
- Trò chuyện vui → thoải mái, thân thiện
- LUÔN cố gắng giúp đỡ, không từ chối
"""

    def _call_gemini_api_with_key(self, api_key, message, context="", conversation=None):
        """Gọi Groq API với conversation history, fallback sang Gemini nếu lỗi"""
        import time

        system_prompt = self._get_system_prompt()

        # Build conversation history
        history_messages = []
        if conversation:
            # Lấy tối đa 20 tin nhắn gần nhất để tránh vượt token limit
            past_messages = self.env['chatbot.message'].search(
                [('conversation_id', '=', conversation.id)],
                order='create_date asc',
                limit=20
            )
            for msg in past_messages:
                role = 'user' if msg.is_user else 'assistant'
                history_messages.append({'role': role, 'content': msg.content or ''})

        # === THỬ GROQ TRƯỚC ===
        try:
            # Lấy Groq key từ Odoo Settings (ưu tiên) hoặc env
            icp = self.env['ir.config_parameter'].sudo()
            groq_key = (icp.get_param('q_trang_chu.gemini_api_key') or '').strip()
            if not groq_key:
                groq_key = os.environ.get('GROQ_API_KEY', '').strip()
            if groq_key:
                messages = [
                    {"role": "system", "content": system_prompt + f"\n\nThông tin hệ thống:\n{context}"},
                ] + history_messages + [
                    {"role": "user", "content": message}
                ]
                payload = {
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                }
                response = requests.post(
                    GROQ_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    _logger.warning(f"Groq error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            _logger.warning(f"Groq failed: {e}")

        # === FALLBACK: GEMINI ===
        try:
            if not api_key:
                return None
            url = f"{GEMINI_API_URL}?key={api_key}"
            full_prompt = f"{system_prompt}\n\nThông tin hệ thống:\n{context}\n\nCâu hỏi: {message}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
            }
            for attempt in range(2):
                response = requests.post(
                    url, json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get('candidates'):
                        return result['candidates'][0]['content']['parts'][0]['text']
                    return None
                elif response.status_code == 429:
                    time.sleep(2)
                    continue
                else:
                    _logger.warning(f"Gemini error {response.status_code}")
                    return None
        except Exception as e:
            _logger.error(f"Gemini failed: {e}")

        return None

    def _call_gemini_api(self, message, context=""):
        """Gọi Gemini API để sinh câu trả lời"""
        try:
            # Ưu tiên: field trong record → System Parameters → biến môi trường
            api_key = self.gemini_api_key
            if not api_key:
                api_key = self.env['ir.config_parameter'].sudo().get_param(
                    'mail_bot_gemini.api_key', default=''
                )
            if not api_key:
                api_key = GEMINI_API_KEY
            if not api_key:
                _logger.warning("Gemini API key chưa được cấu hình.")
                return None
            url = f"{GEMINI_API_URL}?key={api_key}"
            
            # Tạo prompt với context
            full_prompt = f"""{self._get_system_prompt()}

Thông tin bổ sung từ hệ thống:
{context}

Câu hỏi của người dùng: {message}

Hãy trả lời câu hỏi trên một cách hữu ích và thân thiện."""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.temperature or 0.7,
                    "maxOutputTokens": self.max_tokens or 1000,
                }
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            _logger.warning(f"Gemini API error: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            _logger.error(f"Error calling Gemini API: {str(e)}")
            return None

    # ============ MAIN CHAT METHOD ============
    @api.model
    def process_message(self, message, conversation_id=None):
        """Xử lý tin nhắn từ người dùng và trả lời"""
        # Tạo hoặc lấy conversation
        if conversation_id:
            conversation = self.env['chatbot.conversation'].browse(conversation_id)
            if not conversation or conversation.user_id != self.env.user:
                conversation = self.env['chatbot.conversation'].create({
                    'user_id': self.env.user.id,
                })
        else:
            conversation = self.env['chatbot.conversation'].create({
                'user_id': self.env.user.id,
            })

        # Lưu tin nhắn người dùng
        self.env['chatbot.message'].create({
            'conversation_id': conversation.id,
            'content': message,
            'is_user': True,
        })

        # Phát hiện intent và xử lý
        intent = self._detect_intent(message)
        
        # Lấy context từ hệ thống
        context = self._get_system_context(message, intent)
        
        # Lấy hoặc tạo cấu hình chatbot
        assistant = self.search([], limit=1)
        if not assistant:
            assistant = self.create({
                'name': 'Moi Moi Assistant',
                'active': True,
                'use_gemini': True,
            })

        # Lấy Groq API key từ Odoo Settings (Thiết lập → Tích hợp AI)
        icp = self.env['ir.config_parameter'].sudo()
        api_key = (icp.get_param('q_trang_chu.gemini_api_key') or '').strip()
        if not api_key:
            # Fallback về biến môi trường
            api_key = os.environ.get('GROQ_API_KEY', '').strip()

        use_gemini = bool(api_key)

        # Thử gọi Gemini API
        gemini_response = None
        if use_gemini and assistant:
            gemini_response = assistant._call_gemini_api_with_key(
                api_key, message, context, conversation
            )
        
        if gemini_response:
            response = {
                'answer': gemini_response,
                'suggestions': self._get_suggestions(intent),
                'actions': self._get_actions(intent),
            }
        else:
            # Fallback về rule-based response
            response = self._generate_response(message, intent, conversation)

        # Lưu tin nhắn bot
        self.env['chatbot.message'].create({
            'conversation_id': conversation.id,
            'content': response['answer'],
            'is_user': False,
            'intent': intent,
            'sources': json.dumps(response.get('sources', [])),
        })

        return {
            'conversation_id': conversation.id,
            'answer': response['answer'],
            'intent': intent,
            'suggestions': response.get('suggestions', []),
            'actions': response.get('actions', []),
        }

    def _get_system_context(self, message, intent):
        """Lấy thông tin context từ hệ thống Odoo - RAG enhanced"""
        context_parts = []
        
        try:
            # Thông tin người dùng
            user = self.env.user
            context_parts.append(f"👤 Người dùng hiện tại: {user.name}")
            
            # Tìm nhân viên tương ứng
            nhan_vien = self.env['nhan_vien'].search([('user_id', '=', user.id)], limit=1)
            if nhan_vien:
                phong_ban = nhan_vien.phong_ban_hien_tai_id.ten_phong_ban if nhan_vien.phong_ban_hien_tai_id else 'Chưa phân công'
                context_parts.append(f"🏢 Nhân viên: {nhan_vien.ho_ten}, Phòng ban: {phong_ban}")
            
            # Thống kê tài sản
            TaiSan = self.env['tai_san']
            total_assets = TaiSan.search_count([])
            active_assets = TaiSan.search_count([('trang_thai_thanh_ly', 'in', ['da_phan_bo', 'chua_phan_bo'])])
            context_parts.append(f"📊 Tổng số tài sản: {total_assets}, đang sử dụng: {active_assets}")
            
            # Tài sản có thể mượn (liệt kê tên cụ thể)
            PhanBo = self.env['phan_bo_tai_san']
            available_assets = PhanBo.search([
                ('tinh_trang', '=', 'binh_thuong'),
                ('trang_thai', '=', 'in-use'),
            ], limit=10)
            if available_assets:
                asset_names = [f"{a.tai_san_id.ten_tai_san} ({a.phong_ban_id.ten_phong_ban if a.phong_ban_id else 'N/A'})" for a in available_assets[:5]]
                context_parts.append(f"📦 Tài sản sẵn sàng cho mượn ({len(available_assets)} tài sản):")
                for name in asset_names:
                    context_parts.append(f"  • {name}")
            
            # Thống kê đơn mượn
            DonMuon = self.env['don_muon_tai_san']
            don_cho_duyet = DonMuon.search_count([('trang_thai', '=', 'cho_duyet')])
            don_dang_muon = DonMuon.search_count([('trang_thai', '=', 'dang_muon')])
            context_parts.append(f"📝 Đơn mượn: {don_cho_duyet} chờ duyệt, {don_dang_muon} đang mượn")
            
            # Thông tin tài sản được phân bổ cho nhân viên
            if nhan_vien and intent in ['bao_hanh', 'general']:
                ts_phan_bo = PhanBo.search([('nhan_vien_su_dung_id', '=', nhan_vien.id)])
                if ts_phan_bo:
                    context_parts.append(f"🔧 Tài sản được phân bổ cho {nhan_vien.ho_ten}:")
                    for pb in ts_phan_bo[:5]:
                        asset = pb.tai_san_id
                        context_parts.append(f"  • {asset.ten_tai_san}")
            
            # Đơn mượn của nhân viên hiện tại
            if nhan_vien:
                don_muon_cua_toi = DonMuon.search([
                    ('nhan_vien_muon_id', '=', nhan_vien.id),
                    ('trang_thai', 'in', ['cho_duyet', 'da_duyet', 'dang_muon'])
                ], limit=5)
                if don_muon_cua_toi:
                    context_parts.append(f"📋 Đơn mượn của bạn:")
                    for dm in don_muon_cua_toi:
                        status_emoji = {
                            'cho_duyet': '⏳',
                            'da_duyet': '✔️',
                            'dang_muon': '📦'
                        }.get(dm.trang_thai, '📝')
                        context_parts.append(f"  • {status_emoji} {dm.ma_don_muon}: {dm.ten_don_muon}")
                        
        except Exception as e:
            _logger.warning(f"Error getting context: {str(e)}")
        
        return "\n".join(context_parts)

    def _get_suggestions(self, intent):
        """Lấy gợi ý dựa trên intent"""
        suggestions_map = {
            'muon_tai_san': [
                'Xem tài sản có thể mượn',
                'Quy định mượn tài sản',
                'Đơn mượn của tôi',
            ],
            'tra_tai_san': [
                'Hướng dẫn trả tài sản',
                'Xem đơn mượn đang có',
            ],
            'bao_hanh': [
                'Làm sao khi tài sản hỏng?',
                'Liên hệ hỗ trợ kỹ thuật',
            ],
            'thanh_ly': [
                'Điều kiện thanh lý',
                'Quy trình thanh lý chi tiết',
            ],
            'thong_ke': [
                'Báo cáo chi tiết',
                'Xem Dashboard',
            ],
        }
        return suggestions_map.get(intent, [
            'Làm sao để mượn tài sản?',
            'Kiểm tra tài sản còn trống',
            'Thống kê tổng quan',
        ])

    def _get_actions(self, intent):
        """Lấy action buttons dựa trên intent"""
        actions_map = {
            'muon_tai_san': [{
                'type': 'link',
                'label': '📝 Tạo đơn mượn',
                'action': 'quan_ly_tai_san.don_muon_tai_san_action',
            }],
            'thong_ke': [{
                'type': 'link',
                'label': '📈 Xem Dashboard',
                'action': 'q_trang_chu.action_dashboard_main',
            }],
        }
        return actions_map.get(intent, [])

    def _detect_intent(self, message):
        """Phát hiện ý định của người dùng"""
        message_lower = message.lower()
        
        # Pattern matching cho các intent phổ biến
        patterns = {
            'muon_tai_san': [
                r'mượn', r'cho mượn', r'đăng ký mượn', r'muốn mượn',
                r'máy chiếu', r'laptop', r'xe', r'thiết bị'
            ],
            'tra_tai_san': [
                r'trả', r'hoàn trả', r'trả lại'
            ],
            'kiem_tra_lich': [
                r'còn trống', r'available', r'lịch', r'có thể mượn',
                r'ngày \d+', r'hôm nay', r'ngày mai'
            ],
            'bao_hanh': [
                r'bảo hành', r'warranty', r'còn bảo hành', r'hết bảo hành'
            ],
            'thanh_ly': [
                r'thanh lý', r'quy trình thanh lý', r'xử lý tài sản cũ'
            ],
            'huong_dan': [
                r'làm sao', r'cách', r'hướng dẫn', r'how to', r'như thế nào'
            ],
            'thong_ke': [
                r'thống kê', r'báo cáo', r'tổng quan', r'bao nhiêu'
            ],
            'quy_trinh': [
                r'quy trình', r'quy định', r'policy', r'quy chế'
            ],
        }

        for intent, keywords in patterns.items():
            for keyword in keywords:
                if re.search(keyword, message_lower):
                    return intent
        
        return 'general'

    def _generate_response(self, message, intent, conversation):
        """Sinh câu trả lời dựa trên intent (fallback khi không có Gemini)"""
        
        # Xử lý theo từng intent
        if intent == 'muon_tai_san':
            return self._handle_muon_tai_san(message)
        elif intent == 'kiem_tra_lich':
            return self._handle_kiem_tra_lich(message)
        elif intent == 'bao_hanh':
            return self._handle_bao_hanh(message)
        elif intent == 'thanh_ly':
            return self._handle_thanh_ly(message)
        elif intent == 'huong_dan':
            return self._handle_huong_dan(message)
        elif intent == 'thong_ke':
            return self._handle_thong_ke(message)
        elif intent == 'quy_trinh':
            return self._handle_quy_trinh(message)
        else:
            return self._handle_general(message)

    def _handle_muon_tai_san(self, message):
        """Xử lý yêu cầu mượn tài sản"""
        response = """🎯 **Hướng dẫn mượn tài sản:**

**Bước 1:** Truy cập menu **Quản lý Tài sản** → **Đơn mượn tài sản**

**Bước 2:** Nhấn nút **Tạo** để tạo đơn mượn mới

**Bước 3:** Điền thông tin:
- Chọn phòng ban cho mượn
- Chọn nhân viên mượn
- Thời gian mượn và trả dự kiến
- Lý do mượn

**Bước 4:** Thêm tài sản vào danh sách mượn

**Bước 5:** Nhấn **Lưu** rồi **Gửi duyệt**

💡 *Sau khi được duyệt, bạn sẽ nhận được thông báo và có thể đến nhận tài sản.*"""

        return {
            'answer': response,
            'suggestions': [
                'Kiểm tra tài sản còn trống',
                'Xem đơn mượn của tôi',
                'Quy định mượn tài sản',
            ],
            'actions': [
                {
                    'type': 'link',
                    'label': '📝 Tạo đơn mượn',
                    'action': 'quan_ly_tai_san.don_muon_tai_san_action',
                }
            ],
        }

    def _handle_kiem_tra_lich(self, message):
        """Kiểm tra tài sản còn trống"""
        available_assets = self.env['phan_bo_tai_san'].search([
            ('tinh_trang', '=', 'binh_thuong')
        ], limit=10)
        
        if available_assets:
            asset_list = '\n'.join([f"• {a.tai_san_id.ten_tai_san} ({a.phong_ban_id.ten_phong_ban})" 
                                   for a in available_assets[:5]])
            response = f"""✅ **Tài sản có sẵn để mượn:**

{asset_list}

📊 Tổng cộng có **{len(available_assets)}** tài sản sẵn sàng cho mượn.

💡 *Bạn có thể tạo đơn mượn ngay bằng cách nhấn nút bên dưới.*"""
        else:
            response = """⚠️ **Hiện tại không có tài sản nào sẵn sàng cho mượn.**

Vui lòng liên hệ quản trị viên để biết thêm chi tiết."""

        return {
            'answer': response,
            'suggestions': [
                'Làm sao để mượn tài sản?',
                'Danh sách tài sản theo phòng ban',
            ],
            'actions': [
                {
                    'type': 'link',
                    'label': '📋 Xem tất cả tài sản',
                    'action': 'quan_ly_tai_san.phan_bo_tai_san_action',
                }
            ],
        }

    def _handle_bao_hanh(self, message):
        """Kiểm tra bảo hành tài sản"""
        user_employee = self.env['nhan_vien'].search([
            ('user_id', '=', self.env.user.id)
        ], limit=1)
        
        if user_employee:
            allocations = self.env['phan_bo_tai_san'].search([
                ('nhan_vien_su_dung_id', '=', user_employee.id)
            ])
            
            if allocations:
                asset_info = []
                for alloc in allocations:
                    asset = alloc.tai_san_id
                    # Field ngay_het_bao_hanh không tồn tại - hiển thị thông tin cơ bản
                    asset_info.append(
                        f"• **{asset.ten_tai_san}** - "
                        f"Giá trị: {asset.gia_tri_hien_tai:,.0f} VNĐ"
                    )
                
                if asset_info:
                    response = f"""🔧 **Tài sản được phân bổ cho bạn:**

{chr(10).join(asset_info)}

💡 *Nếu tài sản gặp sự cố, vui lòng liên hệ phòng kỹ thuật.*"""
                else:
                    response = "ℹ️ Các tài sản của bạn chưa có thông tin."
            else:
                response = "ℹ️ Bạn chưa được phân bổ tài sản nào."
        else:
            response = "ℹ️ Không tìm thấy thông tin nhân viên của bạn.\n\nVui lòng liên hệ quản trị viên để được hỗ trợ."

        return {
            'answer': response,
            'suggestions': [
                'Làm sao khi tài sản hỏng?',
                'Xem danh sách tài sản của tôi',
            ],
        }

    def _handle_thanh_ly(self, message):
        """Hướng dẫn quy trình thanh lý"""
        response = """📋 **Quy trình thanh lý tài sản:**

**Điều kiện thanh lý:**
- Tài sản đã khấu hao hết giá trị
- Tài sản hư hỏng không thể sửa chữa
- Tài sản lỗi thời không còn phù hợp

**Các bước thực hiện:**

1️⃣ **Đề xuất thanh lý**: Người quản lý tài sản tạo đề xuất thanh lý

2️⃣ **Kiểm kê tài sản**: Thực hiện kiểm kê trước khi thanh lý

3️⃣ **Phê duyệt**: Lãnh đạo phê duyệt đề xuất

4️⃣ **Thực hiện thanh lý**: Bán, tặng hoặc hủy tài sản

5️⃣ **Ghi nhận kế toán**: Hạch toán thanh lý tài sản

💡 *Liên hệ phòng Kế toán - Tài chính để được hỗ trợ chi tiết.*"""

        return {
            'answer': response,
            'suggestions': [
                'Xem danh sách tài sản chờ thanh lý',
                'Tạo đề xuất thanh lý',
            ],
        }

    def _handle_huong_dan(self, message):
        """Xử lý yêu cầu hướng dẫn chung"""
        knowledge = self._search_knowledge_by_query(message)
        
        if knowledge:
            return {
                'answer': knowledge[0].get('content', 'Không tìm thấy thông tin.'),
                'sources': knowledge,
            }
        
        return {
            'answer': """ℹ️ **Tôi có thể giúp bạn với các chủ đề sau:**

📦 **Quản lý tài sản:**
- Mượn/trả tài sản
- Kiểm tra lịch sử mượn
- Xem thông tin bảo hành

💰 **Quản lý tài chính:**
- Đề xuất mua tài sản
- Quy trình thanh lý
- Báo cáo khấu hao

❓ Bạn cần hỗ trợ về vấn đề gì?""",
            'suggestions': [
                'Làm sao để mượn máy chiếu?',
                'Quy trình đề xuất mua tài sản',
                'Kiểm tra tài sản còn trống',
            ],
        }

    def _handle_thong_ke(self, message):
        """Xử lý yêu cầu thống kê"""
        dashboard = self.env['dashboard.main']
        stats = dashboard.get_dashboard_data()
        
        tai_san = stats.get('tai_san', {})
        muon_tra = stats.get('muon_tra', {})
        
        response = f"""📊 **Thống kê tổng quan:**

**Tài sản:**
• Tổng số: {tai_san.get('total', 0)} tài sản
• Đang sử dụng: {tai_san.get('active', 0)}
• Đang cho mượn: {tai_san.get('dang_muon', 0)}
• Tổng giá trị: {tai_san.get('total_value', 0):,.0f} VNĐ

**Mượn trả:**
• Đơn chờ duyệt: {muon_tra.get('don_cho_duyet', 0)}
• Đang mượn: {muon_tra.get('don_dang_muon', 0)}
• Quá hạn: {muon_tra.get('qua_han', 0)}

💡 *Truy cập Dashboard để xem chi tiết hơn.*"""

        return {
            'answer': response,
            'actions': [
                {
                    'type': 'link',
                    'label': '📈 Xem Dashboard',
                    'action': 'q_trang_chu.action_dashboard_main',
                }
            ],
        }

    def _handle_quy_trinh(self, message):
        """Xử lý yêu cầu về quy trình, quy định"""
        response = """📚 **Các quy trình chính:**

1️⃣ **Mượn tài sản:**
Đăng ký → Chờ duyệt → Nhận tài sản → Sử dụng → Trả tài sản

2️⃣ **Đề xuất mua tài sản:**
Tạo đề xuất → Phê duyệt → Mua sắm → Nhập kho → Phân bổ

3️⃣ **Thanh lý tài sản:**
Đề xuất → Kiểm kê → Phê duyệt → Thực hiện → Ghi sổ

4️⃣ **Bảo trì, sửa chữa:**
Báo hỏng → Đánh giá → Sửa chữa → Nghiệm thu

❓ Bạn muốn tìm hiểu chi tiết quy trình nào?"""

        return {
            'answer': response,
            'suggestions': [
                'Quy trình mượn tài sản chi tiết',
                'Quy trình thanh lý tài sản',
                'Quy trình đề xuất mua tài sản',
            ],
        }

    def _handle_general(self, message):
        """Xử lý câu hỏi chung"""
        # Chào hỏi
        greetings = ['xin chào', 'hello', 'hi', 'chào', 'hey']
        if any(g in message.lower() for g in greetings):
            return {
                'answer': f"""👋 **Xin chào {self.env.user.name}!**

Tôi là **AI Assistant** - trợ lý thông minh của hệ thống Quản lý Tài sản.

Tôi có thể giúp bạn:
• 📦 Hướng dẫn mượn/trả tài sản
• 📅 Kiểm tra lịch trình tài sản
• 🔧 Tra cứu thông tin bảo hành
• 📋 Giải thích quy trình, quy định
• 📊 Cung cấp thống kê nhanh

❓ Bạn cần hỗ trợ gì hôm nay?""",
                'suggestions': [
                    'Làm sao để mượn máy chiếu?',
                    'Kiểm tra tài sản còn trống',
                    'Thống kê tổng quan',
                ],
            }

        # Cảm ơn
        thanks = ['cảm ơn', 'thank', 'thanks', 'tks']
        if any(t in message.lower() for t in thanks):
            return {
                'answer': """😊 **Không có gì!**

Rất vui được hỗ trợ bạn. Nếu cần thêm hỗ trợ, đừng ngần ngại hỏi tôi nhé!""",
            }

        # Mặc định
        return {
            'answer': """🤔 Tôi đang xử lý câu hỏi của bạn...

Bạn có thể thử hỏi theo các mẫu sau:
• "Làm sao để mượn máy chiếu?"
• "Tôi có thể mượn laptop ngày 15/2 không?"
• "Laptop của tôi còn bảo hành bao lâu?"
• "Quy trình thanh lý tài sản như thế nào?"

❓ Hoặc cho tôi biết bạn cần hỗ trợ về vấn đề gì?""",
            'suggestions': [
                'Mượn tài sản',
                'Kiểm tra bảo hành',
                'Thống kê tổng quan',
            ],
        }

    def _search_knowledge(self, topic):
        """Tìm kiếm trong knowledge base"""
        knowledge = self.env['chatbot.knowledge'].search([
            ('topic', '=', topic),
            ('active', '=', True)
        ], limit=5)
        return [{'title': k.title, 'content': k.content} for k in knowledge]

    def _search_knowledge_by_query(self, query):
        """Tìm kiếm knowledge base theo từ khóa"""
        knowledge = self.env['chatbot.knowledge'].search([
            '|', '|',
            ('title', 'ilike', query),
            ('content', 'ilike', query),
            ('keywords', 'ilike', query),
        ], limit=5)
        return [{'title': k.title, 'content': k.content} for k in knowledge]
