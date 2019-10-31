#!/usr/bin/env python3
from flask import Flask, request, jsonify
import nexmo
from pprint import pprint
import librosa
from dtw import dtw
from numpy.linalg import norm
import os


client = nexmo.Client(application_id='PUT APPLICATION ID HERE',private_key='PUT PRIVATE KEY HERE',) # make sure to place your nexmo appID and private key here
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
def sending_strings_for_convo_uuid(convo_uuid):
    for x in ConvoArr[convo_uuid]['strings_to_send']:
        whateverr = client.send_dtmf(ConvoArr[convo_uuid]['uuid'], digits=x)
    return 'pow'

@app.route("/nexmo/api/answering/<string:personal_id>")
def answer_call(personal_id):
    ConvoArr[request.args.get('conversation_uuid')]={"uuid":request.args.get('uuid'),"personal_id":personal_id}
    ncco = [{"action": "input", "eventUrl": ["http://PUT_API_ADDRESS_HERE/nexmo/api/send_id"], "name": "waiting", "timeOut": 3},{"action": "record","eventUrl": ["http://PUT_API_ADDRESS_HERE/nexmo/api/recordings/id"], "name": "send_record","timeOut":4}]
    print("Started call for ID: "+personal_id)
    return jsonify(ncco)


@app.route("/nexmo/api/answering_strings/<string:strings_to_send>")
def sending_abcd(strings_to_send):
    ConvoArr[request.args.get('conversation_uuid')] = {"uuid": request.args.get('uuid'), "strings_to_send": strings_to_send}
    timeoutseconds=len(strings_to_send)/3
    ncco = [
        {"action": "input", "eventUrl": ["http://PUT_API_ADDRESS_HERE/nexmo/api/send_strings"], "name": "waiting", "timeOut": timeoutseconds},
        {"action": "record", "eventUrl": ["http://PUT_API_ADDRESS_HERE/nexmo/api/recordings/strings"], "name": "send_record",
         "timeOut": 10}]
    return jsonify(ncco)

@app.route("/nexmo/api/send_id", methods=['POST'])
def sending_id():
    data = request.get_json()
    sending_id_for_convo_uuid(data['conversation_uuid'])
    return "I wish I was a little bit taller"

@app.route("/nexmo/api/send_strings", methods=['POST'])
def sending_strings():
    data = request.get_json()
    sending_strings_for_convo_uuid(data['conversation_uuid'])
    return "I wish I was a baller"

@app.route("/nexmo/api/recordings/<string:functionality>", methods=['POST'])
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
                os.rename(fileName,"check_these/special_check/"+new_file_name)
                print("The ID " +ConvoArr[data['conversation_uuid']]['personal_id'] + " sounds like the right ID recording!!!!")
            else:
                os.rename(fileName, "check_these/" + new_file_name)
        else:
            os.rename(fileName, "supposed_to_be_garbage/" + "maybe_garbage" + fileName)
    if(functionality=='strings'):
        f = open("Sent_Strings_" + ConvoArr[data['conversation_uuid']]['strings_to_send'] + ".mp3", 'wb+')
        f.write(a_record)
        f.close()
    return "I wish I had a girl, that looked good, I would call her"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

