import time  # time.sleep() <-- Number in seconds
import random
import requests
import json
import scratchattach as scratch
import os
from hugchat import hugchat
from hugchat.login import Login

# Login to Hugging Face and grant authorization to HuggingChat
EMAIL = os.environ['HUGGINGFACEEMAIL']
PASSWD = os.environ['HUGGINGFACEPASSWORD']
cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

# Create ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

session = scratch.login(os.environ['SCRATCH_USERNAME'], os.environ['SCRATCH_PASSWORD'])

studio = session.connect_studio("35801399")
print(studio.comments(limit=1, offset=0))  # Fetches all project comments except for comment replies

message_result = chatbot.chat(os.environ['CHATBOT_START_PROMPT'])
message_str = message_result.wait_until_done()

while True:
    comments = studio.comments(limit=1, offset=0)
    comment_alldata = comments[0]  # Access the first comment in the list
    comment = comment_alldata['content']
    text = "comment: " + comment
    print(text)
    commentid = comment_alldata['id']
    text2 = "comment id: " + str(commentid)
    print(text2)
    
    texttobechecked = "#@"
    if texttobechecked in comment:
        print("Comment Does Contain #@")
        replies = studio.get_comment_replies(comment_id=commentid, limit=40, offset=0)  # Fetches the replies to a specific comment
        print(replies)
        reply_content = [reply['content'] for reply in replies]
        print(reply_content)
        
        texttobecheckedinreply = "/."
        if any(texttobecheckedinreply in reply for reply in reply_content):
            print("Reply Contains /.")
        else:
            print("Reply Does NOT Contain /.")
            # Send the user's message to the chatbot and get the response
            message_result = chatbot.chat(comment)
            message_str = message_result.wait_until_done()
            AIReplyMessage = message_str + " /."
            studio.reply_comment(content=AIReplyMessage, parent_id=commentid, commentee_id=None)
    else:
        print("Comment Does NOT Contain #@")
    time.sleep(5)
