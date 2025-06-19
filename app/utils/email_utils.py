from app.models.events_model import EventResult

def format_events_for_email(events: list[EventResult]) -> str:
    html = """
    <html>
    <head>
        <style>
            * {
                margin: 0;
                padding: 0;
            }

            .outer-box-link {
                text-decoration: none;
                color: inherit;
                border-radius: 16px;
                padding: 12px;
                display: block;
                margin-bottom: 8px;
            }

            body {
                padding: 24px;
                margin: 0;
                height: 100vh;
                color: oklch(21% 0.034 264.665);
                background: linear-gradient(oklch(93% 0.034 272.788), oklch(96.2% 0.018 272.314));
                max-width: 400px;
            }

            h1 {
                font-size: 24px;
                margin-bottom: 16px;
            }

            .outer-box-link h3 {
                font-size: 18px;
                margin-bottom: 2px;
            }

            .outer-box-link p {
                margin-bottom: 6px;
            }

            .box-link {
                font-size: 14px;
                color: oklch(28.3% 0.141 291.089);
                text-decoration: underline;
                display: block;
            }
        </style>
    </head>
    <body>
        <h1>Events specifically picked for you! 🤩</h1>
    """
    
    for i, event in enumerate(events):
        relevance = event['relevance']
        if relevance == 100:
            emoji = "💯"
        if relevance >= 80:
            emoji = "🚀"
        elif relevance >= 60:
            emoji = "⭐"
        elif relevance >= 40:
            emoji = "🤔"
        else:
            emoji = "📅"
        
        html += f"""
        <a href="{event['event_url']}" class="outer-box-link">
            <h3>{event['event_details']['title']}</h3>
            <p>Match: {emoji} <b>{relevance}%</b></p>
            <span class="box-link">Check it out</span>
        </a>
        """
        
        # Add horizontal rule between events (except after the last one)
        if i < len(events) - 1:
            html += "<hr />"
    
    html += """
    </body>
    </html>
    """
    return html