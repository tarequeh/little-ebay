import datetime
import hashlib

from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import modelformset_factory

from lebay.apps.lebay.forms import UserRegistrationForm, UserLoginForm, SellerProfileForm, ItemForm, AuctionEventForm, BidForm, UserProfileEditForm, PasswordChangeForm, AuctionSearchForm, PaymentForm, SalesForm
from lebay.apps.lebay.models import Seller, AuctionEvent, Item, User, ItemCategory, Sales
from lebay.apps.lebay.constants import AUCTION_EVENT_SORTING_CHOICES, AUCTION_EVENT_SORTING_TITLE, AUCTION_ITEM_STATUS_RUNNING, AUCTION_ITEM_STATUS_IDLE, AUCTION_ITEM_STATUS_SOLD
from lebay.apps.lebay.utils import process_ended_auction

def index(request):
    if request.user.is_authenticated():
        request.session['message'] = ''
        return HttpResponseRedirect(reverse('lebay_user_home'))
    else:
        return HttpResponseRedirect(reverse('lebay_view_auction_events'))

def login_user(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(reverse('lebay_user_home')) 
    else:
        form = UserLoginForm()

    return render_to_response('login.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('lebay_index'))

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('lebay_login'))
    else:
        form = UserRegistrationForm()
    
    return render_to_response('register.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('lebay_user_home')) 
    else:
        form = PasswordChangeForm()

    return render_to_response('lebay/change_password.html', {
        'form': form,
    }, context_instance=RequestContext(request))        

@login_required
def edit_user_profile(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('lebay_view_user_profile', args=[user.pk]))
    else:
        form = UserProfileEditForm(instance=request.user.user)
    
    return render_to_response('lebay/edit_user_profile.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def view_user_profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404
        
    return render_to_response('lebay/view_user_profile.html', {
        'user': user,
    }, context_instance=RequestContext(request))

@login_required
def view_user_home(request):
    current_auctions = AuctionEvent.objects.filter(item__seller=request.user.user, item__status=AUCTION_ITEM_STATUS_RUNNING)
    won_auctions = AuctionEvent.objects.filter(winning_bidder=request.user.user, item__status=AUCTION_ITEM_STATUS_SOLD)
    listable_items = Item.objects.filter(seller=request.user.user, status=AUCTION_ITEM_STATUS_IDLE)
    
    return render_to_response('lebay/view_user_home.html', {
        'current_auctions': current_auctions,
        'won_auctions': won_auctions,
        'listable_items': listable_items,
    }, context_instance=RequestContext(request))

@login_required
def edit_seller_profile(request):
    if request.user.user.is_seller():
        seller = Seller.objects.get(user=request.user.user)
    else:
        seller = Seller(user=request.user.user, paypal_email=request.user.email)
        seller.save()

    if request.method == 'POST':
        form = SellerProfileForm(data=request.POST, instance=seller)
        if form.is_valid():
            seller = form.save()
            return HttpResponseRedirect(reverse('lebay_user_home')) 
    else:
        form = SellerProfileForm(instance=seller)

    return render_to_response('lebay/seller_profile.html', {
        'form': form,
    }, context_instance=RequestContext(request))        

@login_required
def view_item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        raise Http404

    item_locked = False
    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        item_locked = True
    
    return render_to_response('lebay/view_item_detail.html', {
        'item': item,
        'item_locked': item_locked
    }, context_instance=RequestContext(request))

@login_required
def edit_item(request, item_id):
    try:
        item = Item.objects.get(pk=item_id, seller=request.user.user)
    except Item.DoesNotExist:
        raise Http404
    
    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        return HttpResponseRedirect(reverse('lebay_view_item_detail', args=[item.pk]))

    if request.method == 'POST':
        item_form = ItemForm(data=request.POST, instance=item)
        
        if item_form.is_valid():
            saved_item = item_form.save()
            return HttpResponseRedirect(reverse('lebay_view_item_detail', args=[saved_item.id])) 
    else:
        item_form = ItemForm(instance=item)
    
    return render_to_response('lebay/edit_item_detail.html', {
        'item_form': item_form,
    }, context_instance=RequestContext(request))

@login_required
def list_item(request):
    try:
        seller_profile = Seller.objects.get(user=request.user.user)
    except Seller.DoesNotExist:
        return HttpResponseRedirect(reverse('lebay_create_seller_profile') + '?next=%s' % reverse('lebay_list_item'))
    
    if request.method == 'POST':
        item_form = ItemForm(data=request.POST, seller=request.user.user)
        auction_form = AuctionEventForm(data=request.POST)
        
        if item_form.is_valid() and auction_form.is_valid():
            item = item_form.save()
            auction_event = auction_form.save(item=item)
            return HttpResponseRedirect(reverse('lebay_view_auction_event', args=[auction_event.id])) 
    else:
        item_form = ItemForm()
        auction_form = AuctionEventForm(initial={'shipping_method': seller_profile.default_shipping_method, 'shipping_detail': seller_profile.default_shipping_detail, 'payment_detail': seller_profile.default_payment_detail})

    return render_to_response('lebay/list_item.html', {
        'item_form': item_form,
        'auction_form': auction_form
    }, context_instance=RequestContext(request))        

@login_required
def list_existing_item(request, item_id=None):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        raise Http404

    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        auction_event = AuctionEvent.objects.get(item=item)
        return HttpResponseRedirect(reverse('lebay_view_auction_event', args=[auction_event.pk]))

    if request.method == 'POST':
        auction_form = AuctionEventForm(data=request.POST)
        if auction_form.is_valid():
            auction_event = auction_form.save(item=item)
            return HttpResponseRedirect(reverse('lebay_view_auction_event', args=[auction_event.pk])) 
    else:
        auction_form = AuctionEventForm()

    return render_to_response('lebay/list_existing_item.html', {
        'item': item,
        'auction_form': auction_form
    }, context_instance=RequestContext(request))        

def view_categories(request):
    categories = ItemCategory.objects.all()
    return render_to_response('lebay/view_categories.html', {
        'categories': categories,
    }, context_instance=RequestContext(request))        

def view_category(request, category_id):
    try:
        category = ItemCategory.objects.get(pk=category_id)
    except ItemCategory.DoesNotExist:
        raise Http404
    
    auction_events = AuctionEvent.objects.get_current_auctions().filter(item__category=category)
    auction_paginator = Paginator(auction_events, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        auction_page = auction_paginator.page(page)
    except (EmptyPage, InvalidPage):
        auction_page = auction_paginator.page(post_paginator.num_pages)
    
    return render_to_response('lebay/view_category.html', {
        'category': category,
        'auction_page': auction_page,
    }, context_instance=RequestContext(request))        

def search_auction_events(request):
    if request.method == 'POST':
        form = AuctionSearchForm(data=request.POST)
        if form.is_valid():
            matching_auctions = form.search()
            return render_to_response('lebay/display_search_results.html', {
                'matching_auctions': matching_auctions,
            }, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(reverse('lebay_view_auction_events'))
    else:
        return HttpResponseRedirect(reverse('lebay_view_auction_events'))

@login_required
def view_auction_event(request, auction_event_id=None):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = BidForm(data=request.POST, auction_event=auction_event, bidder=request.user.user)
        if form.is_valid():
            bid = form.save()
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = BidForm(initial={'amount': auction_event.get_current_price() + Decimal('0.01')})
    
    return render_to_response('lebay/view_auction.html', {
        'form': form,
        'auction_event': auction_event
    }, context_instance=RequestContext(request))

@login_required
def view_ended_auction_event(request, auction_event_id=None):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404
    
    if not auction_event.is_running():
        process_ended_auction(auction_event)

    return render_to_response('lebay/view_ended_auction.html', {
        'auction_event': auction_event
    }, context_instance=RequestContext(request))

def view_auction_events(request):
    try:
        auction_events = AuctionEvent.objects.get_current_auctions().filter(~Q(item__seller=request.user.user))
    except Exception, e:
        auction_events = AuctionEvent.objects.get_current_auctions()

    if request.GET:
        sort_by = request.GET.get('sort_by', '')
        if sort_by not in AUCTION_EVENT_SORTING_CHOICES:
            sort_by = AUCTION_EVENT_SORTING_TITLE
        auction_events = auction_events.order_by(dict(AUCTION_EVENT_SORTING_CHOICES)[sort_by])
    auction_paginator = Paginator(auction_events, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        auction_page = auction_paginator.page(page)
    except (EmptyPage, InvalidPage):
        auction_page = auction_paginator.page(post_paginator.num_pages)
    
    return render_to_response('lebay/view_auctions.html', {
        'auction_page': auction_page
    }, context_instance=RequestContext(request)) 

@login_required
def view_bid_history(request, auction_event_id):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404
    
    bids = auction_event.bids.all()
    if bids.count():
        highest_bid = auction_event.bids.order_by('-amount')[0]
    else:
        highest_bid = None

    return render_to_response('lebay/view_bid_history.html', {
        'auction_event': auction_event,
        'highest_bid': highest_bid,  
        'bids': bids,
    }, context_instance=RequestContext(request))

@login_required
def pay_for_item(request, auction_event_id):
    try:
        auction_event = AuctionEvent.objects.get(pk=auction_event_id)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if auction_event.winning_bidder == request.user.user:
        if not auction_event.is_paid():
            if request.method == 'POST':
                form = PaymentForm(request.POST)
                if form.is_valid():
                    invoice_hash = hashlib.md5()
                    invoice_hash.update(str(auction_event.pk) + str(auction_event.winning_bidder.pk))
                    
                    sale_record = Sales()
                    sale_record.auction_event = auction_event
                    sale_record.invoice_number = invoice_hash.hexdigest()
                    sale_record.save()
                    return HttpResponseRedirect(reverse('lebay_user_home'))
            else:
                form = PaymentForm()

            return render_to_response('lebay/pay_for_item.html', {
                'form': form,
                'auction_event': auction_event
            }, context_instance=RequestContext(request))
        else:
            return render_to_response('error.html', {
                'title': 'Payment Error',
                'summary': "You have already paid for this item.",
            }, context_instance=RequestContext(request))
    else:
        return render_to_response('error.html', {
            'title': 'Payment Error',
            'summary': "You are trying to pay for an item you didn't win.",
        }, context_instance=RequestContext(request))

@login_required
def manage_payments(request):
    sales = Sales.objects.filter(auction_event__item__seller=request.user.user)
    sales_formset = []
    if request.method == "POST":
        forms_are_valid = True
        for sale in sales:
            sale_form = SalesForm(data=request.POST, instance=sale, prefix=sale.pk)
            if sale_form.is_valid():
                sale_form.save()
                return HttpResponseRedirect(reverse('lebay_manage_payments'))
    else:
        for sale in sales:
            sale_form = SalesForm(instance=sale, prefix=sale.pk)
            sales_formset.append({'sale': sale, 'form': sale_form})
    return render_to_response("lebay/manage_payments.html", {
        'sales_formset': sales_formset,
    }, context_instance=RequestContext(request))
