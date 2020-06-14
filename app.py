import os, sys ,json, collections,requests
from flask import Flask, request,jsonify,g
from pymessenger import Bot


from IBM_Watson import NLPService
from Book_GoodReads import GoodReads
from tokens import *



app= Flask(__name__)

bot = Bot(PAGE_ACCESS_TOKEN)


#Global Variables:
Conversation_Flow="0"
User_id='0'
sender_id='0'
booklist=[]
flow='0'

@app.route('/', methods=['GET'])
def verify():
    #Webhook Verification
    if request.args.get("hub.mode")=="subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token")==VERIFY_TOKEN:
            return "Verification token mismtch", 403
        return request.args["hub.challenge"], 200

    return "MV-BookStore By Rida Khan", 200


@app.route('/', methods=['POST'])
def webhook():
    global sender_id
    global User_id
    global Conversation_Flow
    global booklist
    global flow

    data= request.get_json()
    #log(data)
    if data['object'] == 'page':

        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                        #This condition ensures the message is from sender to application.
                        if 'text' in messaging_event['message'] and 'app_id' not in messaging_event['message']:
                            recieved_message=messaging_event['message']['text']
                            sender_id=messaging_event['sender']['id']
                            recipient_id= messaging_event['recipient']['id']

                            if User_id=='0' and flow=='0': #This condition ensure it is new user or new session
                            #retrieving user_name
                                Greet()

                            else:
                                if User_id==sender_id:

                                      #If User has already been Greeted and needs to be asked about the search options.
                                    if flow=='1':
                                        booklist=[] #refreshing previous booklist
                                        getChoice(recieved_message)


                                    #If User enters Book Title.
                                    elif flow=='2a':
                                        booklist=GoodReads.searchbytitle(recieved_message,User_id) #Getting top 5 books list and asking to select
                                        set_Conversation_Flow('3')
                                        
                                        #If User enters Book GoodReads ID.
                                    elif flow=='2b':
                                        if recieved_message.isnumeric():
                                            NLPService.Review_analysis(recieved_message,User_id) #Retrieving Reviews and IBM Analysis
                                            exitsearch()
                                        else:
                                            bot.send_text_message(User_id,'Please enter valid GoodReads ID')



                                    elif flow=='3': #User selects from given 5 titles
                                        if recieved_message.isnumeric() and (int(recieved_message)>=1 and int(recieved_message)<=5):
                                            book_id=GoodReads.Retrieve_book_id(recieved_message,booklist) #Retriving GoodReads ID from title
                                            NLPService.Review_analysis(book_id,User_id) #Retrieving Reviews and IBM Analysis
                                            exitsearch()

                                        else:
                                            bot.send_text_message(User_id,'Please Enter valid input and Select Book from the list of 1-5.')
                            flow=Conversation_Flow


    return "ok", 200



def Greet():
    global sender_id
    global User_id
    global Conversation_Flow
    #fixing the current user. User_id doesnt change till the end of cycle.
    User_id=sender_id
    #Retrieving Username from Facebook Graph API.
    graphurl='https://graph.facebook.com/'+User_id+'?access_token='+PAGE_ACCESS_TOKEN
    userinfo=requests.get(graphurl)
    data=userinfo.json()
    if 'first_name' in data:
        firstname=data['first_name']
        messaging_text='Hello '+firstname+'!!'
        bot.send_text_message(User_id,messaging_text)

        #Sending Message to Greet and Ask for choices between Search bty Title or Search By GoodReads ID:
    bot.send_text_message(User_id,'May I know how do you want to search your book?')
    bot.send_text_message(User_id,'Enter 1 to Search by BookTitle.')
    bot.send_text_message(User_id,'Enter 2 to Search by GoodReads ID.')
    set_Conversation_Flow('1')




def getChoice(recieved_message):
    global sender_id
    global User_id
    global Conversation_Flow
    #if he selects search by book title:
    if recieved_message=='1':
        msg="Please Enter Book Title."
        bot.send_text_message(User_id,msg)
        set_Conversation_Flow('2a')



    #if he selects search by book GoodReads Book ID:
    elif recieved_message=='2':
        bot.send_text_message(User_id,"Please Enter GoodReads Book ID.")
        set_Conversation_Flow('2b')



    #Invalid Input:
    else:
        bot.send_text_message(User_id,'Enter 1 to Search by BookTitle.')
        bot.send_text_message(User_id,'Enter 2 to Search by GoodReads ID.')


def exitsearch():
    global Conversation_Flow
    global User_id
    bot.send_text_message(User_id,'It was great helping you.!! Enter any key to continue searching!!')
    User_id='0'
    set_Conversation_Flow('0') #TO INITIATE NEXT SEARCH







def get_Conversation_Flow():
    global Conversation_Flow
    return Conversation_Flow

def set_Conversation_Flow(val):
    global Conversation_Flow
    Conversation_Flow=val


def log(message):
    print(message)
    sys.stdout.flush()



if __name__ == "__main__":
    app.run(debug= True, port =80)
