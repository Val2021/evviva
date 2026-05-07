import imaplib

from api.config.settings import settings


def test_imap_connection() -> None:
    if not settings.imap_user or not settings.imap_password:
        raise ValueError("IMAP_USER and IMAP_PASSWORD must be configured in .env")

    print("Connecting to IMAP server...")
    print(f"Host: {settings.imap_host}")
    print(f"User: {settings.imap_user}")

    if settings.imap_use_ssl:
        mail = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    else:
        mail = imaplib.IMAP4(settings.imap_host, settings.imap_port)

    mail.login(settings.imap_user, settings.imap_password)

    print("Login successful.")

    status, mailboxes = mail.list()

    if status == "OK":
        print("\nAvailable mailboxes:")
        for mailbox in mailboxes[:10]:
            print(mailbox.decode("utf-8", errors="ignore"))

    mail.logout()
    print("\nIMAP connection test completed successfully.")


if __name__ == "__main__":
    test_imap_connection()
