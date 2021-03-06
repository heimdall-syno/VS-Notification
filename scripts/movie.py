import os
from datetime import datetime, timedelta
from collections import Counter
from os.path import isdir, join
from prints import debugmsg, errmsg, infomsg

def delimiter_get(filename):
    """ Get the delimiter of the current movie file.

    Arguments:
        filename {string} -- File name of the current movie.

    Returns:
        string -- String containing the most common delimiter.
    """

    delimiters = [".", "-", "_"]
    delimiter_count = Counter(filename).most_common()
    delimiter_count = [(key, val) for key, val in delimiter_count if key in delimiters]
    delimiter = sorted(delimiter_count, key=lambda x: x[1])[-1][0]
    return delimiter

def movie_get_name(category, movie_path):
    """ Get the real movie name of the file

    Arguments:
        category {string}   -- Path of the category ("/volume1/Serien")
        movie_path {string} -- Path of the current movie file

    Returns:
        string -- Fixed movie name
    """

    movie_name = []
    movie_path_bk = movie_path.replace(category, "").split(os.sep)[1]
    for token in movie_path_bk.split(delimiter_get(movie_path)):
        if (token.isdigit() and int(token) > 1925 and int (token) < 2050):
            break
        movie_name.append(token)
    return " ".join(movie_name)

def movie_get_releases(args):
    """ Get all new "releases" sorted by their category for the passed interval.
        All changelog files of mounts are filtered by the date.

    Arguments:
        args {Namespace} -- Namespace containing all arguments.

    Returns:
        list -- List of categories and their items.
    """

    ## Get all mounts of the main volume
    volume_path = os.path.join(os.sep, "volume1")
    mounts = [m for m in os.listdir(volume_path) if isdir(join(volume_path, m))]
    mounts = [join(volume_path, m) for m in mounts if "@" not in m]
    since = datetime.today() - timedelta(days=args.interval)
    since = since.replace(hour=0, minute=0, second=0, microsecond=0)

    ## Get all items per category (mount)
    items, invalid = ([] for _ in range(2))
    for mount in mounts:
        changelog = os.path.join(mount, "changelog.txt")
        if not os.path.isfile(changelog):
            invalid.append(mount)
            continue
        with open(changelog, 'r') as f: cat_items = f.readlines()
        cat_items = [i.replace('\n', '').split(',') for i in cat_items]
        cat_items = [i[1] for i in cat_items if datetime.strptime(i[0], "%Y-%m-%d") > since]
        cat_items = sorted(list(set(cat_items)))
        if cat_items:
            items.append((mount, cat_items))
            debugmsg("Releases for mount", "Mounts", (mount, ','.join(cat_items)))
    infomsg("Skipped following mounts due to no changelog file", "Mounts", (','.join(invalid),))
    return sorted(items)
