import praw
import re
import datetime


# Add your app details (https://www.reddit.com/prefs/apps/)
def reddit_login():
    return praw.Reddit(client_id='',
                       client_secret='',
                       password='',
                       user_agent='',
                       username='')


# Creates a poll on poll_sub
def create_poll(poll_sub, title, celebs_list_cleaned, reddit):
    poll = poll_sub.submit_poll(
        title,
        selftext="",
        options=celebs_list_cleaned,
        duration=3  # Change poll duration here
    )

    poll.mod.lock()
    self_text = poll.selftext

    return poll, self_text[self_text.index('(') + 1: self_text.index(')')]


# Checks whether the title contains a battle
def is_battle(title):
    return " vs" in title.lower() or "," in title.lower() or " and " in title.lower() or " or " in title.lower()


def draw_line(character):
    print(character * 50)


def log_it(submission):
    print(f"Title: {submission.title}")
    print(f"Subreddit: {submission.subreddit}")
    print(f"Author: {submission.author}")
    print(f"Submission id: {submission}")
    

def clean_title(title):
    title = title.lower()
    title = title.replace(",", " vs ")
    title = title.replace(" and ", " vs ")
    title = title.replace(" or ", " vs ")

    if ":" in title:
        title = title[title.index(":") + 1:]

    # remove text inside parenthesis
    title = re.sub(r'\([^)]*\)', '', title)

    celebs_list = title.split(" vs")
    celebs_list_cleaned = [celebs.replace(".", "").lstrip().rstrip().title() for celebs in celebs_list]
    return celebs_list_cleaned


def main():
    reddit = reddit_login()
    print("Logged in: " + str(datetime.datetime.now()))
    allowed_subs = [''] # Add subs where you want the bot to run
    
    # Flairs
    voting_open_flair = ''  # Create a flair and add the id here

    subreddit = reddit.subreddit('+'.join(allowed_subs))
    poll_sub = reddit.subreddit('')  # Add the subreddit where polls will be created 
    count = 0

    try:
        for submission in subreddit.new(limit=20):
            # Process posts only if they have no flair
            if submission.link_flair_text:
                continue

            # This block checks whether the title contains a valid separator
            if not is_battle(submission.title):
                comment = submission.reply("Removed rule [xx]: Title must contain a vs")
                comment.mod.distinguish(sticky=True)
                submission.mod.remove()
                draw_line('-')
                print("Removed rule [3b]: Title does not contain a valid separator")
                log_it(submission)
                draw_line('-')
                continue

            # This block checks whether the title contains more than one ":"
            if submission.title.lower().count(":") > 1:
                comment = submission.reply("Removed rule x: Title contains more than one ':'")
                comment.mod.distinguish(sticky=True)
                submission.mod.remove()
                draw_line('-')
                print("Removed rule 3: Title contains more than one ':'")
                log_it(submission)
                draw_line('-')
                continue

            title = submission.title
            celebs_list_cleaned = clean_title(title)

            # This block removes the post if the celeb count is more than 15
            if len(celebs_list_cleaned) > 6:
                comment = submission.reply("Too many celebs. Max 6 allowed")
                comment.mod.distinguish(sticky=True)
                submission.mod.remove()
                print("Too many celebs")
                continue

            # This block checks if the title has any additional text
            addtional_text_flag = False
            for celeb in celebs_list_cleaned:
                if len(celeb.split(" ")) > 3 and submission.subreddit == 'CelebBattles':
                    comment = submission.reply(
                        "Removed rule [xx].\n\nIt appears you have additional text in your title.\n\nIf you feel this was an error, contact the mods")
                    comment.mod.distinguish(sticky=True)
                    submission.mod.remove()
                    draw_line('-')
                    print("removed rule [3e] - additional text")
                    log_it(submission)
                    draw_line('-')
                    addtional_text_flag = True
                    break
            if addtional_text_flag:
                continue

            # create poll
            poll_post_link, poll_link = create_poll(poll_sub, title, celebs_list_cleaned, reddit)

            if poll_link is None:
                raise Exception('None response returned when creating poll link')

            poll_post_link.reply(
                f"Poll for [{submission.title}](https://reddit.com/{submission}) on {submission.subreddit}")

            response = f"Vote here: {poll_link}\n\n---\n\n^^I'm ^^a ^^bot. ^^This ^^action ^^was ^^performed ^^automatically."
    
            comment = submission.reply(response)
            comment.mod.distinguish(sticky=True)
            submission.flair.select(voting_open_flair)
            count += 1

            draw_line('*')
            print(f"Count: {count}")
            print(f"Response: {poll_link}")
            log_it(submission)
            draw_line('*')
            
    except Exception as e:
        draw_line('!')
        print(f"EXCEPTION: {e}")
        draw_line('!')


main()
