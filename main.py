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

def post_daily_prompt(reddit):
    # Get daily_counter line, which is first line,
    # and increment it if there are new prompts left,
    # otherwise choose a random prompt from used_prompts.txt
    lines = open("counters.txt").read().splitlines()
    daily_counter = lines[0].rstrip()
    prompt_counter = lines[1].rstrip()
    total_prompts = lines[2].rstrip()

    # If no prompts left, choose random one
    # Increment daily counter (lines[0])
    if int(prompt_counter) > int(total_prompts):
        prompt_counter = random.randint(1, int(total_prompts))
        daily_prompt = get_prompt(prompt_counter)
        print("too far")
        lines[0] = str(int(lines[0].rstrip()) + 1)
        open("counters.txt", "w").write("\n".join(lines))

    else:
        # If prompts left still, use it
        # Increment prompt_counter (lines[1]) and total_prompts (lines[2])
        lines[0] = str(int(lines[0].rstrip()) + 1)
        lines[1] = str(int(lines[1].rstrip()) + 1)
        open("counters.txt", "w").write("\n".join(lines))

        daily_prompt = get_prompt(int(prompt_counter))

    title = "Daily3D#" + daily_counter + "--" + daily_prompt.capitalize()
    print(title)
    # reddit.subreddit("test").submit(title, selftext='')

def get_prompt(prompt_counter):
    with open("prompts.txt") as daily_prompt_file:
        for i, line in enumerate(daily_prompt_file):
            if i == prompt_counter - 1:
                daily_prompt = line.rstrip()
    daily_prompt_file.close()
    return daily_prompt

def main():
    reddit = bot_login()
    post_daily_prompt(reddit)

if __name__ == "__main__":
    main()
