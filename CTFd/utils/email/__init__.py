from flask import url_for

from CTFd.utils import get_config
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email import mailgun, smtp
from CTFd.utils.formatters import safe_format
from CTFd.utils.security.signing import serialize


def sendmail(addr, text, subject="Message from {ctf_name}"):
    subject = safe_format(subject, ctf_name=get_config("ctf_name"))
    provider = get_mail_provider()
    if provider == "smtp":
        return smtp.sendmail(addr, text, subject)
    if provider == "mailgun":
        return mailgun.sendmail(addr, text, subject)
    return False, "No mail settings configured"


def password_change_alert(email):
    text = safe_format(
        get_config("password_change_alert_body"),
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        email_sender=get_config("mailfrom_addr"),
        url=url_for("auth.reset_password", _external=True),
    )

    subject = safe_format(
        get_config("password_change_alert_subject"), ctf_name=get_config("ctf_name")
    )
    return sendmail(addr=email, text=text, subject=subject)


def forgot_password(email):
    text = safe_format(
        get_config("password_reset_body"),
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        email_sender=get_config("mailfrom_addr"),
        url=url_for("auth.reset_password", data=serialize(email), _external=True),
    )

    subject = safe_format(
        get_config("password_reset_subject"), ctf_name=get_config("ctf_name")
    )
    return sendmail(addr=email, text=text, subject=subject)


def verify_email_address(addr):
    text = safe_format(
        get_config("verification_email_body"),
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        email_sender=get_config("mailfrom_addr"),
        url=url_for("auth.reset_password", data=serialize(addr), _external=True),
    )

    subject = safe_format(
        get_config("verification_email_subject"), ctf_name=get_config("ctf_name")
    )
    return sendmail(addr=addr, text=text, subject=subject)


def user_created_notification(addr, name, password):
    text = safe_format(
        get_config("user_creation_email_body"),
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        email_sender=get_config("mailfrom_addr"),
        url=url_for("views.static_html", _external=True),
        name=name,
        password=password,
    )

    subject = safe_format(
        get_config("user_creation_email_subject"), ctf_name=get_config("ctf_name")
    )
    return sendmail(addr=addr, text=text, subject=subject)


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")
    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]
        if domain not in domain_whitelist:
            return False
    return True
