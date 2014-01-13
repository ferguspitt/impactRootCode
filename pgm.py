
'''
You'll need to change these values

Feel free to use this code. If you do, I'd be thrilled to hear what you're using it for. Drop me a line at fergus@fergle.com .  If you include a credit, well that'd be lovely.

'''

header1Type='From'
header1Value='yourname@domain.tld'
filesLocation=''


import urllib2 
import html5lib
import re
from bs4 import BeautifulSoup 
import time
from urlparse import urlparse
import operator
from datetime import datetime
import csv

#some data to munch on

storyList=[{'Syrian Civil War': {'wikipages': ['Syrian_civil_war',
    'Timeline_of_the_Syrian_civil_war_(January-April_2013)',
    'Casualties_of_the_Syrian_Civil_War']}},
 {'Obamacare': {'wikipages': ['Patient_Protection_and_Affordable_Care_Act',
    'Affordable_Health_Care_for_America_Act',
    'Constitutional_challenges_to_the_Patient_Protection_and_Affordable_Care_Act']}},
 {'US Government Shutdown': {'wikipages': ['United_States_federal_government_shutdown_of_2013',
    'Government_shutdown_in_the_United_States',
    'United_States_debt-ceiling_crisis_of_2013']}},
 {'Edward Snowden': {'wikipages': ['Global_surveillance_disclosure',
    'Edward_Snowden',
    'PRISM_(surveillance_program)']}},
 {'Boston Marathon Bombing': {'wikipages': ['Boston_Marathon_bombings',
    '2013_Boston_Marathon',
    'Dzhokhar_and_Tamerlan_Tsarnaev']}},
 {'Nelson Mandela Death': {'wikipages': ['Death_and_state_funeral_of_Nelson_Mandela',
    'Nelson_Mandela',
    'Makgatho_Mandela']}},
 {'Pope Francis': {'wikipages': ['Pope_Francis',
    'Theology_of_Pope_Francis',
    'Coat_of_arms_of_Pope_Francis']}},
 {'George Zimmerman Trial': {'wikipages': ['State_of_Florida_v._George_Zimmerman',
    'George_Zimmerman',
    'Shooting_of_Trayvon_Martin']}},
 {'US Economy': {'wikipages': ['Economy_of_the_United_States',
    'Economy_of_the_United_States_by_sector',
    'Economic_history_of_the_United_States']}},
 {'Egypt Coup': {'wikipages': ['Anti-Coup_Alliance',
    '2013_Egyptian_coup_d\'%E9tat',
    'Islamist_protests_in_Egypt_(July_2013%E2%80%93present)']}}]






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
            fh=open(filesLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'HTTPError = ' + str(e.code))
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'HTTPError'
        except urllib2.URLError, e:
            fh=open(filesLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'URLError = ' + str(e.reason))
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'URLError'
        except httplib.HTTPException, e:
            fh=open(filesLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'HTTPException')
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'HTTPException'
        except Exception:
            import traceback
            fh=open(filesLocation+'RequestFailures.log','a')
            fh.write('\n at '+str(datetime.now())+', From: '+compiledURL+'\n'+'generic exception: ' + traceback.format_exc())
            fh.close()
            i=i+1
            time.sleep(2)
            data=''
            print 'exception'
    print "called: "+ compiledURL;
    return data



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
                        webcitationLog=open(filesLocation+'badcitationLog.log','a')
                        problemcite=str(link.get('href'))+' triggered this citation condition from:'+str(citation)
                        webcitationLog.write(topicURL+'\n')
                        webcitationLog.write(problemcite)
                        webcitationLog.write('\n\n')
                        webcitationLog.close()
                       # print 'citation used an archive service'
                    else:
                        #print 'more than two links, we\'re choosing: '+str(link)
                        leftoverLog=open(filesLocation+'SelectionFromArchive.log','a')
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
    URLLog=open(filesLocation+'URLLog.log','a')
    URLLog.write('\n\n\n\n'+topicURL+' at:')
    timestamp = str(datetime.now())
    URLLog.write(timestamp+'\n\n')
    URLDict['NumberOfURLs']=len(URLDict['ExternalURLs'])
    # get the unique domains.
    uniqueDomains={}
    checkDomainCount=0
    for URL in URLDict['ExternalURLs']:
        URLLog.write(URL+'\n')
        domain =''
        #checkeddomain =''
        parsed_uri = urlparse(URL)
        domain = '{uri.netloc}'.format(uri=parsed_uri).replace('www.','') #hey look, we're getting rid of the www. This may not be smart.
        #start normalizing domains with multiple brands, could do by calling then scraping HTML for canonical URLs, but it's bandwidth & processor intensive, not OK for private budget.
        #potentially contentious decision: businessweek being aggregated with bloomberg, Al Jazeeras America and English being aggregated, nbc + msn varients
        
        if domain=='':
                print 'top: '+URL     
        if domain[-12:] =='.abcnews.com' or re.search('abc(\w*).go.com',domain):
            rollLog=open(filesLocation+'abcnewsRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='abcnews.com'        
        if 'http://www.google.com/hostednews/afp/' in str(URL):
            rollLog=open(filesLocation+'afpRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='afp.com'
        if domain in ['aljazeera.net'] or domain[-14:] =='.aljazeera.com':
            rollLog=open(filesLocation+'alJazzRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='aljazeera.com'
        if 'http://www.google.com/hostednews/ap/' in str(URL) or domain[-7:]=='.ap.org': #this captures some 'hosted' URLs
            rollLog=open(filesLocation+'apRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='ap.org'
        if domain[-17:] =='.baltimoresun.com':
            rollLog=open(filesLocation+'baltimoreSunRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='baltimoresun.com'
        if domain in ['bbc.co.uk','news.bbc.co.uk','bbcnews.co.uk','bbcnews.com']:
            rollLog=open(filesLocation+'bbcRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='bbc.co.uk'
        if domain in ['boston.com'] or domain[-16:] =='.bostonglobe.com':
            rollLog=open(filesLocation+'bostonGlobeJazzRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='bostonglobe.com'
        if domain[-16:] == 'businessweek.com':
            rollLog=open(filesLocation+'BloombergRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='bloomberg.com'
        if domain[-13:] =='.cbslocal.com': 
            rollLog=open(filesLocation+'cbsRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='cbsnews.com'
        if domain[-8:]=='.cnn.com': 
            rollLog=open(filesLocation+'cnnRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='cnn.com'
        if domain[-11:]=='.forbes.com':
            rollLog=open(filesLocation+'forbesRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='forbes.com'
        if domain[-7:]=='.ft.com':
            rollLog=open(filesLocation+'ftRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='ft.com'
        if domain in ['guardian.co.uk','theguardian.co.uk','theguardiannews.com','guardiannews.com','theguardian.com','m.guardiannews.com']:#deliberately verbose: there are copycat guardian brands.
            rollLog=open(filesLocation+'guardianRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='theguardian.com'
        if domain[-12:] == '.latimes.com':
            rollLog=open(filesLocation+'latimesRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='latimes.com'
        if domain in ['msnbc.msn.com','msnbcmedia.msn.com'] or domain[-12:] == '.nbcnews.com' or re.search('nbc(\w*).com',domain): #too greedy?
            rollLog=open(filesLocation+'nbcRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='nbcnews.com'
        if domain[-12:]== '.nytimes.com':
            rollLog=open(filesLocation+'nytimesRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='nytimes.com'
        if domain[-8:] == '.npr.org': 
            rollLog=open(filesLocation+'nprRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='npr.org'
        if domain[-12:]=='.reuters.com':
            rollLog=open(filesLocation+'reutersRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='reuters.com'
        if domain[-20:]=='.orlandosentinel.com':
            rollLog=open(filesLocation+'orlandosentinelUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='orlandosentinel.com'
        if domain[-16:]=='.telegraph.co.uk':
            rollLog=open(filesLocation+'telegraphRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='telegraph.co.uk'
        if domain[-13:]=='.usatoday.com':
            rollLog=open(filesLocation+'usaTodayRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='usatoday.com'
        if domain[-15:]=='.news.yahoo.com':
            rollLog=open(filesLocation+'yahooRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='news.yahoo.com'
        if domain[-19:]=='.washingtonpost.com':
            rollLog=open(filesLocation+'washingtonpostRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='washingtonpost.com'
        if domain[-8:]=='.wsj.com':
            rollLog=open(filesLocation+'wsjRollUpLog.log','a')
            rollLog.write(str(URL)+':\n'+domain+'\n\n')
            rollLog.close()
            domain='wsj.com'
        else:
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




#Given a Wikipedia URL, we can now get the footnotes in a dictionary






def runIt(Stories):    
    topStoryFootnotes=[]
    for story in Stories: 
        key=story.keys()[0]
        keyDict={key:{}}
        for wikipage in story[key]['wikipages']:
            #topStoryFootnotes[story]={'results'={key=wikipage}}

            results = extractFootNotes('http://en.wikipedia.org/wiki/'+wikipage) #maybe change this to simply take and pass the full wikipedia URL
            keyDict[key][wikipage]=results
        topStoryFootnotes.append(keyDict)
    return topStoryFootnotes


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
        #storyDomains[story]=sorted(topDomainsByStory[story].items(), operator.itemgetter(1), reverse=True)
    
    sorted_Domains = sorted(topDomains.items(), key=operator.itemgetter(1), reverse=True) 

    return sorted_Domains, storyTopDomainsSorted


smallData=runIt(storyList)
rank=countOverAllDomains(smallData)

#write out a Master List
with open(filesLocation+'compiledResults.csv','w') as csvfile:
    outputWriter=csv.writer(csvfile)
    lst=['Domain','Citations']
    outputWriter.writerow(lst) 
    for domain in rank[0]:
        outputWriter.writerow(domain)
csvfile.close

#write out files for each story
for story in rank[1].keys():
    with open(filesLocation+story+'Results.csv','w') as csvSubFile:
        outputWriter=csv.writer(csvSubFile)
        lst=['Domain','Citations']
        outputWriter.writerow(lst)  
        for domain in rank[1][story]:            
            outputWriter.writerow(domain)
    csvfile.close








