import os
import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
import getpass
from symbol import except_clause
import time
#just for MAC
#from StdSuites.Type_Names_Suite import null
from bookingCal.ecalendar.models import Entry
from bookingCal.ecalendar.models import Equipment
from bookingCal.ecalendar.models import Guest
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as logout_
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.context_processors import request
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
import ldap
from django.template import RequestContext
import re
from django.utils import simplejson
from django.core import serializers
import string
from time import gmtime, strftime
import smtplib
from email.MIMEText import MIMEText
from django.core.mail import EmailMessage

mnames = "January February March April May June July August September October November December"
mnames = mnames.split()
_email = ""
def reminders(request):
    """Return the list of reminders for today and tomorrow."""
    year, month, day = time.localtime()[:3]
    reminders = Entry.objects.filter(date__year=year, date__month=month,
                                     date__day=day, remind=True)
    tomorrow = datetime.now() + timedelta(days=1)
    year, month, day = tomorrow.timetuple()[:3]
    return list(reminders) + list(Entry.objects.filter(date__year=year, date__month=month,
                                  date__day=day, remind=True))




def main(request, year=None):
    """Main listing years and months; three Year per Page """
    # prev /next years

    if year: year = int(year)
    else:    year = time.localtime()[0]

    nowy, nowm = time.localtime()[:2]
    lst = []

    #create a list of months for each year, indication ones that contain entries and current
    for y in [year, year + 1, year + 2]:
        mlst = []
        for n, month in enumerate(mnames):
            entry = current = False #and there entry for this month ; current mont?
            entries = Entry.objects.filter(date__year=y, date__month=n + 1)

            if entries:
                entry = True
            if y == nowy and n + 1 == nowm:
                current = True
            mlst.append(dict(n=n + 1, name=month, entry=entry, current=current))
        lst.append((y, mlst))
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False

    return render_to_response("ecalendar/index.html", dict(years=lst, year=year,
                              reminders=reminders(request),request=request,context=context), context_instance=RequestContext(request))

def month(request, year, month, change=None,eq=None):
    """Listinng of days in 'month'. """
    year, month = int(year), int(month)
    sort=False
    if change == "sort":
        eq = int(eq)
        sort=True
        print eq
    #apply next/previos change
    if change in ("next", "prev"):

        if change == "next":
            now, mdelta = date(year, month, 1), timedelta(days=31)
            mod = mdelta
        elif change == "prev":
            now, mdelta = date(year, month, 1), timedelta(1)
            mod = -mdelta

        year, month = (now + mod).timetuple()[:2]

        #init variables
    equipname=""
    cal = calendar.Calendar()
    month_days = cal.itermonthdays(year, month)
    nyear, nmonth, nday = time.localtime()[:3]
    lst = [[]]
    week = 0

    #make month lists containing list of days for each week
    #each day tuple will contain list of entries and current indicator
    for day in month_days:
        entries = current = False   #are there entries for this day; curren day?
        if day:
            # entries= Entry.objects.filter(date__year<=year, date__month<=month, date__day<=day, enddate__year>=year, enddate__month>=month, enddate__day>=day)
        # entries= Entry.objects.filter(date__year=year, date__month=month, date__day=day)

            # Zeitangabe erzeugen
            fday = day
            checktime = datetime(year, month, fday)

            if sort:
                equip=Equipment.objects.get(id=eq)
                a = Entry.objects.filter(equipment=equip)
                equipname=equip.name
            else:
                a = Entry.objects.all()
        
            entries = []
            for en in a:
                startdate = datetime(en.date.year, en.date.month, en.date.day)
                enddate = datetime(en.enddate.year, en.enddate.month, en.enddate.day)

                if startdate <= checktime and enddate >= checktime:
                    check = Entry.objects.get(id=en.id)
                    if len(entries) == 3:
                        check.equipment.name = "and more"
                        entries.append(check)
                        break

                    entries.append(check)

            if day == nday and year == nyear and month == nmonth:
                current = True

        lst[week].append((day, entries, current))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    equipment=Equipment.objects.all()
        
    return render_to_response("ecalendar/month.html", dict(year=year,id_eq=eq,month=month, month_days=lst, mname=mnames[month-1],equipmentName=equipname,request=request,context=context,equipment=equipment), context_instance=RequestContext(request))

