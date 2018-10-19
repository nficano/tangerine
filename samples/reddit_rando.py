# -*- coding: utf-8 -*-
"""
    reddit rando (comment)
    ~~~~~~~~~~~~~~~~~~~~~~

    Get a random comment from a given subreddit.

    # Sample usage:

    import reddit_rando as reddit
    from tangerine import Tangerine

    tangerine = Tangerine('xoxb-your-key-here')

    @tangerine.listen_for('rando comment')
    def rando(user, message):
        subreddit = message.replace('rando comment', '').strip()
        ok, comment = reddit.get_random_comment_in_subreddit(subreddit)
        if not ok:
            return 'oh hamburgers. {0}'.format(comment)
        return comment

    if __name__ == '__main__':
        tangerine.run()
"""
import random

import requests


def get_posts_in_subreddit(subreddit):
    url = 'https://www.reddit.com/r/{0}/.json'.format(subreddit)
    ok, res = reddit_request(url)
    if not ok:
        yield
    for child in res.get('data', {}).get('children', []):
        if child['data']['num_comments'] == 0:
            continue
        permalink = child.get('data', {}).get('permalink')
        url = 'https://www.reddit.com{0}.json'.format(permalink)
        yield url


def get_comments_in_post(url):
    ok, res = reddit_request(url)
    if not ok:
        yield
    for comment in res[1].get('data', {}).get('children', []):
        body = comment.get('data', {}).get('body', '').strip()
        if len(body) < 800 and 'http' not in body:
            yield body


def get_random_comment_in_subreddit(subreddit):
    urls = [url for url in get_posts_in_subreddit(subreddit)]
    if not urls:
        return False, 'no posts.'
    url = random.choice(urls)
    comments = [c for c in get_comments_in_post(url)]
    if not comments:
        return get_random_comment_in_subreddit(subreddit)
    return True, random.choice(comments)


def reddit_request(url):
    resp = requests.get(
        url, headers={
            'User-agent': 'darwin:slackbot:v1.2.3 (by /u/nficano)',
        },
    )
    if not resp.ok:
        return False, resp
    return True, resp.json()


if __name__ == '__main__':
    subreddit = 'mildlyinteresting'
    ok, comment = get_random_comment_in_subreddit(subreddit)
    if ok:
        print(comment)
