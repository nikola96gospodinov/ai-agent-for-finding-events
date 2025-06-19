from app.models.events_model import EventResult

def format_events_for_email(events: list[EventResult]) -> str:
    html = """
    <html>
    <head>
    </head>
    <body style="padding: 24px; margin: 0; color: oklch(21% 0.034 264.665); background: linear-gradient(oklch(93% 0.034 272.788), oklch(96.2% 0.018 272.314)); max-width: 400px;">
    """
    
    for i, event in enumerate(events):
        relevance = event['relevance']
        if relevance == 100:
            emoji = "💯"
        elif relevance >= 80:
            emoji = "🚀"
        elif relevance >= 60:
            emoji = "⭐"
        elif relevance >= 40:
            emoji = "🤔"
        else:
            emoji = "📅"
        
        html += f"""
        <a href="{event['event_url']}" style="text-decoration: none; color: inherit; border-radius: 16px; padding: 12px; display: block; margin-bottom: 8px;">
            <h3 style="font-size: 18px; margin-bottom: 2px;">{event['event_details']['title']}</h3>
            <p style="margin-bottom: 6px;">Match: {emoji} <b>{relevance}%</b></p>
            <span style="font-size: 14px; color: oklch(28.3% 0.141 291.089); text-decoration: underline; display: block;">Check it out</span>
        </a>
        """
        
        if i < len(events) - 1:
            html += "<hr />"
    
    html += """
    </body>
    </html>
    """
    return html