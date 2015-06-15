from __future__ import division
import urllib2, threading, sys, json, csv


unique_pages = 0
url_map = {
	"Mercury": "http://localhost:8000/api/v1/article?random&titleOnly&_=1433175328355",
	"MediaWiki": "http://community.agleeson.wikia-dev.com/api.php?action=query&generator=random&grnnamespace=0&format=json",
	"MediaWiki_alt": "http://community.agleeson.wikia-dev.com/api.php?action=query&list=random&rnnamespace=%5B0%2C12%5D&rnlimit=1&format=json",
	"Production":  "http://muppet.wikia.com/api/v1/article?random&titleOnly&_=1433175328355"
	}
hashset = set()
batch_size = 25
repeats = dict()
response_headers = list()

json1_file = open('headers.json')
json1_str = json1_file.read()
request_headers = json.loads(json1_str)

def printError(str):
	print 'Error: ' + str + '\n'

if len( sys.argv ) != 3 :
	printError("Please enter an API and # of calls\nUsage: python random_api_test.py [API name] [# calls]")
	exit()

if sys.argv[1] not in url_map.keys():
	printError("Invalid API name. Allowed names: " + ', '.join(url_map.keys()))
	exit()

if not sys.argv[2].isdigit():
	printError("Number of calls must be a positive integer")
	exit()

total_calls = int(sys.argv[2])
api = sys.argv[1]


num_batches = total_calls//batch_size

url = url_map[api]

def crawl():
	global unique_pages
	request_headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
				'Cache-Control': 'max-age=0' }
	req = urllib2.Request(url, headers=request_headers)
	try:
		response = urllib2.urlopen( req )
		response_header = response.info()
		data = json.loads(response.read())
	except:
		print 'Error'

	response_headers.append(response_header)
	

	#print data

	title = extractTitle(data)

	#print '\t' + title

	if title not in hashset:
		unique_pages += 1
		hashset.add(title)
	else:
		if(title in repeats):
			repeats[title] += 1
		else:
			repeats[title] = 1


def extractTitle(data):
	title = ""

	if isinstance(data, dict):
		for key, val in data.iteritems():
			if key == 'title':
				title = val
				break
			elif isinstance(val, dict):
				title = extractTitle(val) if title == "" else title
			elif isinstance(val, list):
				title = extractTitle(val) if title == "" else title
	else:
		for val in data:
			title = extractTitle(val) if title == "" else title

	return title



threads = []

print '\nRandom Page Numerical Analysis\n'

if total_calls - batch_size*num_batches == 0:
	print 'Running ' + `num_batches` + " batches of " + `batch_size` + " calls for a total of " + `total_calls` + " calls."
else:
	print 'Running ' + `num_batches` + " batches of " + `batch_size` + " calls plus one batch of " + `total_calls - batch_size*num_batches` + " calls for a total of " + `total_calls` + " calls."

print "\nURL: " +  url + "\n"

for b in range(num_batches):
	sys.stdout.write("\rWaiting for batch #" + `b+1` + " / " + `num_batches`)

	for n in range(batch_size):
		thread = threading.Thread(target=crawl)
		thread.start()

		threads.append(thread)

	for thread in threads:
		thread.join()

	#print "Complete."
	sys.stdout.flush()



for n in range(total_calls - batch_size*num_batches):
	thread = threading.Thread(target=crawl)
	thread.start()

	threads.append(thread)

	sys.stdout.write("\rWaiting for remainder batch")

	for thread in threads:
		thread.join()

	#print "Complete."
	sys.stdout.flush()

print "\n\nRESULTS:"
print "============================="
print "For " + `total_calls` + " calls, the " + api + " API returned " + `unique_pages` + " unique pages"
print "Uniques/total: " + `unique_pages/total_calls`

if len(repeats) > 0:
	print "\nRepeated pages:"
	for key, val in repeats.iteritems():
		print "\t" + key + ": " + `val`


cacheHits = 0
cacheMisses = 0
f = open('response_headers.txt','w')
f.seek(0)
f.truncate()

keys = response_headers[0].keys()
keys.sort()

for header in response_headers:
	for key in keys:
		if(header.getheader(key)):
			f.write(key + ": " + header.getheader(key) + "\n")
	f.write("\n")
	if header.getheader('X-Cache') == 'MISS, MISS':
		cacheMisses += 1
	else:
		cacheHits += 1

print "Cache Hits: " + `cacheHits`
print "Cache Misses: " + `cacheMisses`

f.close() # you can omit in most cases as the destructor will call if
