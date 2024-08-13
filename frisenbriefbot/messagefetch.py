
import logging
from imbox import Imbox

logger = logging.getLogger(__name__)

def fetch_messages(host, email_addr, password, since):
    """Filter and return Email messages"""
    with Imbox(
        host,
        username=email_addr,
        password=password,
        ssl=True,
        ssl_context=None,
        starttls=False,
    ) as imbox:
        status, folders = imbox.folders()
        print(f"{status}, {len(folders)} folders")
        msgs = imbox.messages(sent_to="frisenbrief@avfrisia.de", date__gt=since)

        # Some messages are corrupt...
        try:
            for uid, message in msgs:
                    if len(message.attachments) > 0:
                        logger.info(f"Message with UID {uid} has attachments")
                        yield message
        except Exception as e:
            logging.exception(e)