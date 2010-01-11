import datetime
from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.util import ValidationError
from django.contrib.admin import widgets as adminwidgets
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField

from lebay.apps.lebay.models import User, Seller, Item, AuctionEvent, Bid, Sales
from lebay.apps.lebay.constants import AUCTION_ITEM_STATUS_RUNNING

class UserLoginForm(forms.Form):
    username = forms.CharField(label=u'User Name')
    password = forms.CharField(label=u'Password', widget=forms.PasswordInput(render_value=False))

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username', '')
        password = cleaned_data.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                raise ValidationError('This account is disable. Please constact the webmaster.') 
        else:
            raise ValidationError('Wrong username and or password. Try again.') 
        
        return cleaned_data

    def get_user(self):
        username = self.cleaned_data.get('username', '')
        password = self.cleaned_data.get('password', '')
        user = authenticate(username=username, password=password)

        return user

class AuctionSearchForm(forms.Form):
    query = forms.CharField(max_length=200, required=False, label='')
    
    def search(self):
        cleaned_data = self.cleaned_data
        cleaned_query = cleaned_data.get('query', '') 
        if cleaned_query:
            matching_auctions = AuctionEvent.objects.get_current_auctions().filter(Q(item__title__icontains=cleaned_query) | Q(item__description__icontains=cleaned_query))
        else:
            matching_auctions = AuctionEvent.objects.get_current_auctions()
            
        return matching_auctions

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=u'Password', widget=forms.PasswordInput(render_value=False))
    retyped_password = forms.CharField(label=u'Retype Password', widget=forms.PasswordInput(render_value=False))
    zipcode = USZipCodeField()
    phone = USPhoneNumberField()

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'retyped_password',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'zipcode',
            'phone']
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'phone']

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password', '')
        retyped_password = cleaned_data.get('retyped_password', '')
        
        if password != retyped_password:
            raise ValidationError('Password and retyped password didn\'t match.')
        
        return cleaned_data

    def save(self, force_insert=False, force_update=False, commit=True, *args, **kwargs):
        user = super(UserRegistrationForm, self).save(*args, **kwargs)
        password = user.password
        user.set_password(password)
        user.save()
        
        return user

class UserProfileEditForm(forms.ModelForm):
    zipcode = USZipCodeField()
    phone = USPhoneNumberField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'zipcode', 'phone']

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(label=u'Current Password', widget=forms.PasswordInput(render_value=False))
    new_password = forms.CharField(label=u'New Password', widget=forms.PasswordInput(render_value=False))
    retyped_password = forms.CharField(label=u'Retype New Password', widget=forms.PasswordInput(render_value=False))

    def __init__(self, data=None, user=None, *args, **kwargs):
        self.user = user
        super(UserProfileEditForm, self).__init__(data=data, *args, **kwargs)

    def clean_current_password(self):
        cleaned_data = self.cleaned_data
        current_password = cleaned_data.get('current_password', '')
        
        if not self.user.check_password(current_password):
            raise ValidationError('Wrong current password.')
        
        return current_password

    def clean(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get('new_password', '')
        retyped_password = cleaned_data.get('retyped_password', '')

        if len(new_password) == 0 or len(retyped_password) == 0:
            raise ValidationError('Blank password fields.')
        
        if new_password != retyped_password:
            raise ValidationError('New password and retyped password do not match.')
        
        return cleaned_data
        
    def save(self):
        self.user.set_password(new_password)
        return self.user

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['paypal_email', 'default_shipping_method', 'default_shipping_detail', 'default_payment_detail']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'condition', 'category']

    def __init__(self, data=None, seller=None, *args, **kwargs):
        self.seller = seller
        super(ItemForm, self).__init__(data, *args, **kwargs)

    def save(self, force_insert=False, force_update=False, commit=True):
        item = super(ItemForm, self).save(commit=False)
        item.seller = self.seller
        item.save()
        return item

class AuctionEventForm(forms.ModelForm):
    class Meta:
        model = AuctionEvent
        fields = ['shipping_method', 'shipping_detail', 'payment_detail', 'start_time', 'end_time', 'starting_price', 'shipping_fee', 'reserve_price']

    def clean_start_time(self):
        cleaned_data = self.cleaned_data
        cleaned_start_time = cleaned_data.get('start_time')
        if cleaned_start_time < datetime.datetime.now():
            raise ValidationError('Specified time occurs in the past.')
        return cleaned_start_time

    def clean_end_time(self):
        cleaned_data = self.cleaned_data
        cleaned_end_time = cleaned_data.get('end_time')
        if cleaned_end_time < datetime.datetime.now():
            raise ValidationError('Specified time occurs in the past.')
        return cleaned_end_time
    
    def clean(self):
        cleaned_data = self.cleaned_data
        cleaned_start_time = cleaned_data.get('start_time')
        cleaned_end_time = cleaned_data.get('end_time')
        if cleaned_start_time and cleaned_end_time and cleaned_end_time < cleaned_start_time:
            raise ValidationError('End time must be greater than start time.')
        
        cleaned_starting_price = cleaned_data.get('starting_price')
        cleaned_reserve_price = cleaned_data.get('reserve_price')
        if cleaned_starting_price and cleaned_reserve_price and cleaned_reserve_price < cleaned_starting_price:
            raise ValidationError('Reserve price must be higher than starting price.')
        
        return cleaned_data

    def save(self, item=None, force_insert=False, force_update=False, commit=True):
        if not item:
            raise Exception('AuctionEvent save method requires items to be passed in.')
        auction_event = super(AuctionEventForm, self).save(commit=False)
        item.status = AUCTION_ITEM_STATUS_RUNNING
        item.save()
        auction_event.item = item
        auction_event.save()
        return auction_event

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
    
    def __init__(self, data=None, auction_event=None, bidder=None, *args, **kwargs):
        self.auction_event = auction_event
        self.bidder = bidder
        super(BidForm, self).__init__(data, *args, **kwargs)

    def clean_amount(self):
        cleaned_data = self.cleaned_data
        cleaned_amount = cleaned_data.get('amount', Decimal('0.00'))
        if self.auction_event.bids.count():
            if cleaned_amount < self.auction_event.bids.order_by('-amount')[0].amount:
                raise ValidationError('Your bid has to be higher than the current price.')
        return cleaned_amount

    def clean(self):
        cleaned_data = self.cleaned_data
        current_time = datetime.datetime.now()
        if current_time > self.auction_event.end_time:
            raise ValidationError('This auction event has expired.')
        return cleaned_data
    
    def save(self, force_insert=False, force_update=False, commit=True):
        bid = super(BidForm, self).save(commit=False)
        bid.auction_event = self.auction_event
        bid.bidder = self.bidder
        bid.save()
        self.auction_event.winning_bidder = bid.bidder
        self.auction_event.save()
        return bid

class PaymentForm(forms.Form):
    paypal_email = forms.EmailField(label='Enter your PayPal email.')

class SalesForm(forms.ModelForm):
    class Meta:
        model = Sales
        fields = ['payment_status']