def day(request, year, month, day, eq=None):
    year, month, day = int(year), int(month), int(day)

    if day:
        fday = day
        checktime = datetime(year, month, fday)

        if eq:
            equip=Equipment.objects.get(id="1")
            a = Entry.objects.filter(equipment=equip)
        else:
           a = Entry.objects.all().order_by('equipment__name')
        entries = []
        for en in a:
            startdate = datetime(en.date.year, en.date.month, en.date.day)
            enddate = datetime(en.enddate.year, en.enddate.month, en.enddate.day)

            if startdate <= checktime and enddate >= checktime:
                check = Entry.objects.get(id=en.id)
                entries.append(check)
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    equipment=Equipment.objects.all()
    return render_to_response("ecalendar/day.html", dict(year=year, month=month, day=day, entries=entries ,request=request,context=context,equipment=equipment), context_instance=RequestContext(request))

def event(request, evid):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    if evid:
        entries = Entry.objects.get(id=evid)

    return render_to_response("ecalendar/event.html", dict(entries=entries ,request=request,context=context), context_instance=RequestContext(request))

def ldapU(request, username, password):
    c = {}
    c.update(csrf(request))
    print request 
    server_uri = 'ldap://ad.dkfz-heidelberg.de:389'

    # if bind_user and bind_pw is both '' it does an anonymous bind
    bind_user = 'CN=ldap,CN=Users,DC=ad,DC=dkfz-heidelberg,DC=de'
    bind_pw = 'logalvsa'

    base_dn = 'OU=Kst-B110,OU=Fsp-B,OU=DKFZ,DC=ad,DC=dkfz-heidelberg,DC=de'
    filter_str = '(CN=%s)'
    searchScope = ldap.SCOPE_SUBTREE
    attrs = ['sAMAccountName', 'displayName', 'mail']
    adUser = username
    adPW = password

    # Probably turn it off for production code.
    if server_uri.startswith('ldaps:'):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

    ldap.set_option(ldap.OPT_REFERRALS, 0)

    print "Initializing connection to %s ..." % server_uri
    l = ldap.initialize(server_uri)
    print "LDAP protocol version %d" % l.protocol_version

    print "Binding to directory using bind user %r (and configured password) ..." % bind_user
    l.bind_s(bind_user, bind_pw)

    search_filter = filter_str % adUser

    print "Searching under base dn %s for %s ..." % (base_dn, search_filter)

    lusers = l.search_s(base_dn, searchScope, search_filter, attrs)
    results = len(lusers)
    print "Results: %d" % results

    ldapIn = False

    if results:
        for dn, ldap_dict in lusers:
            print "    %s" % dn
        first_dn = lusers[0][0]
        print "Trying to authenticate with first found dn %s (and configured password) ..." % first_dn
        try:
            l.bind_s(first_dn, adPW)
            ldapIn = True
            for dn,entry in lusers:
                if dn != None:
                    print 'Processing',repr(dn)
                    print entry['sAMAccountName']
                    print entry['mail']
                    emailad =  entry['mail']
                    fname = entry['displayName']
                    backendAuth(username,fname, emailad)
            print "Succcessfully bound - whoami says: "
        except ldap.INVALID_CREDENTIALS, err:
            print "LDAP Error: %s" % err
        
   
    print "Unbinding from directory ..."
    l.unbind()
    print "-" * 100
    print "\n"

    return ldapIn

def backendAuth(username,name, mail):
    password = '123Secret'
    name[0] = name[0].replace(",","")
    name_list = name[0].split(' ')
    lastname = name_list[0]
    firstname =name_list[1]
    mail = mail
    
    user = authenticate(username=username, password=password)
    if user is not None:
        return
    else:
        lastname.replace(",","")
        user = User.objects.create_user(username, '', password)
        user.first_name = firstname
        user.last_name = lastname
        user.email = mail[0]
        user.groups.add(1)
        user.is_active = True
        user.is_staff = False
        user.save()
        return

def new(request):
    c = {}
    c.update(csrf(request))
    if not request.session.get('ldapU_is_auth'):
        return render_to_response('ecalendar/new.html',c,context_instance=RequestContext(request))
    else:
        return add(request,"")
    
