#!/usr/bin/env python
# -*- coding: utf-8 -*-

gConfig = {
    "PROXY_SERVER" : "http://opliruqi.appspot.com/",
    #proxy without any content rewrite, to fetch IP blocked sites
    "PROXY_SERVER_SIMPLE" : "westchamberproxy.appspot.com",
    "BLOCKED_DOMAINS_URI" : "https://raw.github.com/liruqi/kernet/stable/Scripts/timeout.txt",
    "REMOTE_DNS" : "168.95.1.1",
    "SKIP_LOCAL_RESOLV" : True,
    "REDIRECT_DOMAINS": {
        "plus.url.google.com":"url",
        "plus.url.google.com.hk":"q|url"
    },
    #feed back slow down proxy, if you intend to improve this proxy, uncomment following line
    #"FEEDBACK_LOG_SERVER" : "http://wcproxy.liruqi.info/",
    "LOCAL_PORT" : 1998,
    "HSTS_DOMAINS" : {
        "developers.facebook.com": 1,
        "www.paypal.com" : 1,
        "www.elanex.biz" : 1,
        "jottit.com" : 1,
        "sunshinepress.org" : 1,
        "www.noisebridge.net" : 1,
        "neg9.org" : 1,
        "riseup.net" : 1,
        "factor.cc" : 1,
        "splendidbacon.com" : 1,
        "aladdinschools.appspot.com" : 1,
        "ottospora.nl" : 1,
        "www.paycheckrecords.com" : 1,
        "market.android.com" : 1,
        "lastpass.com" : 1,
        "www.lastpass.com" : 1,
        "keyerror.com" : 1,
        "entropia.de" : 1,
        "romab.com" : 1,
        "logentries.com" : 1,
        "stripe.com" : 1,
    },
    #collect domains that support HTTPS, to reduce usage of web proxy
    "HSTS_ON_EXCEPTION_DOMAINS" : {
        "s.ytimg.com": 1,
        "i1.ytimg.com": 1,
        "i2.ytimg.com": 1,
        "i3.ytimg.com": 1,
        "i4.ytimg.com": 1,
        "i1.tdimg.com": 1,
        "i2.tdimg.com": 1,
        "i3.tdimg.com": 1,
        "i4.tdimg.com": 1,
        "bits.wikimedia.org": 1,
        "www.wikipedia.org": 1,
        "www.google-analytics.com": 1,
        "www.google-analytics.com": 1,
        "facebook.com": 1,
        "www.facebook.com": 1,
        "apps.facebook.com": 1,
        "graph.facebook.com": 1,
        "www.youtube.com": 1,
        "twitter.com": 1,
        "api.twitter.com": 1,
    }
}
