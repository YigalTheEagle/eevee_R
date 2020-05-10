#!/usr/bin/env python3
from flask import Flask, request, jsonify
import nexmo
from pprint import pprint
import librosa
from dtw import dtw
from numpy.linalg import norm
import urllib.parse
import os
from requests import get
import time



#Implement another 'class' file that will contain all the API endpoint paths, and the application_id and private key of the application




#


client = nexmo.Client(application_id='',private_key='private.key',) # make sure to place your nexmo appID and private key file here
app=Flask(__name__)
ConvoArr={}



API_endpoint = 'http://'+get('https://api.ipify.org').text

def load_files_for_audio_comp(file1):
    y1, sr1 = librosa.load(file1) #change this to the location of the audiofile with the "wrong ID" recording
    return y1,sr1

#This function returns the distance between the signals in the two provided mp3 files. The higher the value, the more different are the signals in the recordings.
def compare_Audio_Files(file1,file2):
    y1,sr1=load_files_for_audio_comp(file1)
    y2,sr2=load_files_for_audio_comp(file2)
    mfcc1 = librosa.feature.mfcc(y1,sr1)
    mfcc2 = librosa.feature.mfcc(y2, sr2)
    distance = lambda x, y: norm(x-y, ord = 1)
    dist, cost, path, what= dtw(mfcc1.T, mfcc2.T,dist=distance)
    return dist

#As the name implies, this function receives a conversation UUID (received from the answering API endpoints), and sends through DTMF the targeted ID number 
def sending_id_for_convo_uuid(convo_uuid):
    for single_digit in ConvoArr[convo_uuid]['personal_id']:
        client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=single_digit)

#As the name implies, this function receives a conversation UUID and sends through DTMF PINS
def sending_pin_for_convo_uuid(convo_uuid,pin):
    for single_digit in pin:
        client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=single_digit)

def sending_strings_for_convo_uuid(convo_uuid):
    for x in ConvoArr[convo_uuid]['strings_to_send']:
        client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=x)

def send_dtmf_for_convo_uuid(convo_uuid,dtmf):
    for single_item in dtmf:
        client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=single_item)

def ncco_create_talk_action(whattosay):
    speech = whattosay.replace("_"," ")
    return {"action":"talk","text":speech}

def ncco_create_record_action_for_length(thelength):
    #Currently, the eventUrl is not dynamic, might need to edit this -- optionally add additional parsing for recording options, for instance comparing with wrong or right FOR EXAMPLE: w5,544363125,r5cwr,w5,1332 (wait 5, input id, record for 5 seconds and compare against wrong + right (cwr), wait 5, input 1332)
    #Additional functionality could be to add if's inside the parameters, or all characters from client side on a single digit, launching conversations to all combinations, comparing their results with one another
    #implement something in the api_endpoint eventurl
    return {"action":"record","eventUrl":[API_endpoint+"/api/recordings/test"],"name":"RecordFor"+thelength,"timeOut":thelength}

def ncco_create_wait_action(ttl):
    #possibly add the ability to create a custom eventUrl
    return {"action":"input","eventUrl": [API_endpoint+"/api/just_waiting"], "name": "waiting", "timeOut":ttl}

def ncco_delimit_string_until_comma(thestring):
    return thestring[0:thestring.index(',')-1]

def ncco_create_this_input(whattosend):
    #possibly add the ability to create a custom eventUrl
    return {"action":"input","eventUrl": [API_endpoint+"/api/send_this/"+urllib.parse.quote(whattosend)], "name": "inserting_this", "timeOut":len(whattosend)/3}

#build parameter should be along the lines of i5,544363125,r5,tthank_you, -- wait 5 seconds, input series of number, record 5 seconds, say thank you
def build_ncco(parameters):
    ncco = []
    loops = parameters.split(",")
    for i in loops:
        if(i[0]=='t' or i[0]=='T'):
            ncco.append(ncco_create_talk_action(i[1:]))
        if(i[0]=='r' or i[0]=='R'):
            ncco.append(ncco_create_record_action_for_length(i[1:]))
        if(i[0]=='w' or i[0]=='W'):
            ncco.append(ncco_create_wait_action(i[1:]))
        if(i[0]=='i' or i[0]=='I'):
            ncco.append(ncco_create_this_input(i[1:]))
    return ncco
        