def mail(user, startdate, enddate, starttime, endtime, eqi, type,is_guest):
    print "Mailing recipient"
    print "the email address is"
    print type 
    smtp_server = 'localhost'
    print is_guest
    print eqi
    recipients = user.email
    if is_guest != 0:
        recipients=is_guest.email
	firstname = is_guest.firstname
    else:
        firstname = user.first_name
    print "recipients"
    print recipients
    sender = 'maximilian.koch@dkfz.de'
    if (type=="new"):
        subject = "reservation"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname+",\n " "you have booked "+ eqi +" on "+ startdate + " at "+ starttime +" to "+ enddate +" at "+ endtime+"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have booked "+ eqi +" on "+ startdate + " at "+ starttime +" to "+ endtime+"."
    if (type=="change"):
        subject = "changed"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname +",\n " "you have booked "+ eqi +" on "+ startdate + " at "+ starttime +" to "+ enddate +" at "+ endtime+"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have booked "+ eqi +" on "+ startdate + " at "+ starttime +" to "+ endtime+"."
    if (type=="delete"):
        subject = "deleting"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname +",\n " "you have deleted your booked "+ eqi +" that you have booked on "+ startdate +" to "+ enddate +"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have deleted your booked "+ eqi +" that you have booked on "+ enddate +"."
    msg = MIMEText(msg_text)
    msg['Subject'] = subject
    s = smtplib.SMTP()
    s.connect(smtp_server)
    s.sendmail(sender, recipients, msg.as_string())
    print"send"
    s.close()
def add(request,errormsg):
    c = {}
    c.update(csrf(request))
    if request.session.get('ldapU_is_auth'):
        if  request.session.get('user_ID'):
            context=True
            print "user ID"
            print request.session['user_ID']
            userID = request.session['user_ID']
            print userID
            admin=False
            for p in Entry.objects.raw('SELECT U.id,U.is_superuser FROM buchung_django.auth_user as U WHERE U.id=%s',[userID]):
                is_superuser = p.is_superuser
                if is_superuser ==1:
		    admin=True
            print "LDAP AUTH"
            print request.session['ldapU_is_auth']
    else:
        return new(request)
    print errormsg
    entries = Equipment.objects.filter(enabled=True).order_by('name')
    return render_to_response('ecalendar/add.html',{"error_message": errormsg, 'entries':entries,'context':context,'admin': admin },context_instance=RequestContext(request))

