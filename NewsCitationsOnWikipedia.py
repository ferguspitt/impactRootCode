# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

header1Type='From'
header1Value='name@place.edu'
dataLocation='***YOURPLACE***/data/'
outputLocation='***YOURPLACE***/outputs/'
logsLocation='***YOURPLACE***/logs/'

# <codecell>

%pylab inline
import urllib2 
import html5lib
import json
import re
from bs4 import BeautifulSoup 
import time
from urlparse import urlparse
import operator
from datetime import datetime
import csv
import matplotlib.pyplot as plt

# <codecell>



def getPage(compiledURL,headerType,headerValue):
    ''' This function calls a URL. It relies on a number of global variables being set: header1Type, header1Value, filesLocation'''
    request = urllib2.Request(compiledURL)
    request.add_header(headerType,headerValue)
    i=0
    while i<4:
        try: 
            response = urllib2.urlopen(request)
            headers = response.info()
            data = response.read()
            i=4
        except urllib2.HTTPError, e:
            fh=open(logsLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'HTTPError = ' + str(e.code))
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'HTTPError'
        except urllib2.URLError, e:
            fh=open(logsLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'URLError = ' + str(e.reason))
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'URLError'
        except httplib.HTTPException, e:
            fh=open(logsLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'HTTPException')
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'HTTPException'
        except Exception:
            import traceback
            fh=open(logsLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'generic exception: ' + traceback.format_exc())
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'exception'
    print "called: "+ compiledURL;
    return data

# <codecell>

def rollUp(endDomain,startDomain,startURL):
    rollLog=open(logsLocation+endDomain+'RollUpLog.log','a')
    rollLog.write(str(startURL)+':\n'+startDomain+'\n\n')
    rollLog.close()
    return endDomain

