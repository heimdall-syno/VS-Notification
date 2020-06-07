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

def html_add_item(content, movie, season, name, url, f4k):
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
    rating = " ({})".format(movie["rating"]) if movie and "rating" in movie else ""
    f4k = "- 4K" if f4k == True else ""
    cover = movie['cover url'] if movie and 'cover url' in movie else "https://thetvdb.com/images/missing/movie.jpg"

    ## Imdb URL or plain text
    if url:
        html_url = '''<a style="color: #000000; text-decorations:none;" href="{movie_url}">
                    {name} {rating} {f4k}
                 </a>'''.format(movie_url=url, name=name, rating=rating, f4k=f4k)
    else:
        html_url = '''{name} {rating} {f4k}'''.format(name=name, rating=rating, f4k=f4k)

    content = content + ''' \
    <div style="display: table; height: 70px; overflow: hidden;">
        <a href="{url}">
            <div id="image" style="display:inline; padding-left: 30px;">
                <img src="{cover}" width="65px"/>
            </div>
        </a>
        <div style="padding-left: 30px; display: table-cell; vertical-align: middle;">
            <div><font color="black"><strong><span>
                {html_url}
            </span></strong></font></div>
        </div>
    </div><p></p>'''.format(url=url, cover=cover, html_url=html_url)
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

        ## Add information whether its 4K or not
        f4k = ["4K", "2160p", "UHD", "HDR"]
        format_4k = True if any(u for u in f4k if u in movie_name) else False

        ## Series name correction
        season = ""
        if (os.path.basename(category) != "Filme"):
            movie_name, season = movie_name.replace(category, "").split(os.sep)[1:3]
            movie_name = movie_name.replace("oe", "ö").replace("ue", "ü").replace("ae", "ä")
            season = "- {} ".format(season)
            movie_season = "{}{}".format(movie_name, season)

        ## Movie name correction
        else:
            movie_name = movie_get_name(category, os.path.dirname(movie_name))
            movie_name = movie_name.replace("oe", "ö").replace("ue", "ü").replace("ae", "ä")

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
            content = html_add_item(content, movie, season, movie_name, movie_url, format_4k)
            infomsg("Added imdb entry (with image) for item", "HTML", (movie_name, movie, season))
        else:
            content = html_add_item(content, None, season, movie_name, None, format_4k)
            infomsg("Add non-imdb entry for item", "HTML", (movie_name, season))

        if (os.path.basename(category) == "Filme"):
            history.append(movie_name)
        else:
            history.append(movie_season)

    content = content + '<p>&nbsp;</p>'
    return content