def guest(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('ecalendar/guest.html',c, context_instance=RequestContext(request))

def guestReg(request):
    if request.method == 'POST':
        password = '123Secret'
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        firstName = "GUEST:  "
        firstName += firstname
        email = request.POST['email']
        username = firstname +"_" +lastname
        user = authenticate(username=username, password=password)
        if user is None:
            user = User.objects.create_user(username, email, password)
            user.first_name = firstName
            user.last_name = lastname
            user.groups.add(1)
            user.is_active = True
            user.is_staff = False
            user.save()
        check = User.objects.get(username=username)
        if check:
            request.session['ldapU_is_auth'] = True
            request.session['user_ID'] = check.id
            return add(request,"")
        else:
            return guest(request)
    else:
         return guest(request)

def check(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            if not request.session.get('ldapU_is_auth'):
                if ldapU(request, username=username, password=password):
#                    backendAuth(username)
                    check = User.objects.get(username=username)
		    print "Checkinnnng"
		    print check.id
		    print "EMAIL"
                    print ldapU(request, username=username, password=password)
                    if check:
                        request.session['user_ID'] = check.id
                        request.session['ldapU_is_auth'] = True
                        request.session['user_email'] = _email
                        # setting backend on the user manually, because calling authenticate() doesn't work here
                        # this is just a bad hack
                        check.backend='django.contrib.auth.backends.ModelBackend'
                        login(request, check)
                        return add(request,"")
                    else:
                        return new(request)
                    
                else:
                    return new(request)
            else:
                return add(request,"")
        else:
            return new(request)
    else:
        return new(request)

def dbadd(request):
    c = {}
    c.update(csrf(request))
    errormsg=""
    noFail = True
    mailList = []
    checknumber = 0
    if request.method == 'POST':
        if request.session.get('ldapU_is_auth'):
            context=True
          
            Entrytitle = request.POST['title']
            Entryinfo = request.POST['body']
            anzahlEquip = request.POST['countEquip']
#            get the equipments
#            datumformation

            Entrydate1 = request.POST['date_0']
            Entrydate2 = request.POST['enddate_0']
            Entrytime1 = request.POST['date_1']
            Entrytime2 = request.POST['enddate_1']
            regex2 = re.compile("\A[0-2]\d:[0-5]\d$")
            regex = re.compile("\A[0-2]\d:[0-5]\d:[0-5]\d\Z$")
            is_guest = request.POST['forwho']
            print is_guest
            if is_guest == "forguest":
	        g_firstname=request.POST['firstname']
                g_surname=request.POST['lastname']
                g_mail=request.POST['email']
	    else: 
	        print "ist b110"
	   # if firstname=="":
 	    #    print"ist leer"
        #    print g_firstname
	 #   print g_surname
          #  print g_mail
            if regex2.search(Entrytime1):
                Entrytime1+=":00"
            if regex2.search(Entrytime2):
                Entrytime2+=":00"

#            inputcheck
            inputcheck=0

#            one equipment always in

            Eid = request.POST['equipment']
	    EidList = Eid.split(",")
	    print EidList
	    print len(EidList)
	    roundCount = 0
            print("hier ist die Eid")
	    print Eid
	    test = len(EidList)+1
	    print len(EidList) 
	    errorlist = ""
	    r = 0
	   # for Eid in EidList:
	    for Eid in EidList:
		roundCount += 1
		print ("roundCount")
		print len(EidList)
		print roundCount
                myEquipList=[Eid]
                if not anzahlEquip =="":
                    countEquip = int(anzahlEquip)
                    equipSame=0
                    for i in range(2,countEquip+1):
                        print "anzahl"
                        print i
                        equiPostName='equipment'+str(i)
                        print "->"+equiPostName
                        equip =request.POST[equiPostName]
                        if equip =="":
                            inputcheck += 1
                            errormsg+="\nOne equipment is missing !"
                        for i in myEquipList:

                            if equip == i:
                                equipSame+= 1
                        if equipSame > 0:
                            return add(request,"\nThe Equipments are the same!\nPlease select another one!")
                        else:
                            myEquipList.append(equip)
                for i in myEquipList:
                        print"Equip No"
                        print i
	        is_labmember="true"
	        if is_guest =="forguest":
		    is_labmember = "false"
                    atsign = re.compile("@")
                    if g_firstname=="":
                        inputcheck +=1
		        errormsg+="\nWhere is the firstname from the guest?"
                    if g_surname=="":
		        inputcheck +=1
		        errormsg+="\nWhere is the Surname from the guest?"
                    if g_mail=="":
 		        inputcheck +=1
		        errormsg+="\nWhere is the email from the guest?"
		    if atsign.search(g_mail)==None:
                        inputcheck += 1
                        errormsg +="\nWhere is the (at) sign in the mail adress?"

                if Eid =="" :
                    inputcheck += 1
                    errormsg+="\nYou haven't entered any equipment !"


#            if Entrytitle =="" :
#                inputcheck += 1
#                errormsg+="\nThe title is missing !"
                if Entrydate1 =="" :
                    inputcheck += 1
                    errormsg+="\nThe start date is missing !"
                if Entrydate2 =="" :
                    inputcheck += 1
                    errormsg+="\nThe end date is missing !"
                if Entrytime1 =="" :
                    inputcheck += 1
                    errormsg+="\nThe start time is missing !"
                if Entrytime2 =="" :
                    inputcheck += 1
                    errormsg+="\nThe end time is missing !"
                if not regex.search(Entrytime1):
                    inputcheck += 1
                    errormsg+="\nThe start time has a wrong Format ! The right Format is: HH:MM"
                if not regex.search(Entrytime2):
                    inputcheck += 1
                    errormsg+="\nThe end time has a wrong Format ! The right Format is: HH:MM"
                if inputcheck > 0:
                    return add(request,errormsg)

#            dateformat creating
                time_format = "%Y-%m-%d %H:%M:%S"
                Startdate=Entrydate1+" "+Entrytime1
                Enddate=Entrydate2+" "+Entrytime2
            
                sDT = datetime.fromtimestamp(time.mktime(time.strptime(Startdate, time_format)))
                eDT = datetime.fromtimestamp(time.mktime(time.strptime(Enddate, time_format)))
                today = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                nDT = datetime.fromtimestamp(time.mktime(time.strptime(today, time_format)))
                if sDT>eDT:
                    errormsg+="\nThe end time is before the start time !"
                    return add(request,errormsg)
                if sDT<nDT:
                    errormsg+="\nThe start time is in the past !"
                    return add(request,errormsg)
                for i in myEquipList:
                    print"Equip No datecheck"
                
    #            Checknumber is for the errorcounter
                    #checknumber = 0
		    
		    eqEn=Equipment.objects.get(id=Eid)
                    for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
#                    print str(i) +' = ' + str(e.equipment_id)
                        if str(i) == str(e.equipment_id):
                            print"in"
                            if sDT >= e.date and eDT <= e.enddate:
                                checknumber += 1
                                errormsg += eqEn.name + "\nis not available at this time!"
                                #return add(request, errormsg)
                            elif sDT >= e.date and sDT <= e.enddate and eDT >= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!"
                                #return add(request, errormsg)
                            elif sDT <= e.date and eDT >= e.date and eDT <= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!"
                                #return add(request, errormsg)
                            elif sDT <= e.date and eDT >= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!"
                                #return add(request, errormsg)
                
                    for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
                        if equipm.id == i:
                            if equipm.enabled == False:
                                checknumber += 1
                                errormsg+="\nThe Equipment is not available!"
                                return add(request,errormsg)

#            when the errorcounter is more than 0 the Reservation is not available
                    for i in myEquipList:
			if checknumber == 0:
                            print"Now the db input"
                            print"Equip No"
                            print i
			    print ("checknumber")
			    print checknumber
                            print request.session.keys()
                            eqEn=Equipment.objects.get(id=i)
                            usEn=User.objects.get(id=request.session['user_ID'])
                            print eqEn
                            print usEn
                            print "My Name is"
		            print usEn
		            print "My mail is"
                            if is_labmember=="true":
			        g1 = 0
		                eNew= Entry(
                                    equipment = eqEn,
                                    title = Entrytitle,
                                    body = Entryinfo,
                                    date = sDT,
                                    enddate = eDT,
                                    creator = usEn,
			            guest_id = 0
                            )    
		            else:
			        g1 = Guest(firstname=g_firstname,surname=g_surname,email=g_mail)
                                g1.save()
			
                                guEn =  g1.id
			        print "g1.id"
		   	        print g1.id
			        print "guen"
				print g1.email
			        print guEn
			        print "g1 creator"
		                eNew= Entry(
                                    equipment = eqEn,
                                    title = Entrytitle,
                                    body = Entryinfo,
                                    date = sDT,
                                    enddate = eDT,
                                    creator = usEn,
                                    guest_id = guEn
                            )
	                     
                            eNew.save()
			    mailList.append(eqEn.name)
			    print ("print mailList")
			    print str(mailList)
			    strmailList=", ".join(mailList)
			    print strmailList 
     	 	            type="new"
                            #mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, eqEn, type, g1)
                            Entrydate1
                            b=Entrydate1.split("-")
                            year = b[0]
                            month = b[1]
			    if roundCount == len(EidList):
			        mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, strmailList, type, g1)
		        else:
                            print ("Hier ist der Fehler")
                            print eqEn.name
                            checknumber = 0
			    noFail=False
		        if noFail == False: 
                            if roundCount == len(EidList):
                                return add(request, errormsg)

            return render_to_response('ecalendar/input.html',{'context':context,'year':year,'month':month}, context_instance=RequestContext(request))
    else:
        return render_to_response('ecalendar/add.html',{'context':context}, context_instance=RequestContext(request))



def history(request):
    if request.session.get('ldapU_is_auth'):
        context=True
        usEn=User.objects.get(id=request.session['user_ID'])
	admin=False
	print usEn.is_superuser
	if usEn.is_superuser == 1:
	    admin=True
        if usEn:
            entries = Entry.objects.filter(creator=usEn).order_by('-enddate')[:16]
            return render_to_response("ecalendar/history.html",{'context':context,'entries':entries,'admin':admin}, context_instance=RequestContext(request))
        else:
             return add(request,"Your User is not available!\n ")
    else:
        return render_to_response('ecalendar/new.html', context_instance=RequestContext(request))

def logout(request):
    del request.session['ldapU_is_auth']
    del request.session['user_ID']
    logout_(request)
    return render_to_response('ecalendar/index.html', context_instance=RequestContext(request))

def change(request, evid):
    if request.session.get('ldapU_is_auth'):
        context=True
    errormsg=""
    splitstring= evid.split('|');
    evid=splitstring[0]
    if len(splitstring) >1:
        print len(splitstring)
        errormsg=splitstring[1]

    print evid
    print errormsg
    if evid:
        entries = Entry.objects.get(id=evid)
        start = entries.date
        sd = start.strftime("%Y-%m-%d")
        st = start.strftime("%H:%M:%S")
        end = entries.enddate
        ed = end.strftime("%Y-%m-%d")
        et = end.strftime("%H:%M:%S")
        entries2 = Equipment.objects.filter(enabled=True).order_by('name')

    return render_to_response("ecalendar/change.html", {"error_message": errormsg, 'entries':entries,'entries2':entries2,'startdate':sd,'starttime':st,'enddate':ed,'endtime':et,'context':context },context_instance=RequestContext(request))
            
            
def changeadd(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    mailList=[]
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        if request.session.get('ldapU_is_auth'):

            Entryid = request.POST['entry']
            errormsg=Entryid+"|"
            Eid = request.POST['equipment']
            Entrytitle = request.POST['title']
            Entryinfo = request.POST['body']

#            dateinformation
            Entrydate1 = request.POST['date_0']
            Entrydate2 = request.POST['enddate_0']
            Entrytime1 = request.POST['date_1']
            Entrytime2 = request.POST['enddate_1']
            regex2 = re.compile("\A[0-2]\d:[0-5]\d$")
            regex = re.compile("\A[0-2]\d:[0-5]\d:[0-5]\d\Z$")

            if regex2.search(Entrytime1):
                Entrytime1+=":00"
            if regex2.search(Entrytime2):
                Entrytime2+=":00"


#            inputcheck
            inputcheck=0
            if Eid =="" :
                inputcheck += 1
                errormsg+="\nThe equipment ID is missing !"
#            if Entrytitle =="" :
#                inputcheck += 1
#                errormsg+="\nThe title is missing !"
            if Entrydate1 =="" :
                inputcheck += 1
                errormsg+="\nThe start date is missing !"
            if Entrydate2 =="" :
                inputcheck += 1
                errormsg+="\nThe end date is missing !"
            if Entrytime1 =="" :
                inputcheck += 1
                errormsg+="\nThe start time is missing !"
            if Entrytime2 =="" :
                inputcheck += 1
                errormsg+="\nThe end time is missing !"
            if not regex.search(Entrytime1):
                inputcheck += 1
                errormsg+="\nThe start time has a wrong Format ! The right Format is: HH:MM:SS"
            if not regex.search(Entrytime2):
                inputcheck += 1
                errormsg+="\nThe end time has a wrong Format ! The right Format is: HH:MM:SS"
            if inputcheck > 0:
                return change(request,errormsg)

#            dateformat creating
            time_format = "%Y-%m-%d %H:%M:%S"
            Startdate=Entrydate1+" "+Entrytime1
            Enddate=Entrydate2+" "+Entrytime2

            sDT = datetime.fromtimestamp(time.mktime(time.strptime(Startdate, time_format)))
            eDT = datetime.fromtimestamp(time.mktime(time.strptime(Enddate, time_format)))

            if sDT>eDT:
                errormsg+="\nThe end time is before the start time !"
                return change(request,errormsg)


#            Checknumber is for the errorcounter
            checknumber = 0
            for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
                if str(e.id) !=Entryid:
                    print str(e.id) +" != "+ Entryid
                     

                    if Eid == str(e.equipment_id):


                        if sDT >= e.date and eDT <= e.enddate:
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!"
                            return change(request,errormsg)
                        elif sDT >= e.date and sDT <= e.enddate and eDT >= e.enddate :
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!"
                            return change(request,errormsg)
                        elif sDT <= e.date and eDT >= e.date and eDT <= e.enddate :
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!"
                            return change(request,errormsg)
                        elif sDT <= e.date and eDT >= e.enddate:
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!"
                            return change(request,errormsg)
                else:
                    print "The selected Entry"
            for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
                if equipm.id == Eid:
                    if equipm.enabled == False:
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available!"
                        return change(request,errormsg)

#            when the errorcounter is more than 0 the Reservation is not available
            if checknumber > 0:
                return delete(request,errormsg)
            else:
                print"Now the db input"
                print request.session['user_ID']
                eqEn=Equipment.objects.get(id=Eid)
                usEn=User.objects.get(id=request.session['user_ID'])
                print eqEn
                print usEn
		g1=0
		Entryobj= Entry.objects.get(id=Entryid)
		if Entryobj.guest_id != 0 :
		   g1=Entryobj.guest
		   guEn=g1.id
                eChange=Entry.objects.filter(id=Entryid)
		if g1 == 0:
                    eChange.update(
                        equipment = eqEn,
                        title = Entrytitle,
                        body = Entryinfo,
                        date = sDT,
                        enddate = eDT,
                        creator = usEn,
		        guest = 0
                       )
		if g1 != 0:
		    eChange.update(
                        equipment = eqEn,
                        title = Entrytitle,
                        body = Entryinfo,
                        date = sDT,
                        enddate = eDT,
                        creator = usEn,
                        guest = guEn
                       )
        	type="change"
		mailList.append(eqEn.name)
                strmailList=", ".join(mailList)
                print strmailList
                mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, strmailList, type, g1)
                return render_to_response('ecalendar/changed.html',{'context':context}, context_instance=RequestContext(request))
        else:
            return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))
    else:
        return render_to_response('ecalendar/add.html',{'context':context}, context_instance=RequestContext(request))

