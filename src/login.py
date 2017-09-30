import getpass
import logging
import os

from base64 import b64encode
from urlparse import urlparse

import httplib
httplib.HTTPConnection.debuglevel = 0

import requests
# https://urllib3.readthedocs.org/en/latest/security.html#insecurerequestwarning
requests.packages.urllib3.disable_warnings()


def login(username, password):
    logger = logging.getLogger(__name__)

    BUNGIE_SIGNIN_URI = "https://www.bungie.net/en/User/SignIn/Psnid"
    PSN_OAUTH_URI = "https://auth.api.sonyentertainmentnetwork.com/login.do"
    # PSN_OAUTH_URI = "https://auth.api.sonyentertainmentnetwork.com/login.jsp"

    logger.info("Logging in...")

    # Get JSESSIONID cookie.
    # We follow the redirection just in case the URI ever changes.
    get_jessionid = requests.get(BUNGIE_SIGNIN_URI, allow_redirects=True)
    jsessionid0 = get_jessionid.history[1].cookies["JSESSIONID"]
    logger.debug("JSESSIONID: %s", jsessionid0)

    # The POST request will fail if the field `params` isn't present
    # in the body of the request.
    # The value is just the query string of the PSN login page
    # encoded in base64.
    params = urlparse(get_jessionid.url).query
    logger.debug("params: %s", params)
    params64 = b64encode(params)
    logger.debug("params64: %s", params64)

    # Post credentials and pass the JSESSIONID cookie.
    # We get a new JSESSIONID cookie.
    # Note: It doesn't appear to matter what the value of `params` is, but
    # we'll pass in the appropriate value just to be safe.
    post = requests.post(
        PSN_OAUTH_URI,
        data={"j_username": username,
              "j_password": password,
              "params": params64,
              "location": "en"},
        cookies={"JSESSIONID": jsessionid0},
        allow_redirects=False
    )
    print " ------ "
    print post.headers
    print " ------ "
    print post.cookies
    print " ------ "

    if "authentication_error" in post.headers["location"]:
        logger.warning("Invalid credentials")
    jsessionid1 = post.cookies["JSESSIONID"]
    logger.debug("JSESSIONID: %s", jsessionid1)

    # Follow the redirect from the previous request passing in the new
    # JSESSIONID cookie. This gets us the x-np-grant-code to complete
    # the sign-in with Bungie.
    get_grant_code = requests.get(
        post.headers["location"],
        allow_redirects=False,
        cookies={"JSESSIONID": jsessionid1}
    )
    grant_code = get_grant_code.headers["x-np-grant-code"]
    logger.debug("x-np-grant-code: %s", grant_code)

    # Finish our sign-in with Bungie using the grant code.
    auth_cookies = requests.get(BUNGIE_SIGNIN_URI,
                                params={"code": grant_code})

    # Create requests Session.
    session = requests.Session()

    # Save the cookies indicating we've signed in to our session
    session.headers["X-API-Key"] = API_KEY
    session.headers["x-csrf"] = auth_cookies.cookies["bungled"]
    session.cookies.update({
        "bungleatk": auth_cookies.cookies["bungleatk"],
        "bungled": auth_cookies.cookies["bungled"],
        "bungledid": auth_cookies.cookies["bungledid"]
    })


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ul3_logger = logging.getLogger("requests.packages.urllib3")
    ul3_logger.setLevel(logging.WARN)

    username = None
    password = None
    API_KEY = os.environ["BUNGIE_API_KEY"]  # Use Bungie API key in bash profile

    while not username:
        username = raw_input("Enter Username: ")
    while not password:
        password = getpass.getpass("Enter Password: ")

    login(username, password)