def extractFootNotes(topicURL):
    topicData=BeautifulSoup(getPage(topicURL,header1Type,header1Value),'html5lib')
    
    Footnotes=[]
    citations=topicData.findAll('span',{'class': re.compile('^citation')})
    # check for common (annoying) archiving sites:
    #print citations
    for citation in citations:
        if len(citation.findAll('a',{'class': re.compile('^external')})) ==1:
            Footnotes.append(citation.findAll('a',{'class':re.compile('^external')})[0])
        else:
            if len(citation.findAll('a',{'class': re.compile('^external')})) >1:
                for link in citation.findAll('a',{'class': re.compile('^external')}):
                    archiveService=['webcitation.org','web.archive.org','archive.is','dx.doi.org']
                    href=str(link.get('href'))
                    if any(x in href for x in archiveService):
                        webcitationLog=open(logsLocation+'badcitationLog.log','a')
                        problemcite=str(link.get('href'))+' triggered this citation condition from:'+str(citation)
                        webcitationLog.write(topicURL+'\n')
                        webcitationLog.write(problemcite)
                        webcitationLog.write('\n\n')
                        webcitationLog.close()
                       # print 'citation used an archive service'
                    else:
                        #print 'more than two links, we\'re choosing: '+str(link)
                        leftoverLog=open(logsLocation+'SelectionFromArchive.log','a')
                        problemcite='Citation has more than two links, we\'re including: '+str(link.get('href'))+'\n from:'+str(citation)
                        leftoverLog.write(topicURL+'\n')
                        leftoverLog.write(problemcite)
                        leftoverLog.write('\n\n')
                        leftoverLog.close()
                        Footnotes.append(link)
    #print Footnotes
    #OK, we should have clean footnotes, now sort them into domains, count them etc.
    URLDict={'ExternalURLs':[]}

    for footnote in Footnotes:
        URL=re.findall(r'href=[\'"]?([^\'" >]+)',str(footnote))
        if URL[0].startswith("http:") == True:
            URLDict['ExternalURLs'].append(URL[0])
    #make it easier to read
    URLDict['ExternalURLs'].sort()
    #count the number of ExternalURLS
    URLLog=open(logsLocation+'URLLog.log','a')
    URLLog.write('\n\n\n\n'+topicURL+' at:')
    timestamp = str(datetime.now())
    URLLog.write(timestamp+'\n\n')
    URLDict['NumberOfURLs']=len(URLDict['ExternalURLs'])
    # get the unique domains.
    uniqueDomains={}
    checkDomainCount=0
    #print URLDict['ExternalURLs']
    for URL in URLDict['ExternalURLs']:
        URLLog.write(URL+'\n')
        domain =''
        #checkeddomain =''
        parsed_uri = urlparse(URL)
        domain = '{uri.netloc}'.format(uri=parsed_uri).replace('www.','') #hey look, we're getting rid of the www. This may not be smart.
        #print 'Raw Domain:' + domain
        if domain=='':
            print 'top: '+URL     
        elif domain[-12:] =='.abcnews.com' or re.search('abc(\w*).go.com',domain):
            domain=rollUp('abcnews.com',domain,URL)
            #print domain
        elif 'http://www.google.com/hostednews/afp/' in str(URL):
            domain=rollUp('afp.com',domain,URL)
            #print domain
        elif domain in ['aljazeera.net'] or domain[-14:] =='.aljazeera.com':
            domain=rollUp('aljazeera.com',domain,URL)
            #print domain
        elif 'http://www.google.com/hostednews/ap/' in str(URL) or domain[-7:]=='.ap.org': #this captures some 'hosted' URLs
            domain=rollUp('ap.org',domain,URL)
        elif domain[-17:] =='.baltimoresun.com':
            domain=rollUp('baltimoresun.com',domain,URL)
        elif domain in ['bbc.co.uk','news.bbc.co.uk','bbcnews.co.uk','bbcnews.com']:
            domain=rollUp('bbc.co.uk',domain,URL)
        elif domain in ['boston.com'] or domain[-16:] =='.bostonglobe.com':
            domain=rollUp('bostonglobe.com',domain,URL)
        elif domain[-16:] == 'businessweek.com':
            domain=rollUp('bloomberg.com',domain,URL)
        elif domain[-13:] =='.cbslocal.com': 
            domain=rollUp('cbsnews.com',domain,URL)
        elif domain[-8:]=='.cnn.com': 
            domain=rollUp('cnn.com',domain,URL)
        elif domain[-11:]=='.forbes.com':
            domain=rollUp('forbes.com',domain,URL)
        elif domain[-7:]=='.ft.com':
            domain=rollUp('ft.com',domain,URL)
        elif domain in ['guardian.co.uk','theguardian.co.uk','theguardiannews.com','guardiannews.com','theguardian.com','m.guardiannews.com']:#deliberately verbose: there are copycat guardian brands.
            domain=rollUp('theguardian.com',domain,URL)
        elif domain[-12:] == '.latimes.com':
            domain=rollUp('latimes.com',domain,URL)
        elif domain in ['msnbc.msn.com','msnbcmedia.msn.com'] or domain[-12:] == '.nbcnews.com' or re.search('nbc(\w*).com',domain): #too greedy?
            domain=rollUp('nbcnews.com',domain,URL)
        elif domain[-12:]== '.nytimes.com':
            domain=rollUp('nytimes.com',domain,URL)
        elif domain[-8:] == '.npr.org': 
            domain=rollUp('npr.org',domain,URL)
        elif domain[-12:]=='.reuters.com':
            domain=rollUp('reuters.com',domain,URL)
        elif domain[-20:]=='.orlandosentinel.com':
            domain=rollUp('orlandosentinel.com',domain,URL)
        elif domain[-16:]=='.telegraph.co.uk':
            domain=rollUp('telegraph.co.uk',domain,URL)
        elif domain[-13:]=='.usatoday.com':
            domain=rollUp('usatoday.com',domain,URL)
        elif domain[-15:]=='.news.yahoo.com':
            domain=rollUp('news.yahoo.com',domain,URL)
        elif domain[-19:]=='.washingtonpost.com':
            domain=rollUp('washingtonpost.com',domain,URL)
        elif domain[-8:]=='.wsj.com':
            domain=rollUp('wsj.com',domain,URL)
        
        #print 'passing domain to checkeddomain'
        checkeddomain=domain
            
        if checkeddomain in uniqueDomains.keys():
            uniqueDomains[checkeddomain]=uniqueDomains[checkeddomain]+1
            URLLog.write('resolves to: '+checkeddomain+'\n')
        else:
            
            uniqueDomains[checkeddomain]=1
            URLLog.write('resolves to: '+checkeddomain+'\n')
    URLLog.close()
    URLDict['uniqueDomains']=uniqueDomains
    URLDict['NumberofUniqueDomains']=len(URLDict['uniqueDomains'])
    for Udomain in uniqueDomains: 
        checkDomainCount=uniqueDomains[Udomain]+checkDomainCount
    URLDict['CheckCount']=checkDomainCount
    if URLDict['CheckCount']!=URLDict['NumberOfURLs']:
        print 'Dropped Footnotes!: URLs Sorted By Domain=' +str(URLDict['CheckCount'])+' but Number of URLs (Raw)= '+str(URLDict['NumberOfURLs'])
    return URLDict['uniqueDomains']

