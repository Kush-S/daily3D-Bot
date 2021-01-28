import praw
import config
import os.path
import random
import boto3
from datetime import datetime

def main():
    NUMBER_OF_DAYS = 365
    MAX_PROMPT_CHECKS = 1000
    recent_prompts = []
    available_prompts = []
    bucket_files = []
    GENERAL_PROMPTS_FILE = "general_prompts.txt"
    PRIORITY_PROMPTS_FILE = "priority_prompts.txt"

    if os.path.getsize("prompts.txt") <= 0:
        print("prompts.txt file is empty. Stopping program")
        return

    bucket_files = get_bucket_files()

    if PRIORITY_PROMPTS_FILE in bucket_files and not check_aws_empty_file(PRIORITY_PROMPTS_FILE):
        available_prompts = get_available_prompts(PRIORITY_PROMPTS_FILE)
        print("priority_prompts has prompts")
    elif GENERAL_PROMPTS_FILE in bucket_files and not check_aws_empty_file(GENERAL_PROMPTS_FILE):
        available_prompts = get_available_prompts(GENERAL_PROMPTS_FILE)
        print("general_prompts has prompts")
    else:
        create_aws_s3_file(GENERAL_PROMPTS_FILE)
        available_prompts = get_available_prompts(GENERAL_PROMPTS_FILE)

    reddit = bot_login()
    recent_prompts = get_recent_prompts(reddit, NUMBER_OF_DAYS)

    new_prompt = generate_new_promp(available_prompts)
    if new_prompt in recent_prompts:
        collisions = 0
        while collisions <= MAX_PROMPT_CHECKS:
            new_prompt = generate_new_promp(available_prompts)
            if new_prompt not in recent_prompts:
                break
            else:
                collisions += collisions

    date_today = get_date_today()
    print(new_prompt)
    title = config.reddit_submission_prefix + ' for ' + date_today + '--' + new_prompt
    reddit.subreddit(config.reddit_subreddit).submit(title, selftext='', send_replies=False)


def get_recent_prompts(reddit, NUMBER_OF_DAYS):
    recent_prompts = []
    old_prompts = []
    post_prefix = config.reddit_submission_prefix

    submissions = reddit.subreddit(config.reddit_subreddit).new(limit=NUMBER_OF_DAYS)
    for post in submissions:
        if post_prefix in post.title and "--" in post.title:
            old_prompts.append(post.title.split("--")[1])
    return recent_prompts
def check_aws_empty_file(file_name):
    aws_s3 = get_aws_s3_session()

    if aws_s3.Bucket(config.aws_s3_bucket_name).Object(file_name).content_length <= 0:
        print(aws_s3.Bucket(config.aws_s3_bucket_name).Object(file_name).content_length)
        return True
    else:
        return False
def get_available_prompts(file_name):
    aws_s3 = get_aws_s3_session()
    prompts = []

    # These 2 lines so single line isn't too long
    file_data = aws_s3.Object(config.aws_s3_bucket_name, file_name)
    file_data = file_data.get()['Body'].read().decode().split()

    for line in file_data:
        prompts.append(line)

    for prompt in prompts:
        print(prompt)
    return prompts
def get_aws_s3_session():
    aws_s3_session = boto3.Session(
        region_name = config.aws_s3_bucket_region,
        aws_access_key_id = config.aws_s3_access_key_id,
        aws_secret_access_key = config.aws_s3_secret_access_key,
    ).resource('s3')
    return aws_s3_session
def get_bucket_files():
    aws_s3 = get_aws_s3_session()
    files_list = []

    s3_object_summary = aws_s3.Bucket(config.aws_s3_bucket_name).objects.all()
    for file in s3_object_summary:
        files_list.append(file.key)
    return files_list
def create_aws_s3_file(file_name):
    aws_s3 = get_aws_s3_session()

    aws_s3.Bucket(config.aws_s3_bucket_name).put_object(Key=file_name)
    return
def bot_login():
    reddit = praw.Reddit(
            username = config.reddit_username,
            password = config.reddit_password,
            client_id = config.reddit_client_id,
            client_secret = config.reddit_client_secret,
            user_agent = config.reddit_user_agent)
    return reddit
def generate_new_promp(prompt_list):
    random_num = random.randint(1, len(prompt_list) - 1)
    return prompt_list[random_num]
def get_date_today():
    today = datetime.today().strftime("%m/%d/%y")
    return
# def store_available_prompts(file_name):
if __name__ == "__main__":
    main()
