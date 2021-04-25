import praw
import config
import os.path
import random
import boto3
from datetime import datetime

def main():
    NUMBER_OF_DAYS = config.reddit_days_of_recent_prompts
    MAX_PROMPT_CHECKS = config.reddit_max_prompt_checks
    recent_prompts = []
    available_prompts_data = []
    bucket_files = []
    GENERAL_PROMPTS_FILE = 'general_prompts.txt'
    PRIORITY_PROMPTS_FILE = 'priority_prompts.txt'
    file_used = ''

    if os.path.getsize("prompts.txt") <= 0:
        print("prompts.txt file is empty. Stopping program")
        return

    bucket_files = get_bucket_files()

    # Choosing file to use
    if PRIORITY_PROMPTS_FILE in bucket_files and not check_aws_empty_file(PRIORITY_PROMPTS_FILE):
        available_prompts_data = get_s3_available_prompts(PRIORITY_PROMPTS_FILE)
        file_used = PRIORITY_PROMPTS_FILE
    elif GENERAL_PROMPTS_FILE in bucket_files and not check_aws_empty_file(GENERAL_PROMPTS_FILE):
        available_prompts_data = get_s3_available_prompts(GENERAL_PROMPTS_FILE)
        file_used = GENERAL_PROMPTS_FILE
    else:
        local_prompts = get_local_prompts()
        store_available_prompts(GENERAL_PROMPTS_FILE, local_prompts)
        available_prompts_data = get_s3_available_prompts(GENERAL_PROMPTS_FILE)
        file_used = GENERAL_PROMPTS_FILE

    reddit = bot_login()
    recent_prompts = get_recent_prompts(reddit, NUMBER_OF_DAYS)
    new_prompt_data = generate_new_promp(available_prompts_data)

    # Make sure prompt has not been used in a while
    # Or just choose one if taking too long to decide
    if file_used != PRIORITY_PROMPTS_FILE:
        if new_prompt_data.split('||')[0].strip().title() in recent_prompts:
            collisions = 0
            while collisions <= MAX_PROMPT_CHECKS:
                new_prompt_data = generate_new_promp(available_prompts_data)
                if new_prompt_data.split('||')[0].strip().title() not in recent_prompts:
                    break
                else:
                    collisions += 1

    # Prompt now decided
    new_prompt = new_prompt_data.split('||')[0].strip()
    new_prompt_body = get_prompt_body(new_prompt_data)

    date_today = get_date_today()
    title = config.reddit_submission_prefix + ' for ' + date_today + '--' + new_prompt

    reddit.subreddit(config.reddit_subreddit).submit(title, selftext=new_prompt_body, send_replies=False)

    available_prompts_data.remove(new_prompt_data)
    store_available_prompts(file_used, available_prompts_data)
    return

# Helpers methods------------
def get_recent_prompts(reddit, NUMBER_OF_DAYS):
    recent_prompts = []
    post_prefix = config.reddit_submission_prefix

    submissions = reddit.subreddit(config.reddit_subreddit).new(limit=NUMBER_OF_DAYS)
    for post in submissions:
        if post_prefix in post.title and "--" in post.title:
            recent_prompts.append(post.title.split("--")[1].title())
    return recent_prompts
def check_aws_empty_file(file_name):
    aws_s3 = get_aws_s3_session()

    if aws_s3.Bucket(config.aws_s3_bucket_name).Object(file_name).content_length <= 0:
        return True
    else:
        return False
def get_s3_available_prompts(file_name):
    aws_s3 = get_aws_s3_session()
    prompts_data = []

    # These 2 lines so single line isn't too long
    file_data = aws_s3.Object(config.aws_s3_bucket_name, file_name)
    file_data = file_data.get()['Body'].read().decode().split("\n")

    for line in file_data:
        prompts_data.append(line)
    return prompts_data
def get_local_prompts():
    prompt_list = []
    prompt_file = open('prompts.txt', 'r')

    for prompt in prompt_file:
        prompt_list.append(prompt.strip())
    return prompt_list
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
def bot_login():
    reddit = praw.Reddit(
            username = config.reddit_username,
            password = config.reddit_password,
            client_id = config.reddit_client_id,
            client_secret = config.reddit_client_secret,
            user_agent = config.reddit_user_agent)
    return reddit
def generate_new_promp(prompts_data):
    random_num = random.randint(0, len(prompts_data) - 1)
    return prompts_data[random_num]
def get_date_today():
    date_today = datetime.today().strftime("%y/%m/%d")
    return date_today
def get_prompt_body(prompt_data):
    if '||' in prompt_data:
        prompt_body = prompt_data.split('||')[1].strip().replace(r'\n', '\n')
    else:
        prompt_body = ''
    return prompt_body
def store_available_prompts(file_name, prompts):
    prompt_string = ''

    while len(prompts) > 0:
        prompt_string += prompts.pop(0) + '\n'

    prompt_string = prompt_string.strip()

    aws_s3 = get_aws_s3_session()
    aws_object = aws_s3.Object(config.aws_s3_bucket_name, file_name)
    aws_object.put(Body=prompt_string, ContentType='text/plain')
    return
if __name__ == "__main__":
    main()
