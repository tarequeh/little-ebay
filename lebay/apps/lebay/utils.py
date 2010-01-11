from lebay.apps.lebay.constants import AUCTION_ITEM_STATUS_SOLD, AUCTION_ITEM_STATUS_EXPIRED

def process_ended_auction(auction_event):
    bid_count = auction_event.bids.count()
    if bid_count:
        auction_event.item.status = AUCTION_ITEM_STATUS_SOLD
        auction_event.item.save()
    else:
        auction_event.item.status = AUCTION_ITEM_STATUS_EXPIRED
        auction_event.item.save()
