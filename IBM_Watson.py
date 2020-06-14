import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pymessenger import Bot

from Book_GoodReads import GoodReads
from tokens import *
#from app import *

bot = Bot(PAGE_ACCESS_TOKEN)


class NLPService:

    authenticator = IAMAuthenticator(IBM_WATSON_API_KEY)
    service = NaturalLanguageUnderstandingV1(
       authenticator=authenticator,
       version='2020-06-13'
    )
    service.set_service_url(IBM_WATSON_API_URL)

    @classmethod
    def get_sentiments(cls,review):
        response = cls.service.analyze(
            text=review,
            features=Features(sentiment=SentimentOptions()),
            language='en',
        ).get_result()
        return response


    @classmethod
    def Review_analysis(cls,book_id,User_id):
        reviews=GoodReads.get_reviews_by_book_id(book_id,User_id)
        bookname=GoodReads.get_book_name(book_id)
        review_count=len(reviews)
        scores = {
            'negative': 0,
            'positive': 0
        }
        for review in reviews:
            score = NLPService.get_sentiments(review.text)
            if score['sentiment']['document']['label'] == 'positive':
                scores['positive'] += 1
            elif score['sentiment']['document']['label'] == 'negative':
                scores['negative'] += 1
        is_recommended = scores['positive'] >= scores['negative']

        if is_recommended:
            response = 'Based on GoodReads Reviews and IBM WATSON Semantic Analysis, The book "'+bookname+'" With GoodReads ID:"'+book_id+'" is recommended for you.'
        else:
            response =  'Based on GoodReads Reviews, The book "'+bookname+'" With GoodReads ID:"'+book_id+'" is NOT recommended for you.'
        bot.send_text_message(User_id,response)
