#!/home/tarequeh/lib/python2.5
import sys, os
sys.path = ['/home/tarequeh/webapps/littleebay', '/home/tarequeh/webapps/littleebay/lib/python2.5', '/home/tarequeh/webapps/littleebay/lebay'] + sys.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'lebay.settings'

import datetime
import hashlib

from lebay.apps.lebay.models import AuctionEvent
from lebay.apps.lebay.utils import process_ended_auction

def process_ended_auctions():
    current_time = datetime.datetime.now()
    ended_auctions = AuctionEvent.objects.filter(end_time__lt=current_time, item__status=AUCTION_ITEM_STATUS_RUNNING)
    for auction_event in ended_auctions:
        process_ended_auction(auction_event)

if __name__ == "__main__":
    process_ended_auctions()

