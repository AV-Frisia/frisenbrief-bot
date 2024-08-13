from pathvalidate import sanitize_filename

from frisenbriefbot.attachmentconvert import convert
import logging
import os
import pathlib

import logging

logger = logging.getLogger(__name__)


def process_email(output_dir, message):
    try:
        process_email_unsame(output_dir, message)
    except Exception as e:
        logging.exception(e)

def process_email_unsame(output_dir, message):
    """Save attachments from an email to disk, returning a list of files"""

    # Return an array of finished tex files
    processed_files = []

    # First, grab metadata
    if not hasattr(message, "subject"):
        message.subject = "[No Subject]"

    if message.sent_from[0]["name"]:
        sender = message.sent_from[0]["name"]
    else:
        sender = message.sent_from[0]["email"]

    # Sanitize metadata
    message.subject = sanitize_filename(message.subject)
    sender = sanitize_filename(sender)

    # Create folder to dump files in
    folder = os.path.join(output_dir, sender, message.subject)
    os.makedirs(folder, exist_ok=True)

    # Save, and if possible convert, each attachment
    for idx, attachment in enumerate(message.attachments):
        filename = sanitize_filename(attachment.get("filename"))

        # First, write our original file
        try:
            original_files_folder = os.path.join(folder, "original")
            os.makedirs(original_files_folder, exist_ok=True)
            original_file_path = os.path.join(original_files_folder, filename)
            original_file = open(original_file_path, "wb")
            original_file.write(attachment.get("content").getbuffer())
            original_file.close()
            logging.info(f"Saved {filename}")
        except Exception as e:
            logging.error(f"Could not save original attachment {filename}")

        # Infer file format from extension
        p = pathlib.Path(filename)
        file_title = p.stem
        file_extension = p.suffix
        file_format = file_extension[1:]

        # Convert the file
        converted = ""
        try:
            converted = convert(file_format, attachment.get("content").read())
            logging.info(f"Converted {filename}")
        except Exception as e:
            logging.error(f"Could not convert {filename}")

        # If the file is successfully converted, write it to disk
        if converted:
            output_path = os.path.join(folder, file_title + ".tex")
            output_file = open(output_path, "w")

            # Add metadata to make it easier for the editor
            metadata_string = "% Von: {author}\r\n% Betreff: {subject}\r\n".format(
                author=sender, subject=message.subject
            )

            # Dump our converted file
            output_file.write(metadata_string)
            output_file.write(converted)
            output_file.close()

            processed_files.append(output_path)

    return filter(None, processed_files)
