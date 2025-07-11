from app.models.events_model import EventResult
from app.models.user_profile_model import UserProfile, Location
from app.utils.address_utils import calculate_distance
from datetime import datetime

def format_events_for_email(events: list[EventResult], user_profile: UserProfile) -> str:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Events for You</title>
        <!--[if mso]>
        <noscript>
            <xml>
                <o:OfficeDocumentSettings>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
            </xml>
        </noscript>
        <![endif]-->
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background-color: #faf5ff; color: #1e293b; min-height: 100vh;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #faf5ff;">
            <tr>
                <td align="center" style="padding: 20px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="1200" style="max-width: 1200px;">
                        <tr>
                            <td>
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
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
        
        # Format date and time
        date_info = ""
        date_of_event = event['event_details'].get('date_of_event')
        if date_of_event:
            try:
                # Handle date format conversion (dd-mm-yyyy to yyyy-mm-dd)
                date_parts = date_of_event.split("-")
                if len(date_parts) == 3:
                    # Convert from dd-mm-yyyy to yyyy-mm-dd
                    date_obj = datetime.strptime(f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}", "%Y-%m-%d")
                    date_info = date_obj.strftime("%A, %B %d, %Y")
                else:
                    date_info = date_of_event
            except:
                date_info = date_of_event
        
        time_info = ""
        start_time = event['event_details'].get('start_time')
        if start_time:
            time_info = start_time
            end_time = event['event_details'].get('end_time')
            if end_time:
                time_info += f" - {end_time}"
        
        # Calculate distance
        distance_info = ""
        location_of_event = event['event_details'].get('location_of_event')
        if (user_profile.get('location') and 
            location_of_event and 
            'latitude' in location_of_event and 
            'longitude' in location_of_event and
            location_of_event['latitude'] is not None and 
            location_of_event['longitude'] is not None):
            
            latitude = location_of_event['latitude']
            longitude = location_of_event['longitude']
            
            event_location: Location = {
                "latitude": latitude,
                "longitude": longitude
            }
            
            distance = calculate_distance(
                user_profile['location'], 
                event_location, 
                user_profile['distance_threshold']['unit']
            )
            
            unit = user_profile['distance_threshold']['unit']
        
        html += f"""
                                    <tr>
                                        <td style="padding: 0;">
                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" class="event-card" style="background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); overflow: hidden; margin-bottom: 20px;">
                                                <tr>
                                                    <td style="padding: 24px;">
                                                        <a href="{event['event_url']}" style="display: block; text-decoration: none; color: inherit; height: 100%; box-sizing: border-box; width: 100%;">
                                                            <h3 style="font-size: 1.2rem; font-weight: 700; color: #1e293b; margin: 0 0 12px 0; line-height: 1.3;">{event['event_details']['title']}</h3>
                                                            <p style="color: #64748b; margin: 0 0 12px 0; font-size: 1rem;">
                                                                Match: {emoji} <strong style="color: #7c3aed; font-weight: 600;">{relevance}%</strong>
                                                            </p>
                                                            {f'<p style="color: #64748b; margin: 0 0 8px 0; font-size: 0.95rem;">📅 {date_info}</p>' if date_info else ''}
                                                            {f'<p style="color: #64748b; margin: 0 0 8px 0; font-size: 0.95rem;">🕒 {time_info}</p>' if time_info else ''}
                                                            {f'<p style="color: #64748b; margin: 0 0 8px 0; font-size: 0.95rem;">📍 {distance:.1f} {unit} away</p>' if distance else ''}
                                                            <span style="display: inline-block; color: #7c3aed; font-size: 0.9rem; font-weight: 500; text-decoration: underline; margin-top: 12px;">Check it out →</span>
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
        """
    
    html += """
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html