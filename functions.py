from csv import reader
from base64 import b64encode

DATA_FILE = "Data.csv"
AGENTS = {"10": "XXXXX", "20": "XXXXX", "30": "XXXXX", "40": "XXXXX", 
        "50": "XXXXX", "60": "XXXXX", "70": "XXXXX", "80": "XXXXX"}

def append_list_as_row(line):
    with open(DATA_FILE, "a") as f:
        f.write(line.replace(",", ";"))
        f.write("\n")

def decoder(name):
    return name[0].decode('utf-8')

def exists_in(number):
    with open(DATA_FILE, mode='r') as csvfile:
        read = reader(csvfile, skipinitialspace=True)
        print(read)
        for row in read:
            if(str(number) in row[0]):
                return True
    return False

def pack_json(ldap_info, ticket_data):

    if("(" in ticket_data[3]):
        subject = "Hovor s agentem - "+AGENTS[ticket_data[3].split("(")[1].replace(")", "")]
        ticketID = ticket_data[3].split("(")[1].replace(")", "")
    else:
        subject = "Chyba subjektu"
        ticketID = ""
    m, s = divmod(int(ticket_data[5]), 60)
    text = "Stav hovoru - {} \nHovor přebehol - {} \nHovor trval - {:02d}:{:02d}".format(ticket_data[8], ticket_data[1], m, s)

    final_json = {
                    "alert": True,
                    "autorespond": False,
                    "source": "API",
                    "name": ldap_info[0],
                    "email": ldap_info[1],
                    "phone": ticket_data[2],
                    "subject": subject,
                    "topicId": "666-"+ticketID,
                    "ip": "123.211.233.122",
                    "message": text,
                }

    return final_json


def data_process(data, apis):
    ticket_data = data.split(",")
    if(not exists_in(ticket_data[0])):
        osticket_data = pack_json(apis[0].search(ticket_data[2]), ticket_data)
        if(ticket_data[11]):
            wav = apis[2].get_wav(ticket_data[11])
            osticket_data['attachments'] = [
                        {"recording.mp3": 'data:mpeg;base64,'+b64encode(wav.read()).decode('UTF-8')},
                    ]
        data += "," + apis[1].post_ticket(osticket_data)
        append_list_as_row(data)  