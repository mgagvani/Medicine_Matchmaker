
# Medicine Matchmaker
# By Manav Gagvani and Kiran Donnelly
# For HackTJ 8.0

from flask import Flask, request
from flask import render_template

import csv
import pandas
import geocoder
from math import radians, cos, sin, asin, sqrt

global key #key for the mapbox API
key = "pk.eyJ1IjoibWdhZ3ZhbmkiLCJhIjoiY2tuYzFwazZqMWxzMzJwbzAyeGlraWJzMSJ9.n02A0dYoScrIMsNIs078ug"

global seq

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/signup/',methods=["GET"])
def signup():
    return render_template('signup.html', output="")

def find_matches(email,location,medicines,donor):
    g=open("txt.txt","r+")
    g.write(f"\n find matches text writer init location-{location} \n")
    donor = bool(donor)
    matches = []
    #first find all users with the same medicine
    df = pandas.read_csv("db.csv")
    df["Distance"] = df.apply (lambda row: find_distance(location,str(row["Location"])), axis=1)#add distance column
    #print(df)
    keywords = medicines.split(" ")
    keywords[0] = keywords[0][1:]
    keywords[-1] = keywords[-1][:-1]
    for i in range(len(keywords)):
        keywords[i] = keywords[i].lower()
    print(keywords)
    for keyword in keywords:
        for i,contains in enumerate(df["Medicine(s)"].str.contains(keyword)):
            if contains:
                if donor:
                    if df.iloc[i]["Donor?"] == False: #person is not a donor also
                        matches.append(df.iloc[i])
                elif not donor:
                    if df.iloc[i]["Donor?"] == True: #person is  a donor
                        matches.append(df.iloc[i])

    #print(matches)

#    print(df)

    #for match in matches:
        #match = numpy.array(match)

    matches = sorted(matches,key=lambda l:l[-1], reverse=False)


    if len(matches) < 1:
        matches = ["Sorry, we did not find any matching users."]
    else:
        while matches[0]["Email"] == email:
            del(matches[0])

    g.write(str(matches))
    g.close()
    return matches


@app.route("/register/", methods=["GET", "POST"])
def need_input():
    g=open("txt.txt","r+")
    g.write("need input text writer init \n")
    seq=[]
    matches = [" "]
    for key, value in request.form.items():
        # g.write("key: {0}, value: {1}".format(key, value))
        # g.write("\n")

        seq.append(value)



    if len(seq)==3:
        temp=seq[2]
        del(seq[2])
        seq.append("Recipient")
        seq.append(temp)

    g.write(f"type of seq[0] {type(seq[0])} seq[0]-{seq[0]} \n")

    if len(seq) == 4: #all values filled out
        if seq[2] == "Donor":
            append_user(seq[1],str(seq[0]),f"[{seq[3]}]","True")
            matches = find_matches(seq[1],str(int(seq[0])),f"[{seq[3]}]","True")
        else:
            append_user(seq[1],str(seq[0]),f"[{seq[3]}]","False")
            matches = find_matches(seq[1],str(int(seq[0])),f"[{seq[3]}]","False")
            #put the data inside of matches into a table or something
            #matches is a __ by 4 array

            #can put this in the html but i don't know how to activate it after the submit button gets clicked
            """
            <table>
        {%for row in matches%}
            <tr>
                {%for col in row%}
                    <td>{{col}}</td>
                {%endfor%}
            </tr>
        {%endfor%}
    </table>
            """
    if len(matches) < 1 and seq[2] == "Donor":
        output="Sorry. We did not find any matching recipients. We have entered your information in our database so that it can be used in the future."
    elif len(matches) < 1 and seq[2] == "Recipient":
        output="Sorry. We did not find any matching donors. Check back later to see if anyone has the medicine you want."
    else:
        output = f"The user who most closely matches you is {matches[0]['Email']}. \n The user lives in {matches[0]['Location']},which is only {matches[0]['Distance']} miles away from you. \n Now you can contact the user and find out your pickup/dropoff location!"


    g.write(f" \n length of matches is {len(matches)} \n")
    #if len(matches) < 1:
    #    matches = ["No matches found for you. Sorry :("]

    g.close()
    return render_template('signup.html',seq=seq,output=output)



def find_distance(location1, location2):
    location1 = str(location1)
    location2 = str(location2)
    location2_int = 0
    #location1 = str(int(location1))
    for digit in location2:
        location2_int *=10
        for d in '0123456789':
            location2_int += digit > d
    location2 = str(location2_int)#[:-2]

    g=open("txt.txt","r+")
    g1 = geocoder.mapbox(location1,key=key)
    g.write(f"initialized geocoder 1 loc1-{location1} loc2-{location2} \n")
    bbox1 = g1.bbox
    g.write(f"distance func log bbox1-{bbox1}  \n")
    lat1 = bbox1["northeast"][0] + bbox1["southwest"][0]
    long1 = bbox1["northeast"][1] + bbox1["southwest"][1]

    g2 = geocoder.mapbox(location2,key=key)
    bbox2 = g2.bbox
    g.write(f"distance func log bbox2-{bbox2}  \n")
    lat2 = bbox2["northeast"][0] + bbox2["southwest"][0]
    long2 = bbox2["northeast"][1] + bbox2["southwest"][1]

    R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(long2 - long1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    dist = R * c

    g.write(f"distance func log bbox1-{bbox1} bbox2-{bbox2} dist-{dist} \n")
    g.close()
    return dist



#to add user to csv database
def append_user(email,location,medicines,donor):
    with open("db.csv",mode="a") as db:
        fieldnames = ["Email","Location","Medicine(s)","Donor?"]
        writer = csv.DictWriter(db,fieldnames=fieldnames)

        append_dict = {"Email": email, "Location": int(location), "Medicine(s)": medicines.lower(), "Donor?": str(donor) if type(donor) is not str else donor}
        writer.writerow(append_dict)
#find matching users


