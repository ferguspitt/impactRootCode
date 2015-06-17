lstoflists=[[strng,strng],strng,["another","string"]]
strng='peterString'
tple=('peterTple',0)
dct={'peterDct':lst}





with open(filesLocation+'compiledResults.csv','w') as csvfile:
    outputWriter=csv.writer(csvfile)
    lst=['Domain','Citations']
    outputWriter.writerow(lst) 
    for domain in rank[0]:
        outputWriter.writerow(domain)
csvfile.close

for story in rank[1].keys():
    with open(filesLocation+story+'Results.csv','w') as csvSubFile:
        outputWriter=csv.writer(csvSubFile)
        lst=['Domain','Citations']
        outputWriter.writerow(lst)  
        for domain in rank[1][story]:
            
            outputWriter.writerow(domain)
    csvfile.close


