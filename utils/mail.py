import os, getpass
from datetime import datetime
from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def mail_get_addresses(args):
    """ Get all users and mail address of the current system

    Arguments:
        args {Namespace} -- Namespace containing all arguments.

    Returns:
        string -- List of tuples with users and mail addresses
    """

    ## Get the username, real name and the mail address of each user
    admin = getpass.getuser()
    user_file = os.path.join(os.sep, "volume1", "homes", admin, "users.csv")
    user_mails = os.path.join(args.scriptdir, "scripts", "user_mails.sh")
    p = Popen(["/bin/bash", user_mails, admin], stdout=PIPE, stderr=PIPE)
    p.communicate()
    with open(user_file, 'r', encoding='utf-8', errors='replace') as f: users = f.read()
    os.remove(user_file)

    ## Parse each entry and store it as tuple-list
    users = ("".join(i for i in users if ord(i) < 128)).split("\n")
    users = [u.replace("\n", "").replace("\"", "") for u in users]
    users = [u.replace(" (user)", "").replace(" (admin)", "") for u in users]
    users = list(filter(None, users))
    user_mails = ["{} <{}>".format(u.split(",")[1], u.split(",")[2]) for u in users if u.split(",")[0] != admin]
    admin_mails = ["{} <{}>".format(u.split(",")[1], u.split(",")[2]) for u in users if u.split(",")[0] == admin]
    mails = admin_mails if args.receivers == "admin" else user_mails
    if args.receivers == "all": mails = admin_mails + user_mails
    return mails

def mail_create_header(args):
    """ Create a MIMEMultiPart mail header.

    Arguments:
        args {Namespace} -- Namespace containing all arguments.

    Returns:
        MIMEMultipart -- Instance of a MIMEMultipart header.
    """

    message = MIMEMultipart('alternative')
    message['From'] = "{} <{}>".format(args.name, args.address)
    message['To'] = "; ".join(args.receivers)
    if args.date:
        td = datetime.today()
        current_day = datetime.strftime(datetime(td.year, td.month, td.day), "%d %B %Y")
        message['Subject'] = '{subject} since {date}'.format(subject=args.subject, date=current_day)
    else:
        message['Subject'] = '{subject}'.format(subject=args.subject)
    return message

def mail_send(message, content):
    """ Send the mail via sendmail (postfix) command

    Arguments:
        message {MIMEMultipart} -- Instance of a MIMEMultipart header.
        content {string}        -- HTML content as string.
    """

    message.attach(MIMEText(content, 'html'))
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(message.as_bytes())