# R + Num of seconds to record (delimiter is ,)
# : will be a brief pause
# t will be talk, followed by text to speak (delimiter is ,)

#
# ncco = [
#         {"action": "record", "eventUrl": [API_endpoint+"/api/recordings/strings"], "name": "send_record","timeOut": 10},
#         {"action": "input", "eventUrl": [API_endpoint+"/api/send_strings"], "name": "waiting", "timeOut": timeoutseconds},
#         ]
#=================================== API Routes to send data mid conversation ======================================== 

@app.route("/api/send_id", methods=['POST'])
def sending_id():
    data = request.get_json()
    sending_id_for_convo_uuid(data['conversation_uuid'])
    return "Sending"

@app.route("/api/send_strings", methods=['POST'])
def sending_strings():
    data = request.get_json()
    sending_strings_for_convo_uuid(data['conversation_uuid'])
    return "Sending"

@app.route("/api/send_pin/<string:pin>", methods=['POST'])
def sending_pin(pin):
    data = request.get_json()
    sending_pin_for_convo_uuid(data['conversation_uuid'],pin)
    return "Sending"

@app.route("/api/send_this/<string:whattosend>",methods=['POST'])
def sending_this(whattosend):
    data = request.get_json()
    send_dtmf_for_convo_uuid(data['conversation_uuid'],whattosend)
    return "Sending"


#=================================== Recording Functionality API route ==============================

@app.route("/api/recordings/<string:functionality>", methods=['POST'])
def recordings(functionality):
    data=request.get_json()
    a_record=client.get_recording(data['recording_url'])
    if(functionality=='id'):
        functionalityid(data,a_record)
    if (functionality == 'dos'):
        functionalitydos(data,a_record)
    if(functionality=='strings'):
        functionalitystrings(data,a_record)
    if(functionality=='test'):
        functionalitytestrecording(data,a_record)
        
    return "" #can send an ncco object to continue the conversation

#=================================== Recording Functionality Helpers ==============================

def functionalityid(data,a_record):
    fileName="ID_"+ConvoArr[data['conversation_uuid']]['personal_id']+".mp3"
    f=open(fileName,'wb+')
    f.write(a_record)
    f.close()
    try:
        comparedValue=compare_Audio_Files('wrongID.mp3',fileName)
        if(int(comparedValue) > 40000 and int(comparedValue) < 150000): # this will check if the file is different from the wrong ID recording, above 40000 value means the recording contains a different phrase WARNING: will contain false positives due to inconsistency in the phone line
            new_file_name = "Difference_" + str(int(comparedValue)) + "_" + fileName
            print("The ID: "+ConvoArr[data['conversation_uuid']]['personal_id']+" returned a different response, comparing it against the right ID recording")
            try:
                newcomparison=compare_Audio_Files('rightID.mp3',fileName)
                if(int(newcomparison) < 45000):
                    new_file_name = "RightID_Difference_" + str(int(newcomparison)) + "_"+fileName
                    os.rename(fileName,new_file_name)
                    print("The ID " +ConvoArr[data['conversation_uuid']]['personal_id'] + " sounds like the right ID recording!!!!")
                else:
                    os.rename(fileName, new_file_name)
            except:
                print('No rightID recording present')
        else:
            os.rename(fileName, "maybe_garbage" + fileName)
    except:
        print('No WrongID recording present, please listen to current recording to determine if it suits')

def functionalitydos(data,a_record):
    fileName = "DOS_Num_"+ConvoArr[data['conversation_uuid']]["PhoneNumber"]+"_ID_" + ConvoArr[data['conversation_uuid']]['personal_id'] + "_PINS_"+str(ConvoArr[data['conversation_uuid']]["pinArray"])+".mp3"
    f = open(fileName, 'wb+')
    f.write(a_record)
    f.close()
    print("ID: " + str(ConvoArr[data['conversation_uuid']]['personal_id']) + " was DOSed with PINs: " + str(ConvoArr[data['conversation_uuid']]["pinArray"]))

