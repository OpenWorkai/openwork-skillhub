#!/usr/bin/env python3
"""
Convert a markdown article to a WeChat-ready HTML file with embedded base64 images.
Usage: python3 md_to_wechat_html.py <input.md> [output.html]
"""
import sys
import os
import re
import base64

def get_mime_type(ext):
    return {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }.get(ext.lower(), 'image/png')

def image_to_base64(img_path):
    with open(img_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    ext = os.path.splitext(img_path)[1]
    mime = get_mime_type(ext)
    return f"data:{mime};base64,{data}"

def resolve_image_path(md_path, img_ref):
    """Resolve image path relative to the MD file location."""
    md_dir = os.path.dirname(os.path.abspath(md_path))
    full_path = os.path.normpath(os.path.join(md_dir, img_ref))
    return full_path

def md_to_html(md_text, md_path):
    """Simple markdown to HTML conversion with WeChat-friendly styling."""
    lines = md_text.split('\n')
    html_lines = []
    in_list = False
    in_blockquote = False
    
    for line in lines:
        stripped = line.strip()
        
        # Close list/blockquote if needed
        if in_list and not stripped.startswith('- '):
            html_lines.append('</ul>')
            in_list = False
        if in_blockquote and not stripped.startswith('> '):
            html_lines.append('</blockquote>')
            in_blockquote = False
        
        # Image: ![alt](path)
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', stripped)
        if img_match:
            alt = img_match.group(1)
            img_ref = img_match.group(2)
            img_path = resolve_image_path(md_path, img_ref)
            if os.path.exists(img_path):
                b64 = image_to_base64(img_path)
                html_lines.append(f'<p style="text-align:center;margin:20px 0;"><img src="{b64}" alt="{alt}" style="max-width:100%;border-radius:8px;" /></p>')
            else:
                html_lines.append(f'<p style="color:#999;text-align:center;">[图片缺失: {alt}]</p>')
            continue
        
        # Headers
        if stripped.startswith('# '):
            title = stripped[2:]
            html_lines.append(f'<h1 style="color:#2D3E4F;font-size:22px;font-weight:bold;text-align:center;margin:25px 0 15px;">{title}</h1>')
            continue
        if stripped.startswith('## '):
            title = stripped[3:]
            html_lines.append(f'<h2 style="color:#2D3E4F;font-size:19px;font-weight:bold;margin:30px 0 12px;border-bottom:2px solid #7B6B8D;padding-bottom:8px;">{title}</h2>')
            continue
        if stripped.startswith('### '):
            title = stripped[4:]
            html_lines.append(f'<h3 style="color:#7B6B8D;font-size:16px;font-weight:bold;margin:25px 0 10px;">{title}</h3>')
            continue
        
        # Horizontal rule
        if stripped == '---':
            html_lines.append('<hr style="border:none;border-top:1px solid #E8E2ED;margin:25px 0;" />')
            continue
        
        # List items
        if stripped.startswith('- '):
            if not in_list:
                html_lines.append('<ul style="margin:12px 0;padding-left:20px;color:#3a3a3a;line-height:1.9;">')
                in_list = True
            item = stripped[2:]
            # Bold
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#2D3E4F;">\1</strong>', item)
            html_lines.append(f'<li style="margin:6px 0;">{item}</li>')
            continue
        
        # Blockquote
        if stripped.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote style="border-left:4px solid #7B6B8D;background:#F7F2F5;padding:15px 20px;margin:20px 0;color:#2D3E4F;font-size:15px;border-radius:0 8px 8px 0;">')
                in_blockquote = True
            text = stripped[2:]
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            html_lines.append(f'<p style="margin:5px 0;">{text}</p>')
            continue
        
        # Bold inline
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#2D3E4F;">\1</strong>', stripped)
        
        # Empty line
        if not stripped:
            continue
        
        # Regular paragraph
        html_lines.append(f'<p style="color:#3a3a3a;font-size:15px;line-height:1.9;margin:12px 0;letter-spacing:0.5px;">{text}</p>')
    
    # Close any open tags
    if in_list:
        html_lines.append('</ul>')
    if in_blockquote:
        html_lines.append('</blockquote>')
    
    return '\n'.join(html_lines)

def generate_html(md_path, output_path=None):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    body_html = md_to_html(md_text, md_path)
    
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公众号文章预览</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;">
<div style="max-width:677px;margin:0 auto;background:#fff;padding:30px 25px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Helvetica Neue',sans-serif;">
{body_html}
</div>
<p style="text-align:center;color:#999;font-size:12px;padding:20px;">在浏览器中 Ctrl+A 全选 → Ctrl+C 复制 → 粘贴到公众号编辑器</p>
</body>
</html>'''
    
    if output_path is None:
        output_path = os.path.splitext(md_path)[0] + '.html'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"HTML generated: {output_path}")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 md_to_wechat_html.py <input.md> [output.html]")
        sys.exit(1)
    
    md_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_html(md_path, output_path)
