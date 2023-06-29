#!/usr/bin/python

"""
From https://github.com/tumblr/pytumblr/blob/master/interactive_console.py.
Refactored to remove unnecessary extra dependencies and removed console functionality.
"""

from builtins import input
from pprint import pprint

from requests_oauthlib import OAuth1Session


def new_oauth():
    """
    Return the consumer and oauth tokens with three-legged OAuth process and
    save in a yaml file in the user's home directory.
    """

    print(
        "Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps"
    )
    consumer_key = input("Paste the consumer key here: ").strip()
    consumer_secret = input("Paste the consumer secret here: ").strip()

    request_token_url = "http://www.tumblr.com/oauth/request_token"
    authorize_url = "http://www.tumblr.com/oauth/authorize"
    access_token_url = "http://www.tumblr.com/oauth/access_token"

    # STEP 1: Obtain request token
    oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth_session.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")

    # STEP 2: Authorize URL + Response
    full_authorize_url = oauth_session.authorization_url(authorize_url)

    # Redirect to authentication page
    print("\nPlease go here and authorize:\n{}".format(full_authorize_url))
    redirect_response = input("Allow then paste the full redirect URL here:\n").strip()

    # Retrieve oauth verifier
    oauth_response = oauth_session.parse_authorization_response(redirect_response)

    verifier = oauth_response.get("oauth_verifier")

    # STEP 3: Request final access token
    oauth_session = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth_session.fetch_access_token(access_token_url)

    tokens = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "oauth_token": oauth_tokens.get("oauth_token"),
        "oauth_token_secret": oauth_tokens.get("oauth_token_secret"),
    }

    return tokens


if __name__ == "__main__":
    tokens = new_oauth()
    pprint(tokens)
