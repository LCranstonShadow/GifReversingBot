import praw.exceptions
import prawcore.exceptions
from core import constants as consts
from core.context import CommentContext
# from core.gif import Gif as GifObject
from core.hosts import Gif as NewGifObject
from random import randrange
# from core.credentials import CredentialsLoader
#
# credentials = CredentialsLoader().get_credentials()


def reply(context: CommentContext, gif):
    # If we have a gif, use it's data. Else, use info from context
    if isinstance(gif, NewGifObject):
        url = gif.url
        nsfw = gif.nsfw or context.nsfw
    else:
        url = gif
        nsfw = context.nsfw

    comment = context.comment

    reverse_flag = randrange(0, 3000) == 0 and not context.unnecessary_manual and not context.distinguish and not nsfw
    # if comment.author.name == credentials['general']['operator']:
    #     print("Hi", credentials['general']['operator'])
    #     reverse_flag = True

    # Assemble prefixing messages
    message = url
    if context.unnecessary_manual:
        message = message + consts.unnecessary_manual_message

    # Format and send the reply
    try:
        if nsfw:
            comment = comment.reply(consts.nsfw_reply_template.format(message))
        else:
            if reverse_flag:
                comment = comment.reply(consts.reply_reverse_template.format(message[::-1], message))
            else:
                comment = comment.reply(consts.reply_template.format(message))
        if context.distinguish:
            comment.mod.distinguish(sticky=True)

        print("Successfully reversed and replied!")
    except praw.exceptions.APIException as err:
        error = vars(err)
        if err.error_type == "RATELIMIT":
            errtokens = error['message'].split()
            print("Oops! Hit the rate limit! Gotta wait " + errtokens[len(errtokens) - 2] + " " + errtokens[
                len(errtokens) - 1])
    except prawcore.exceptions.Forbidden:
        # Probably banned, message the gif to them
        comment.author.message(consts.reply_ban_subject, consts.reply_ban_template.format(url))
        print("Successfully reversed and messaged!")
