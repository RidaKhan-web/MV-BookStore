import os, sys ,json, collections,requests
from flask import Flask, request,jsonify,g
from pymessenger import Bot
#from goodreads import client

import goodreads_api_client as gr
from bs4 import BeautifulSoup


from tokens import *
#from app import *


client = gr.Client(developer_key=GOODREADS_DEVELOPERKEY)
bot = Bot(PAGE_ACCESS_TOKEN)




class GoodReads:

    @classmethod
    def Retrieve_book_id(cls,index,booklist):
        goodread_id=str(booklist[int(index)-1]['id'])
        return goodread_id

    @classmethod
    def searchbytitle(cls,title,User_id):
         booktitles = []
         books = client.search_book(title, 'title')

         response_result = books['results']['work']
         bot.send_text_message(User_id,'CLOSEST BOOK MATCH FOUND ON GOODREADS.')
         max_length = 5 if len(response_result) > 5 else len(response_result)
         for value in range(0, max_length):
                 booktitle ={
                       'title': response_result[value]['best_book']['title'],
                       'id':response_result[value]['best_book']['id']['#text']
                     }
                 booktitles.append(booktitle)
                 count=value+1
                 bot.send_text_message(User_id,'ENTER '+str(count)+' TO SELECT:\n'+str(booktitle['title']))
         return booktitles




    @classmethod
    def get_reviews_by_book_id(cls,book_id,User_id):

            book = client.Book.show(book_id)
            review_widget = book['reviews_widget']
            review_holder = BeautifulSoup(review_widget, 'html.parser')
            review_url = review_holder.find('iframe')
            r = requests.get(review_url['src'])
            response_html = r.text
            review_page = BeautifulSoup(response_html, 'html.parser')
            all_div = review_page.findAll('div')
            reviews = []

            for div in all_div:
                if 'gr_review_text' in div.get('class', []):
                    reviews.append(div)
            return reviews

    @classmethod
    def get_book_name(cls,book_id):
        book = client.Book.show(book_id)
        book_name = book['title']
        return book_name
