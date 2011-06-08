from django.db import models

# Create your models here.
from django.db import models

class Person(models.Model):
    twitter_username = models.CharField(max_length=200)
    twitter_id = models.IntegerField(null=True)
    watched = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "people"
    def __unicode__(self):
        return self.twitter_username

class TwitterTag(models.Model):
    hashtag = models.CharField(max_length=200)
    person = models.ManyToManyField(Person, through='Trusted')
    class Meta:
        verbose_name_plural = "tags"
    def __unicode__(self):
        return self.hashtag
    
class Trusted(models.Model):
    trustee = models.ForeignKey(Person, related_name="trustee")
    twittertag = models.ForeignKey(TwitterTag)
    creator = models.CharField(max_length=200)
    date_created = models.DateField()
    tweet_id = models.IntegerField()
    class Meta:
        verbose_name_plural = "trusted"
    def __unicode__(self):
        return "@%s trusted on #%s by @%s" % (self.trustee.twitter_username, self.twittertag.hashtag, self.creator) 
        
class Connection(models.Model):
     twittertag = models.ForeignKey(TwitterTag)
     #uri = models.CharField(max_length=200)
     type = models.CharField(max_length=200)
     predicate = models.CharField(max_length=200)
     value = models.CharField(max_length=200)
     def __unicode__(self):
        return self.twittertag.hashtag