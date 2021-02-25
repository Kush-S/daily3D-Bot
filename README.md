# A Reddit bot for the [/r/daily3D](reddit.com/r/Daily3D) subreddit, made in Python 3.8.1.

This bot uses a list of prompts provided to it, chooses 1 at random, and posts it every time it is run. The bot must be run every time it needs to post a new prompt, for example by AWS Lambda, but the python code can be run locally as well. AWS S3 is required currently, as it uses that for file storage.

To start running this bot on Lambda, copy code from 'main.py', and create 'config.py' and 'prompts.txt' files into it. Lambda needs to use AWS Layers with the [PRAW library](https://praw.readthedocs.io/en/latest/) in it. For your convenience, the praw-aws-layer.zip is provided. You can upload that zip while creating a layer. If running locally and not on Lambda, make sure PRAW is installed locally.

### Services required
* Reddit account with access to post on subreddit you want to post o
* Amazon Web Server IAM account with access to AWS S3
* AWS Lambda, set to run whenever prompt needs to be posted
  - Alternative: Locally run this code manually or on a timer
  - If not running on Lambda, change line #8 of program from
    - def main(event, context): to def main():

---
### File content
* main.py
  - All code from this repository's main.py
* prompts.txt
  - A list of prompts, each on a new line. The prompts will be part of the title. Unless you provide text for the body of the reddit post, the post will be empty inside. To provide the text used in the body, add '||' after the prompt and enter body text.

  - Because prompts and their bodies are imported from a .txt file, markdown can be a bit wonky. Currently tested markdown syntax that work are '\n\n' for new paragraph, \*text\* for italics, and \*\*text\*\* for bold. You can use single quotes ('), slashes (/), and dashes (-), in both the prompt title and body. Example of prompts.txt file:

    ```
    fireworks || Could be a **GIANT** rocket, or *small* fireworks.
    table||Workman's table
    Shooting star
    1950's diner ||Any angle/shot from a diner-or any objects from it.\n\nOr just the whole diner.
    Track/railway|| LONG TRACKS
    ```
* config.py - Contains config information about Reddit and AWS account. These are variables the bot will be using. These are required.
  - reddit_username = 'NULL'
  - reddit_password = 'NULL'
  - reddit_client_id = 'NULL'
  - reddit_client_secret = 'NULL'
  - reddit_user_agent = 'NULL'
  - reddit_subreddit = 'NULL'
  - reddit_submission_prefix = 'NULL'
  - reddit_days_of_recent_prompts = 365
  - reddit_max_prompt_checks = 1000
  - aws_s3_access_key_id = 'NULL'
  - aws_s3_secret_access_key = 'NULL'
  - aws_s3_bucket_region = 'NULL'
  - aws_s3_bucket_name = 'NULL'

### Description of config.py variables
reddit_username, reddit_password, reddit_client_id, reddit_client_secret, and reddit_user_agent are about the details of the Reddit account.

reddit_subreddit is the subreddit that the bot will be posting to. Reddit account being used should have access to this subreddit.

reddit_submission_prefix is the prefix of the post title. We use 'Daily3D' since that is our subreddit name.

Example of daily posts the bot makes using the prefix 'Daily3D':
```
Daily3D for 21/01/30--fireworks
```

reddit_days_of_recent_prompts is how many recent posts from the subreddit this bot needs to pull. This is so prompts aren't repeated too often. For example, setting this to 365 will mean pull the latest 365 posts from the subreddit. This number should be smaller than the total number of prompts in prompts.txt. For example, if there are 5 prompts in prompts.txt, set reddit_days_of_recent_prompts 4 or less.

reddit_max_prompt_checks is how many checks should be made while checking for repeated prompts. This bot will generate a prompt, and it will compare that prompt against the posts it pulled from reddit_days_of_recent_prompts. The bot will compare a maximum of reddit_max_prompt_checks times. If exceeded the reddit_max_prompt_checks, the bot will just post whatever prompt it has currently. Recommended to keep this around 1000. The higher it is, the longer it will take to run.

aws_s3_access_key_id and aws_s3_secret_access_key are the AWS AIM account that needs access to the AWS S3 Bucket for file storage.

aws_s3_bucket_region is the S3 bucket's region.

aws_s3_bucket_name is the name of the bucket this bot will be storing files in
