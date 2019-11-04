<h1>eevee_r</h1>

<h3>An IVR system automatic penetration testing script </h3>
This tool is still a work in progress, but functions as a beginning of an automation framework for IVR penetration testing.

Currently this tool supports three modes:
1. Bruteforcing possible IDs in the IVR system
2. Sending an ID followed by PINs seperated with a comma, in an attempt to DOS via account lockout / guess the right PIN
3. Sending irregular DTMF signals in order to expose hidden IVR interfaces


Once you create a recording of the IVR's response indicating the ID did not match a correct one, and a recording of the IVR's response indicating the ID is the right one (look up in the code wrongID.mp3 and rightID.mp3), it will automatically give you an indication when the recording did not sound like a wrong ID and when it sounded like a right ID.
</br>
<h1>Installation</h1>

You need to install an MP3 parser in order to use librosa's mfcc module

`apt install ffmpeg`

other than that install the requirements.txt file
</br>
<h1>Usage:</h1>
</br>
You must obtain API keys for nexmo, you can get a free trial with 2 euros balance, which amounts to around 500 calls.
Set the API keys on both the event_api and the calling_and_iterating_IDs. Must be the same to access one another.
</br>
<h3>API endpoint:</h3>
</br>
In order to differentiate between when the IVR system says the ID exists or not, you must first generate both recordings.</br>
You can use the 'enum' module of the client and send two seperate calls against the target IVR system in order to generate both recordings (currently the default is a 4 seconds recording right after the ID was DTMF'd in, might add the ability to change it if this tool proves useful to others). </br>
Make sure to generate a recording with the IVR response of a "wrong id, please try again" and "right id, please type in your PIN" or whatever your IVR target says, so the tool will have both as "wrongID.mp3" and "rightID.mp3". </br>
Once you generate both, you can easily send the tool to bruteforce possible IDs and it will automatically flag all those that did not contain the "wrong ID" response, while also flagging all those that contained the "right ID" response, giving you the ability to enumerate possible IDs.
</br>
</br>

`python event_api.py`

</br>
</br>

<h3>Running the client:</h3>
</br>

`python calling_and_iterating_IDs.py -p [phone-number] -t [test-type, for example enum or dos] -a [api_endpoint] -enumidstart [id_to_start_from] -enumidend [id_to_end_the_iteration]`


</br>

Feel free to contribute and let me know of any improvements you wish to make