# <codecell>

#Given a Wikipedia URL, we can now get the footnotes in a dictionary
def runIt(Stories):    
    topStoryFootnotes=[]
    for story in Stories['Stories']:
        #print '\n'+story.keys()[0] #debug
        print '.'
        key=story.keys()[0]
        keyDict={key:{}}
        for wikipage in story[key]:
            #topStoryFootnotes[story]={'results'={key=wikipage}}
            #results = extractFootNotes('http://en.wikipedia.org/wiki/'+wikipage) #maybe change this to simply take and pass the full wikipedia URL
            results = extractFootNotes(wikipage) 
            keyDict[key][wikipage]=results
        topStoryFootnotes.append(keyDict)
    return topStoryFootnotes


# <codecell>

# the function that counts the number of citations per domain.
def countOverAllDomains(dataSource):
    topDomains={}
    topDomainsByStory={}
    storyTopDomainsSorted={}
    for story in dataSource:
        topDomainsByStory[story.keys()[0]]={}
        for wikipage in story:
            for domainList in story[wikipage].keys():
                for domain in story[wikipage][domainList].items():
                    if domain[0] not in topDomains.keys():
                        topDomains[domain[0]]=domain[1]
                        
                    else:
                        topDomains[domain[0]]=topDomains[domain[0]]+domain[1]
                    #now make a dictionary for each story
                    if domain[0] not in topDomainsByStory[story.keys()[0]].keys():
                        topDomainsByStory[story.keys()[0]][domain[0]]=domain[1]
                    else:
                        topDomainsByStory[story.keys()[0]][domain[0]]=topDomainsByStory[story.keys()[0]][domain[0]]+domain[1]
        storyTopDomainsSorted[story.keys()[0]]=sorted(topDomainsByStory[story.keys()[0]].items(), key=operator.itemgetter(1), reverse=True)
    
    sorted_Domains = sorted(topDomains.items(), key=operator.itemgetter(1), reverse=True) 

    return sorted_Domains, storyTopDomainsSorted

# <codecell>

