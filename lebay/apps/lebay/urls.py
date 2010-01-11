from django.conf.urls.defaults import url, patterns, include
from lebay.apps.lebay import views as lebay_views

urlpatterns = patterns('',
    url(r'^$', lebay_views.index, name='lebay_index'),
    url(r'^home/$', lebay_views.view_user_home, name='lebay_user_home'),
    url(r'^register/$', lebay_views.register_user, name='lebay_register_user'),
    url(r'^login/$', lebay_views.login_user, name='lebay_login'),
    url(r'^logout/$', lebay_views.logout_user, name='lebay_logout'),
    url(r'^search/$', lebay_views.search_auction_events, name='lebay_search_auction_events'),
    
    url(r'^categories/$', lebay_views.view_categories, name='lebay_view_categories'),
    url(r'^categories/(?P<category_id>\d+)/$', lebay_views.view_category, name='lebay_view_category'),
    
    url(r'^item/sell/$', lebay_views.list_item, name='lebay_list_item'),
    url(r'^item/buy/$', lebay_views.view_auction_events, name='lebay_view_auction_events'),
    url(r'^item/(?P<item_id>\d+)/view/$', lebay_views.view_item, name='lebay_view_item_detail'),
    url(r'^item/(?P<item_id>\d+)/edit/$', lebay_views.edit_item, name='lebay_edit_item_detail'),
    url(r'^item/(?P<item_id>\d+)/sell/$', lebay_views.list_existing_item, name='lebay_list_existing_item'),
    url(r'^item/auction/(?P<auction_event_id>\d+)/$', lebay_views.view_auction_event, name='lebay_view_auction_event'),
    url(r'^item/auction/(?P<auction_event_id>\d+)/ended/$', lebay_views.view_ended_auction_event, name='lebay_view_ended_auction_event'),
    url(r'^item/auction/(?P<auction_event_id>\d+)/bids/$', lebay_views.view_bid_history, name='lebay_view_bid_history'),    
    url(r'^item/auction/payments/(?P<auction_event_id>\d+)/pay/$', lebay_views.pay_for_item, name='lebay_pay_for_item'),
    url(r'^item/auction/payments/manage/$', lebay_views.manage_payments, name='lebay_manage_payments'),
    
    url(r'^profile/password/change/$', lebay_views.change_password, name='lebay_change_password'),
    url(r'^profile/user/edit/$', lebay_views.edit_user_profile, name='lebay_edit_user_profile'),
    url(r'^profile/user/(?P<user_id>\d+)/$', lebay_views.view_user_profile, name='lebay_view_user_profile'),
    url(r'^profile/seller/create/$', lebay_views.edit_seller_profile, name='lebay_create_seller_profile'),
    url(r'^profile/seller/edit/$', lebay_views.edit_seller_profile, name='lebay_edit_seller_profile'),
)
