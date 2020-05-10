#################################################
##             Scope: Host-system              ##
#################################################

import os, sys, argparse, logging
cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(cur_dir, "scripts"))
sys.path.append(os.path.join(cur_dir, "VS-Utils"))
from movie import movie_get_releases, movie_get_name
from mail import mail_get_addresses, mail_send
from htmls import html_add_header, html_add_closing
from htmls import html_add_category, html_add_items
from prints import init_logging, debugmsg, errmsg, infomsg
from scope import scope_get

def check_path(log):
    if os.path.isdir(log):
        return log
    else:
        raise NotADirectoryError(log)

def check_interval(interval):
    inv = int(interval)
    if inv <= 0:
        raise argparse.ArgumentTypeError("Error: Invalid parater for argument \"--interval\"")
    return inv

def init_notification_log(args):
    ## Initialize the logging
    if (args.log):
        cfg = argparse.Namespace()
        cfg.log_dir = args.log
        cfg.log_level = logging.DEBUG
        init_logging(args, cfg)
    else:
        init_logging(None, None)
    debugmsg("-" * 35, "Notification")

def parse_arguments():
    """ Parse all shell arguments.

    Returns:
        Namespace -- Namespace containing all arguments.
    """
    ## Get the shell arguments
    args = argparse.Namespace()
    parser = argparse.ArgumentParser(description='Notification service for new VS releases')
    parser.add_argument('-n','--name', help='Name of the sender', required=True)
    parser.add_argument('-a','--address', help='Address of the sender', required=True)
    parser.add_argument('-c','--service', help='name of the service', required=True)
    parser.add_argument('-s','--subject', help='Subject of the mail', required=True)
    parser.add_argument('-r','--receivers', help='Receiver mode', choices=['admin', 'users', 'all'], required=True)
    parser.add_argument('-d','--date', help='Add release date to subject', action='store_true')
    parser.add_argument('-i','--interval', help='Notification interval (days)', type=check_interval, required=True)
    parser.add_argument('-l','--log', help='Logging directory', type=check_path)
    args = parser.parse_args()
    args.scriptdir = cur_dir
    args.scope = scope_get()
    return args

def main():

    ## Parse all shell arguments
    args = parse_arguments()

    ## Initialize the logging
    init_notification_log(args)

    ## Get all users and mail address of the current system
    args.receivers = mail_get_addresses(args)

    ## Get all categories and the corresponding items
    categories = movie_get_releases(args)
    if not categories:
        infomsg("No new items for any category", "Notification"); exit()

    ## Create a html-structure and add all categories and items
    content = html_add_header(args)
    for category in categories:
        category_name = os.path.basename(category[0])
        content = html_add_category(content, category_name)
        content = html_add_items(content, category[0], category[1])
    content = html_add_closing(args, content)

    ## Send the mail via sendmail (postfix) command
    mail_send(args, content)

if __name__ == "__main__":
    main()