def makePie(CSVfile,V,Title):


    source=[]
    citations=[]
    wedgeN=[]
    wedgeL=[]
    clrs=['#003333','#004747','#005B5B','#007070','#008484','#009999','#00ADAD','#00C1C1','#00D6D6','#00EAEA','#00EFFF']
    i=0


    with open(CSVfile,'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            source.append(row[0]+": ("+row[1]+")")
            citations.append(row[1])
    longtail=0
    for n in citations[11:]:
        longtail=longtail+int(n)
    str(longtail)
    wedges=citations[1:11]
    wedges.append(str(longtail))
    labels=source[1:11]
    labels.append('others: ('+str(longtail)+")")
    figure(V, figsize=(10,10))
    plt.pie(wedges,labels=labels,colors=clrs,startangle=90)
    title(Title, fontsize='22')
    savefig(outputLocation+Title+'.svg', bbox_inches='tight')
    savefig(outputLocation+Title+'.png', bbox_inches='tight')
    plt.close()

# <codecell>

#this function goes to the current events portal, and gets wikipedia URLs for only the currently listed topics.
def fetchTopicsInTheNews():
    wikiNewsData=getPage('https://en.wikipedia.org/wiki/Portal:Current_events',header1Type,header1Value)
    currentEventsHTML=BeautifulSoup(wikiNewsData,'html5lib')
    currentEventsTable=''
    pageLinks=[]
    tables = currentEventsHTML.findAll('table')
    for table in tables:
        rows=table.findAll('tr')
        for row in rows:
            if 'Topics in the news' in str(row):
                #print 'found the news table'
                currentEventsTable=table
    for link in currentEventsTable.findAll('a'):
        pageLinks.append('https://en.wikipedia.org'+str(link.get('href')))

    return pageLinks

# <codecell>

#
def byteify(input):
        if isinstance(input, dict):
            return {byteify(key):byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

def loadData(filename):
    with open(dataLocation+filename,'r') as data_file: 
        #storyList=data_file.read()
        
        storyjson = json.load(data_file)

    return byteify(storyjson)

# <codecell>

def getTimeLabel():
    tt=str(time.asctime( time.localtime(time.time()) ))
    return tt[0:10]+" "+tt[-4:]


# <codecell>

#lclStoryDict={}

# <codecell>

def wikiNewsToJson(jsonFile):
    try:
        lclStoryDict=loadData(jsonFile)
        #see whether it has our date
        for item in lclStoryDict['Stories']:
            if getTimeLabel() not in item.keys():
                #print "we don't have the key"
                lclStoryDict['Stories'].append({getTimeLabel():fetchTopicsInTheNews()})
                with open(dataLocation+jsonFile, 'w+') as fp:
                    json.dump(lclStoryDict,fp)
            else:
                print "have the date" #at the moment this structure wastes cycles, because even after it's found the date it keeps cylcing.
    except:
        print 'some kind of failure above'
        with open(dataLocation+jsonFile, 'w+') as fp: #so create/open a file at that location
            json.dump({'Stories':[{getTimeLabel():fetchTopicsInTheNews()}]}, fp)

# <codecell>

def writeOutPuts(inputDict):
    #this processes the data and creates csv and image files. It expects a dictionary in a particular form.
    rank=countOverAllDomains(inputDict)

    #write out a Master List
    with open(outputLocation+'compiledResults.csv','w') as csvfile:
        outputWriter=csv.writer(csvfile)
        lst=['Domain','Citations']
        outputWriter.writerow(lst) 
        for domain in rank[0]:
            outputWriter.writerow(domain)
    csvfile.close
    makePie(outputLocation+'compiledResults.csv',1,'Compiled Results')
    print 'master csv and charts saved'

    #write out files for each story
    i=2
    for story in rank[1].keys():
        
        with open(outputLocation+story+'Results.csv','w') as csvSubFile:
            outputWriter=csv.writer(csvSubFile)
            lst=['Domain','Citations']
            outputWriter.writerow(lst)  
            for domain in rank[1][story]:            
                outputWriter.writerow(domain)
        csvfile.close
        makePie(outputLocation+story+'Results.csv',i,story)
        i=i+1
        print 'csv and charts saved for '+story

# <codecell>

wikiNewsToJson('runningDates.json')
storyDict=loadData('runningDates.json')
#CurrentTopicsDict=loadData('June23Stories.json')

# <codecell>

smallData=runIt(storyDict)

# <codecell>

writeOutPuts(smallData)

# <codecell>


