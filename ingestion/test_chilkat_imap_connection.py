import sys

import chilkat2

from api.config.settings import settings


def unlock_chilkat() -> None:
    if not settings.chilkat_license_key:
        raise ValueError("CHILKAT_LICENSE_KEY must be configured in .env")

    glob = chilkat2.Global()

    success = glob.UnlockBundle(settings.chilkat_license_key)

    if not success:
        raise RuntimeError(
            "Failed to unlock Chilkat.\n"
            f"{glob.LastErrorText}"
        )

    print("Chilkat unlocked successfully.")
    print(f"Chilkat status: {glob.UnlockStatus}")


def test_chilkat_imap_connection() -> None:
    if not settings.imap_user or not settings.imap_password:
        raise ValueError("IMAP_USER and IMAP_PASSWORD must be configured in .env")

    unlock_chilkat()

    imap = chilkat2.Imap()
    imap.Ssl = settings.imap_use_ssl
    imap.Port = settings.imap_port

    print("\nConnecting to IMAP server with Chilkat...")
    print(f"Host: {settings.imap_host}")
    print(f"User: {settings.imap_user}")

    success = imap.Connect(settings.imap_host)

    if not success:
        raise RuntimeError(
            "Failed to connect to IMAP server.\n"
            f"{imap.LastErrorText}"
        )

    print("Connected successfully.")

    success = imap.Login(settings.imap_user, settings.imap_password)

    if not success:
        raise RuntimeError(
            "Failed to login to IMAP server.\n"
            f"{imap.LastErrorText}"
        )

    print("Login successful.")

    mailboxes = imap.ListMailboxes("", "*")

    if mailboxes is None:
        raise RuntimeError(
            "Failed to list mailboxes.\n"
            f"{imap.LastErrorText}"
        )

    print("\nAvailable mailboxes:")

    max_to_show = min(mailboxes.Count, 10)

    for index in range(max_to_show):
        print(mailboxes.GetName(index))

    imap.Disconnect()

    print("\nChilkat IMAP connection test completed successfully.")


if __name__ == "__main__":
    try:
        test_chilkat_imap_connection()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
