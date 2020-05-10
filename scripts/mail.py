import os, getpass, logging
from datetime import datetime
from subprocess import Popen, PIPE
logging.getLogger('email').setLevel(logging.WARNING)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from prints import debugmsg, errmsg, infomsg
from users import users_get_selection

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
    user_mails = os.path.join(args.scriptdir, "user_mails.sh")
    p = Popen(["/bin/bash", user_mails, admin], stdout=PIPE, stderr=PIPE)
    stderr = p.communicate()[1]
    if p.returncode != 0:
        errmsg("Could not get user mail addresses", (stderr,)); exit()
    try:
        with open(user_file, 'r', encoding='utf-8', errors='replace') as f: users = f.read()
    except EnvironmentError:
        errmsg("Could not read the user mail addresses file", (user_file,)); exit()
    os.remove(user_file)

    ## Parse user names and separate the admin
    users = ("".join(i for i in users if ord(i) < 128)).split("\n")
    users = [u.replace("\n", "").replace("\"", "") for u in users]
    users = [u.replace(" (user)", "").replace(" (admin)", "") for u in users]
    users = list(filter(None, users))
    fs_admin = users_get_selection(2, False)
    admin = [u for u in users if u.split(',')[0] == fs_admin]
    users = list(set(users) - set(admin))

    ## Get the mail tuples
    fs_admin = users_get_selection(2, False)
    user_mails = ["{} <{}>".format(u.split(",")[1], u.split(",")[2]) for u in users]
    admin_mails = ["{} <{}>".format(a.split(",")[1], a.split(",")[2]) for a in admin]
    mails = admin_mails if args.receivers == "admin" else user_mails

    if args.receivers == "all": mails = admin_mails + user_mails
    infomsg("Selected list of mail addresses by receivers argument", "Mail", (",".join(mails),))
    return mails

def mail_send(args, content):
    """ Send the mail via sendmail (postfix) command

    Arguments:
        args {Namespace} -- Namespace containing all arguments.
        content {string} -- HTML content as string.
    """

    infomsg("Start sending the individual mails", "Mail")
    for receiver in args.receivers:
        message = MIMEMultipart('alternative')
        message['From'] = "{} <{}>".format(args.name, args.address)
        message['To'] = receiver
        if args.date:
            td = datetime.today()
            current_day = datetime.strftime(datetime(td.year, td.month, td.day), "%d %B %Y")
            message['Subject'] = '{subject} since {date}'.format(subject=args.subject, date=current_day)
        else:
            message['Subject'] = '{subject}'.format(subject=args.subject)
        message.attach(MIMEText(content, 'html'))
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        stderr = p.communicate(message.as_bytes())[1]
        if p.returncode != 0:
            infomsg("sendmail returned with non-zero return value", "Mail", stderr)
        infomsg("Send mail", "Mail", (receiver,))