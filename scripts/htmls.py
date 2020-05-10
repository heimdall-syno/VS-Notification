import logging
logging.getLogger('imdbpy').setLevel(logging.WARNING)
logging.getLogger('imdb').setLevel(logging.WARNING)
import os, imdb, textwrap
from movie import movie_get_name
from prints import debugmsg, errmsg, infomsg

def html_add_header(args):
    """ Add the HTML header.

    Arguments:
        args {Namespace} -- Namespace containing all arguments.

    Returns:
        string -- HTML content as string.
    """

    text = "<font color=\"black\"> Now on {service}: Newly added movies, TV shows, seasons, " \
           "animes. Check out the release list below:</font><br>".format(service=args.service)
    content = "<html><body style=\"background-color:white;\">" \
              "<STYLE>A {text-decoration: none;} </STYLE>" + text
    return content

def html_add_closing(args, content):
    """ Add the closeing tags for the html content.

    Arguments:
        args {Namespace} -- Namespace containing all arguments.
        content {string} -- HTML content as string.

    Returns:
        string -- Updated HTML content as string.
    """

    content = content + '''\
    <p><strong>Enjoy {service}!</strong></p>
    <p>&nbsp;</p></body> </html>'''.format(service=args.service)
    return content

def html_add_category(content, category):
    """ Add a category as a caption to the HTML content.

    Arguments:
        content {string}  -- HTML content as string.
        category {stirng} -- Category name.

    Returns:
        string -- Updated HTML content as string.
    """

    content = content + \
        '<font color="black"><h4>{category}:</h4></font>'.format(category=category)
    return content

def html_add_item_image(content, movie, season, name, url):
    """ Add a item with an image next to the title.

    Arguments:
        content {string}  -- HTML content as string.
        movie {string}    -- Movie instance of IMDbPy.
        season {string}   -- Name of the season if it is a series.
        name {string}     -- Title of the item.
        url {string}      -- IMDB url of the item.
    Returns:
        string -- Updated HTML content as string.
    """

    name = "{} {}".format(name, season)
    name =  "<br/>".join(textwrap.wrap(name, width=25))
    rating = " ({})".format(movie["rating"]) if "rating" in movie else ""
    content = content + ''' \
    <div style="display: table; height: 70px; overflow: hidden;">
        <div id="image" style="display:inline; padding-left: 30px;">
            <img src="{movie_image_url}" width="65px"/>
        </div>
        <div style="padding-left: 30px; display: table-cell; vertical-align: middle;">
            <div><font color="black"><strong><span>
                <a style="color: #000000; text-decorations:none;" href="{movie_url}">
                    {name} {rating}
                </a>
            </span></strong></font></div>
        </div>
    </div><p></p>'''.format(movie_image_url=movie['cover url'], movie_url=url,
                            name=name, rating=rating)
    return content

def html_add_item_without_image(content, movie, season, name, url):
    """ Add a item with an image next to the title.

    Arguments:
        content {string}  -- HTML content as string.
        movie {string}    -- Movie instance of IMDbPy.
        season {string}   -- Name of the season if it is a series.
        name {string}     -- Title of the item.
        url {string}      -- IMDB url of the item.
    Returns:
        string -- Updated HTML content as string.
    """

    name = "{} {}".format(name, season)
    name =  "<br/>".join(textwrap.wrap(name, width=25))
    rating = " ({})".format(movie["rating"]) if "rating" in movie else ""
    content = content + ''' \
    <div style="display: table; height: 70px; overflow: hidden;">
        <div id="image" style="display:inline;padding-left: 30px;">
            <img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" width="65px"/>
        </div>
    <div style="padding-left: 30px; display: table-cell; vertical-align: middle;">
        <div><font color="black"><strong><span>
            <a style="color: #000000; text-decorations:none;" href="{movie_url}">
                {movie_name} {rating}
            </a>
        </span></strong></font></div>
        </div>
    </div><p></p>'''.format(movie_url=url, movie_name=name, rating=rating)
    return content

def html_add_items(content, category, items):
    """ Add all items of a single category as html div-blocks.

    Arguments:
        content {string}  -- HTML content as string.
        category {string} -- Path of the current category.
        items {list}      -- List of items of the category.

    Returns:
        string -- HTML content with all items added.
    """

    ## Intialite IMDBPy
    access = imdb.IMDb()

    history = []
    for movie_name in items:
        ## Series name correction
        season = ""
        if (os.path.basename(category) != "Filme"):
            movie_name, season = movie_name.replace(category, "").split(os.sep)[1:3]
            season = "- {} ".format(season)
            movie_season = "{}{}".format(movie_name, season)

        ## Movie name correction
        else:
            movie_name = movie_get_name(category, os.path.dirname(movie_name))
            movie_name = movie_name.replace("oe", "ö").replace("ue", "ü").replace("ae", "ä")
            ultra_hd = ["4K", "2160p", "UHD", "HDR"]
            if any(u for u in ultra_hd if u in movie_name):
                infomsg("Skip entry due to 4K resolution", "HTML", (movie_name,))
                continue

        ## Check for duplicates
        if (os.path.basename(category) == "Filme" and movie_name in history):
            infomsg("Skip entry due to duplicate", "HTML", (movie_name,))
            continue
        elif (os.path.basename(category) != "Filme" and movie_season in history):
            infomsg("Skip entry due to duplicate", "HTML", (movie_season,))
            continue

        ## Search for the movie/series and add the item to the html code
        search_results  = access.search_movie(movie_name)
        if search_results:
            movieID = search_results[0].movieID
            movie = access.get_movie(movieID)
            movie_url = access.get_imdbURL(movie)
            if movie:
                if 'cover url' in movie:
                    content = html_add_item_image(content, movie, season, movie_name, movie_url)
                    infomsg("Added image entry for entry", "HTML", (movie_name, movie, season))
                else:
                    content = html_add_item_without_image(content, movie, season, movie_name, movie_url)
                    infomsg("Added plain entry for entry", "HTML", (movie_name, movie, season))
                if (os.path.basename(category) == "Filme"):
                    history.append(movie_name)
                else:
                    history.append(movie_season)
    content = content + '<p>&nbsp;</p>'
    return content