def functionalitystrings(data,a_record):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    f = open("Sent_Strings_To_"+ConvoArr[data['conversation_uuid']]["PhoneNumber"]+"Strings_" + ConvoArr[data['conversation_uuid']]['strings_to_send'] + "_"+ timestr +".mp3", 'wb+')
    f.write(a_record)
    f.close()

def functionalitytestrecording(data,a_record):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    f = open("test-recording"+ConvoArr[data['conversation_uuid']]["PhoneNumber"]+"_At_"+timestr+".mp3", 'wb+')
    f.write(a_record)
    f.close()

    # ============================= call answer functionality API routes =========================

@app.route("/api/testrecording/")
def record_this_call():
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":None,"PhoneNumber":request.args.get("to")}
    ncco = [
        {"action": "record","eventUrl": [API_endpoint+"/api/recordings/test"], "name": "send_record","timeOut":10}
        ]
    print("Started call for recording")
    return jsonify(ncco)


@app.route("/api/answering/<string:personal_id>")
def answer_call(personal_id):
    while(len(str(personal_id))<9):
        personal_id="0"+personal_id
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":personal_id,"PhoneNumber":request.args.get("to")}
    ncco = [
        {"action": "input", "eventUrl": [API_endpoint+"/api/send_id"], "name": "waiting", "timeOut": 3},
        {"action": "record","eventUrl": [API_endpoint+"/api/recordings/id"], "name": "send_record","timeOut":4}
        ]
    print("Started call for ID: "+personal_id)
    return jsonify(ncco)

#============ This is the dynamically Built NCCO ===========

@app.route("/api/buildncco/<string:conversationdata>")
def create_the_ncco_call(conversationdata):
    pprint(conversationdata)
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"PhoneNumber":request.args.get("to")}
    ncco = build_ncco(conversationdata)
    pprint(ncco)
    print("Started call for build NCCO: "+conversationdata)
    return jsonify(ncco)

#===========================================================

@app.route("/api/answering-dos/<string:pins>/<string:personal_id>/")
def answer_all_with_dos(personal_id,pins):
    pinArray=pins.split(",")
    ncco=[
        {"action":"input","eventUrl":[API_endpoint+"/api/send_id"],"name":"waiting","timeOut":3},
        {"action":"record","eventUrl":[API_endpoint+"/api/recordings/dos"],"name":"send_record"}
        ]
    for i in range(0,len(pinArray)):
        ncco.append({"action": "input", "eventUrl": [API_endpoint+"/api/send_pin/" + pinArray[i]],"name":"waiting","timeOut": 5})
                    
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":personal_id,"pinArray":pins,"PhoneNumber":request.args.get("to")}
    ncco.append({"action":"input","eventUrl":[API_endpoint+"/api/just_wait/"],"name":"waiting","timeOut":15})
    
    print("Started DOS call for ID: " + personal_id+", with PINs "+pins)
    return jsonify(ncco)


@app.route("/api/answering_strings/<string:strings_to_send>")
def sending_abcd(strings_to_send):
    
    ConvoArr[request.args.get('conversation_uuid')] = {"uuid": request.args.get('uuid'), "strings_to_send": strings_to_send,"PhoneNumber":request.args.get("to")}
    timeoutseconds=len(strings_to_send)/3
    ncco = [
        {"action": "record", "eventUrl": [API_endpoint+"/api/recordings/strings"], "name": "send_record","timeOut": 10},
        {"action": "input", "eventUrl": [API_endpoint+"/api/send_strings"], "name": "waiting", "timeOut": timeoutseconds},
        {"action": "record", "eventUrl": [API_endpoint+"/api/recordings/strings"], "name": "send_record","timeOut": 10}
        ]
    return jsonify(ncco)

    # ============================= Main =====================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

