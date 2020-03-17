import praw
import config
import random

def bot_login():
    reddit = praw.Reddit(username = config.username,
            password = config.password,
            client_id = config.client_id,
            client_secret = config.client_secret,
            user_agent = config.user_agent)

    return reddit

def get_title(reddit):
    old_prompts = []

    # Get the 7 newsest prompts,
    # and strip off some of the words to get day number and prompt later
    submissions = reddit.subreddit('Daily3D').new(limit=30)
    for post in submissions:
        if "Daily3D#" in post.title and "--" in post.title:
            old_prompts.append(post.title.split("Daily3D#")[1])

    # Get the day of the latest prompt and add 1 for new day
    day = int(old_prompts[0].split("--")[0]) + 1
    print("day: " + str(day))

    # Store the 7 latest prompts by themselves in old_prompts
    length = len(old_prompts)
    for i in range(length):
        old_prompts[i] = old_prompts[i].split("--")[1]

    new_prompt = get_prompt().capitalize()
    print("New prompt: " + new_prompt)
    print("List is: " + str(old_prompts))
    while new_prompt in old_prompts:
        new_prompt = get_prompt().capitalize()
        print(new_prompt)

    title = "Daily3D#" + str(day) + "--" + new_prompt
    return title

def get_prompt():
    # Get total number of prompts
    lines = open("counters.txt").read().splitlines()
    total_prompts = lines[0].rstrip()

    # Generate random number
    random_num = random.randint(1, int(total_prompts))

    # Choose prompt from prompts.txt
    daily_prompt = ""
    with open("prompts.txt") as daily_prompt_file:
        for i, line in enumerate(daily_prompt_file):
            if i == random_num - 1:
                daily_prompt = line.rstrip()
    daily_prompt_file.close()
    return daily_prompt


def main(event, context):
    reddit = bot_login()
    title = get_title(reddit)
    reddit.subreddit("Daily3D").submit(title, selftext='', send_replies=False)

if __name__ == "__main__":
    main()
