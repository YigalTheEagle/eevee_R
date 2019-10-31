This tool is still a work in progress, but functions as a begining of an automation framework for IVR penetration testing.

Currently this tool supports two modes:
1. Bruteforcing possible IDs in the IVR system
2. Sending irregular DTMF signals


Once you create a recording of the IVR's response indicating the ID did not match a correct one, and a recording of the IVR's response indicating the ID is the right one (look up in the code wrongID.mp3 and rightID.mp3), it will automatically give you an indication when the recording did not sound like a wrong ID and when it sounded like a right ID.


Feel free to contribute and let me know of any improvements you wish to make
