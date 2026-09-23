import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        smtp_from: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from
        logger.info(f"Initializing EmailSender with SMTP host: {smtp_host}:{smtp_port}")

    def send_report(
        self,
        to_emails: List[str],
        subject: str,
        markdown_content: str,
        meeting_title: str,
        attachment_filename: Optional[str] = None,
    ) -> bool:
        if not to_emails:
            logger.warning("No recipient emails provided")
            return False
        if self.smtp_host == "smtp.example.com":
            logger.info("Mock email sending (example config)")
            logger.info(f"Would send to: {to_emails}")
            logger.info(f"Subject: {subject}")
            return True
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0800')

            html_content = self._markdown_to_html(markdown_content)
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
                        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h2 style="margin: 0;">🌾 太空育种会议纪要</h2>
                            <p style="margin: 10px 0 0 0; opacity: 0.9;">{meeting_title}</p>
                        </div>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                            {html_content}
                        </div>
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; font-size: 12px; color: #6c757d;">
                            <p>此邮件由太空育种基因轨迹纪要系统自动生成。</p>
                            <p>如有疑问，请联系项目管理员。</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            msg.attach(MIMEText(markdown_content, 'plain', 'utf-8'))

            if attachment_filename:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(markdown_content.encode('utf-8'))
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment_filename}"'
                )
                msg.attach(part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_from, to_emails, msg.as_string())

            logger.info(f"Email sent successfully to {len(to_emails)} recipients")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return False

    def _markdown_to_html(self, markdown_text: str) -> str:
        lines = markdown_text.split('\n')
        html_lines = []
        in_list = False
        in_quote = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                if in_quote:
                    html_lines.append('</blockquote>')
                    in_quote = False
                html_lines.append('<br/>')
                continue
            if stripped.startswith('# '):
                html_lines.append(f'<h1 style="color: #1e3a5f;">{stripped[2:]}</h1>')
            elif stripped.startswith('## '):
                html_lines.append(f'<h2 style="color: #2563eb; margin-top: 24px;">{stripped[3:]}</h2>')
            elif stripped.startswith('### '):
                html_lines.append(f'<h3 style="color: #0891b2;">{stripped[4:]}</h3>')
            elif stripped.startswith('- '):
                if not in_list:
                    html_lines.append('<ul style="margin: 10px 0; padding-left: 24px;">')
                    in_list = True
                html_lines.append(f'<li style="margin: 6px 0;">{stripped[2:]}</li>')
            elif stripped.startswith('**') and stripped.endswith('**'):
                html_lines.append(f'<p><strong>{stripped[2:-2]}</strong></p>')
            elif stripped.startswith('>'):
                if not in_quote:
                    html_lines.append('<blockquote style="border-left: 4px solid #06b6d4; padding-left: 16px; margin: 12px 0; color: #475569; font-style: italic;">')
                    in_quote = True
                html_lines.append(stripped[1:].strip())
            elif stripped.startswith('---'):
                html_lines.append('<hr style="border: none; border-top: 2px solid #e2e8f0; margin: 24px 0;"/>')
            elif '|' in stripped and stripped.count('|') >= 2:
                html_lines.append(f'<p><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px;">{stripped}</code></p>')
            else:
                html_lines.append(f'<p>{stripped}</p>')

        if in_list:
            html_lines.append('</ul>')
        if in_quote:
            html_lines.append('</blockquote>')

        return '\n'.join(html_lines)
