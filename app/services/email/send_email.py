
from mailgun.client import Client
from app.core.env_vars import get_env_var

key = get_env_var("MAILGUN_API_KEY")
domain = get_env_var("MAILGUN_DOMAIN")
client: Client = Client(auth=("api", key)) # type: ignore

def post_message(email_to: str, email_from: str, subject: str, html: str) -> None:
    data = {
        "from": email_from,
        "to": email_to,
        "subject": subject,
        "html": html
    }

    req = client.messages.create(data=data, domain=domain)
    print(req.json())