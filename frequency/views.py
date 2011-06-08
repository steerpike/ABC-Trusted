# Create your views here.
from django.template import RequestContext
from django.shortcuts import render_to_response

def list(request):
    
    return render_to_response('frequency/list.html', 
                              {}, 
                              context_instance=RequestContext(request))