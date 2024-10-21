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

# Correct the URL by adding the scheme
correct_url = "https://huggingface.co/login?next=https%3A%2F%2Fhuggingface.co%2Foauth%2Fauthorize%3Fclient_id%3D8f1a1d63-479b-46c8-84cb-521fe9f3222f%26scope%3Dopenid%2520profile%2520inference-api%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fhuggingface.co%252Fchat%252Flogin%252Fcallback%26state%3DeyJkYXRhIjp7ImV4cGlyYXRpb24iOjE3Mjk1Mjk3Mzg0NzAsInJlZGlyZWN0VXJsIjoiaHR0cHM6Ly9odWdnaW5nZmFjZS5jby9jaGF0L2xvZ2luL2NhbGxiYWNrIn0sInNpZ25hdHVyZSI6ImQwZGU0MDc4ZDMyM2QzNDIyOTk2MjYzYjQ2MTgxN2FiZmFhMzkyZTMyZWQ0MDBlMDgzNzI5MDc1ZmRlM2YwNjcifQ%253D%253D"

# Use the corrected URL in your request
res = requests.get(correct_url, allow_redirects=False)

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
