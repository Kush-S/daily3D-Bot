import praw
import config

def bot_login():
    reddit = praw.Reddit(username = config.username,
            password = config.password,
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent = config.user_agent)

    return reddit


def post_daily_prompt(reddit):

    # Do stuff here

reddit = bot_login()
post_daily_prompt(reddit)