def delete(request):
    c = {}
    c.update(csrf(request))
    if request.session.get('ldapU_is_auth'):
        context=True
    if request.method == 'POST':
        if request.session.get('ldapU_is_auth'):
            Entryid = request.POST['entry']
            test = int(Entryid)
            g1 = 0
	    Entryobj= Entry.objects.get(id=Entryid)
            if Entryobj.guest_id != 0 :
                g1=Entryobj.guest
            print test
            for p in  Entry.objects.raw('SELECT ecalendar_entry.id,name, date, enddate FROM ecalendar_entry INNER JOIN ecalendar_equipment ON ecalendar_entry.equipment_id = ecalendar_equipment.id WHERE ecalendar_entry.id=%s',[test]):
		Entrydate1= p.date
		Entrydate2 = p.enddate
                eqEn = p.name
            Entrydate1=str(Entrydate1)
            Entrydate2=str(Entrydate2)
            Entrydate1 = Entrydate1.split(" ")[0]
            Entrydate2 = Entrydate2.split(" ")[0]
            Entry.objects.filter(id=Entryid).delete()
            type="delete"
            usEn=User.objects.get(id=request.session['user_ID'])
            Entrytime1=""
            Entrytime2=""
	   # g1 = 0
           # Entryobj= Entry.objects.get(id=Entryid)
            if Entryobj.guest_id != 0 :
                g1=Entryobj.guest
	    print usEn.first_name
            print usEn.email
            print Entrydate1
            print Entrydate2
            print eqEn 
            mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, eqEn, type,g1)
            return render_to_response('ecalendar/delete.html',{'context':context}, context_instance=RequestContext(request))

        else:
            return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))
    else:
          return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))

def ajax_search_equip(request):
    if request.is_ajax():
       if request.method == 'POST':
            post = request.POST.copy()
            if post.has_key('name') :
                print 'Raw Data: "%s"' % request.raw_post_data
                equipment = []
                eName = post['name']
                print eName
                print "AJAX POOST"

                equipment = Equipment.objects.filter(name__contains=eName)
                print equipment
                for e in equipment:
                    print e.name

                json =serializers.serialize('json', equipment, ensure_ascii=False)
                return HttpResponse(json, mimetype="application/json")

    else:
      entries.append("NO AJAX")

    return HttpResponse()

#                another opinion to search
#                a = Equipment.objects.all()
#                regex=re.compile("\w*%s\w*" % name)
#                for en in a:
#                    nameEq = en.name
#                    r = regex.search(nameEq)
#                    if r:
#                        check = Equipment.objects.get(id=en.id)
#                        equipment.append(check)
#                equipment=name
