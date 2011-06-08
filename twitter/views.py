# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
import re
import urllib2
from datetime import datetime
from django.core import serializers
from models import *
import django

def index(request):
    url = get_twitter_search("trusted")
    response = urllib2.urlopen(url)
    json = simplejson.loads(response.read())
    for result in json["results"]:
        tweet = result["text"]
        twittertags = re.findall(r"#(\w+)", tweet)
        users = re.findall(r"@(\w+)", tweet)
        action = None
        twittertags.remove('trusted')
        creator_username = result["from_user"]
        if "add" in twittertags:
            action = "add"
            twittertags.remove('add')
        if "remove" in twittertags:
            action = "remove"
            twittertags.remove('remove')
        for tag in twittertags:
            try:
                tag = TwitterTag.objects.get(hashtag=tag)
            except TwitterTag.DoesNotExist:
                tag = TwitterTag(hashtag=tag)
                tag.save()
            for username in users:
                #get the twitter user details
                if username == "NewtonMark":
                    twit_id = 17615430
                if username == "efa_oz":
                    twit_id = 16997146
                try:
                    person = Person.objects.get(twitter_username=username)
                except Person.DoesNotExist:
                    person = Person(twitter_username=username, twitter_id=twit_id)
                    person.save()
                if action == "add":
                    try:
                        trusted = Trusted.objects.get(trustee=person, creator=creator_username, twittertag=tag)
                    except Trusted.DoesNotExist:
                        trusted = Trusted(trustee=person, creator=creator_username, 
                                     twittertag=tag, tweet_id = result["id_str"], 
                                     date_created=datetime.now())
                        trusted.save()
                if action == "remove":
                    try:
                        trusted = Trusted.objects.get(trustee=person, creator=creator_username, twittertag=tag)
                        trusted.delete()
                    except Trusted.DoesNotExist:
                        pass
                if action == None:
                    try:
                        trusted = Trusted.objects.get(trustee=person, creator=creator_username, twittertag=tag)
                        trusted.delete()
                    except Trusted.DoesNotExist:
                        trusted = Trusted(trustee=person, creator=creator_username, 
                                     twittertag=tag, tweet_id = result["id_str"], 
                                     date_created=datetime.now())
                        trusted.save()
    #all_objects = list(Person.objects.all()) + list(TwitterTag.objects.all()) + list(Trusted.objects.all())
    get_connections()
    trusted = Trusted.objects.select_related()
    data = serializers.serialize('json', trusted)
    return HttpResponse(data)

def tags(request):
    tags = TwitterTag.objects.select_related()
    data = serializers.serialize('json', tags)
    return HttpResponse(data)

def tag(request, tag):
    tag = TwitterTag.objects.select_related().get(hashtag=tag)
    print tag.connection_set.filter(twittertag=tag)
    #data = serializers.serialize('json', tag)
    return HttpResponse(tag)

def get_connections():
    #string = '{"results":[{"from_user_id_str":"37306936","profile_image_url":"http://a3.twimg.com/profile_images/70331252/wild_normal.gif","created_at":"Wed, 11 May 2011 01:16:27 +0000","from_user":"brightcarvings","id_str":"68122262145994752","metadata":{"result_type":"recent"},"to_user_id":null,"text":"make #connection #abc #skos:about=http://en.wikipedia.org/wiki/Australian_Broadcasting_Corporation","id":68122262145994752,"from_user_id":37306936,"geo":null,"iso_language_code":"en","to_user_id_str":null,"source":"&lt;a href=&quot;http://twitter.com/&quot;&gt;web&lt;/a&gt;"}],"max_id":68122262145994752,"since_id":0,"refresh_url":"?since_id=68122262145994752&q=%23connection+from%3Aannabelcrabb+OR+from%3Aabcmarkscott+OR+from%3Alatikambourke+OR+from%3Abrightcarvings","results_per_page":15,"page":1,"completed_in":0.170518,"since_id_str":"0","max_id_str":"68122262145994752","query":"%23connection+from%3Aannabelcrabb+OR+from%3Aabcmarkscott+OR+from%3Alatikambourke+OR+from%3Abrightcarvings"}'
    #url: http://search.twitter.com/search.json?q=%23connection+from%3Aannabelcrabb+OR+from%3Aabcmarkscott+OR+from%3Alatikambourke+OR+from%3Abrightcarvings
    #json = simplejson.loads(string)
    url = get_twitter_search("connection", False)
    response = urllib2.urlopen(url)
    json = simplejson.loads(response.read())
    print json
    label = None
    value = None
    type = None
    key = None
    for result in json["results"]:
        tweet = result["text"]
        twittertags = re.findall(r"(#[^\s]+)", tweet)
        #twittertags = [i  for i in tweet.split() if i.startswith("#")]
        twittertags.remove(u'#connection')
        for hashtag in twittertags:
            hashtag = hashtag.replace(hashtag[0], '')
            if hashtag.find(':') != -1 and hashtag.find('=') != -1:
                machine_tag = hashtag
                parts = machine_tag.split('=')
                value = parts[1]
                keys = parts[0].split(':')
                type = keys[0]
                key  = keys[1]
            else:
                label = hashtag
            if label and type and key and value:
                #print "%s assigned  %s  %s to be %s" % (label, type, key, value)
                try:
                    tag = TwitterTag.objects.get(hashtag=label)
                except TwitterTag.DoesNotExist:
                    tag = TwitterTag(hashtag=label)
                    tag.save()
                connection = Connection(twittertag=tag, type=type, predicate=key, value=value)
                connection.save()

def test(request, tag):
    twittertag = get_object_or_404(TwitterTag, hashtag=tag)
    connections = twittertag.connection_set.all()
    nyt_uri = None
    twitter_uri = "http://search.twitter.com/search.json?q=%23"+tag+"+"
    segments = ""
    for trusted in twittertag.trusted_set.all():
        segments = segments+"from%3A"+trusted.trustee.twitter_username+"+OR+"
    segments = segments[:-4]
    #segments = urllib2.quote(segments)
    twitter_uri = twitter_uri+segments
    for connection in connections:
        if connection.value.find("http://data.nytimes.com/") != -1:
            nyt_uri = connection
    return render_to_response('twitter/tag.html', {'tag': twittertag, 'nyt':nyt_uri, 'twitter_uri':twitter_uri},
                              context_instance=RequestContext(request)) 

def get_twitter_search(tag, get_latest=True):
    people = Person.objects.filter(watched=True)
    domain = "http://search.twitter.com/search.json?" 
    url = "q=%23"+tag+"+"
    segments = ""
    for person in people:
        segments = segments+"from%3A"+person.twitter_username+"+OR+"
    segments = segments[:-4]
    #segments = urllib2.quote(segments)
    url = url+segments
    if get_latest:
        latest = Trusted.objects.order_by('-tweet_id')[0]
        if latest:
            url = url+"&since_id="+str(latest.tweet_id)
    url = domain+url
    return url 