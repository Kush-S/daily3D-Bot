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
    with open("counters.txt") as file:
        for i, line in enumerate(file):
            if i == 0:
                daily_counter = line.rstrip()
            if i == 1:
                total_prompts = line.rstrip()
    file.close()

    with open("daily_prompts.txt") as file:
        if int(daily_counter) > int(total_prompts):
            daily_prompt = "too far"
            print("too far")
        else:
            for i, line in enumerate(file):
                if i == int(daily_counter) - 1:
                    daily_prompt = line.rstrip()
        file.close()

    title = "Daily3D#" + daily_counter + "--" + daily_prompt.capitalize()
    print(title)
    # reddit.subreddit("test").submit(title, selftext='')

def main():
    reddit = bot_login()
    post_daily_prompt(reddit)

if __name__ == "__main__":
    main()
