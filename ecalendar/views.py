import os
import calendar
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
import getpass
from symbol import except_clause
import time
import inspect 
#just for MAC
#from StdSuites.Type_Names_Suite import null
from ecalendar.models import Entry
from ecalendar.models import Equipment
from ecalendar.models import Guest
from django.contrib.auth import authenticate, login
from django.conf import settings
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
    """

    @param request: xxxx
    """
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

    """Listing of days in 'month'. """
    
    year, month = int(year), int(month)
    sort=False
    if change == "sort":
        eq = int(eq)
        sort=True
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
    """

    @param request: xxxx
    """
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
    """ 


    @param request: xxxx
    """
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    if evid:
        entries = Entry.objects.get(id=evid)

    return render_to_response("ecalendar/event.html", dict(entries=entries ,request=request,context=context), context_instance=RequestContext(request))

def ldapU(request, username, password):
    """

    
    @param username: username is your LDAP username
    @param password: password is your LDAP password
    """
    c = {}
    c.update(csrf(request))
    #url from the ldap server 
    server_uri = 'ldap://ad.dkfz-heidelberg.de:389'

    # if bind_user and bind_pw is both '' it does an anonymous bind
    bind_user = 'CN=ldap,CN=Users,DC=ad,DC=dkfz-heidelberg,DC=de'
    bind_pw = 'logalvsa'
    
    #B110
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

    l = ldap.initialize(server_uri)

    l.bind_s(bind_user, bind_pw)

    search_filter = filter_str % adUser


    lusers = l.search_s(base_dn, searchScope, search_filter, attrs)
    results = len(lusers)

    ldapIn = False

    if results:
        first_dn = lusers[0][0]
        try:
            l.bind_s(first_dn, adPW)
            ldapIn = True
            for dn,entry in lusers:
                if dn != None:
                    emailad =  entry['mail']
                    fname = entry['displayName']
                    backendAuth(username,fname, emailad)
        except ldap.INVALID_CREDENTIALS, err:
            print "LDAP Error: %s" % err
        
   
    l.unbind()

    return ldapIn

def backendAuth(username,name, mail):
    """

    @param request: xxxx
    """
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
    """

    @param request: xxxx
    """
    c = {}
    c.update(csrf(request))
    if not request.session.get('ldapU_is_auth'):
        return render_to_response('ecalendar/new.html',c,context_instance=RequestContext(request))
    else:
        return add(request,"")


def mail(user, startdate, enddate, starttime, endtime, eqi, type,is_guest):
    """
    Mail function, which Creates a info mail for booking, changing oder cancleling. 
    This function is called by the "dbadd","changeadd" and "delete" functions. The parameters are.
    
    
    
    
    @type user: object
    @param user: contains the user object
    @type startdate: string
    @param  startdate: contains the startday from the booking
    @type enddate: string
    @param enddate: -"-            endday    -"-
    @type starttime: string
    @param starttime: contains the booking time from the startday
    @type endtime: string
    @param endtime: cointains the return time from the endtime
    @type type: string
    @param type: contains the value like "booking", "changing" oder "deleting" which calls the mail function which mail sould be send.
    @type is_guest: boolean
    @param is_guest: this boolean value defines if the booking mail should be sent to a normal user or to a guest user
    """
    smtp_server=getattr(settings, 'SMTP_SERVER', 'default_value')
    """@var: This is an instance variable."""


    """
    This comment provides documentation for the following
    recipients.
    """ 
    recipients = user.email


    if is_guest != 0:
    
        recipients=is_guest.email
	firstname = is_guest.firstname
    else:
        firstname = user.first_name
    """
    This comment mail.is_guest provides documentation for the following
    sender.
    """
    #: docstring for sender
    sender = getattr(settings, 'SENDER_MAIL', 'default_value')
    """
    views.sender This comment provides documentation for the following
    recipients.
    
    """ 
    if (type=="new"):
        subject = "Booking System: reservation"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname+",\n " "you have booked\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ enddate +" at "+ endtime+"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have booked\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ endtime+"."
    if (type=="change"):
        subject = "Booking System: change"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname +",\n " "you have booked\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ enddate +" at "+ endtime+"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have booked\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ endtime+"."
    if (type=="delete"):
        subject = "Booking System: cancellation"
        if (startdate != enddate):
            msg_text = "Hello "+ firstname +",\n " "you have cancelled the following booking,\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ enddate +" at "+ endtime+"."
        else:
            msg_text = "Hello "+ firstname +",\n " "you have cancelled the following booking,\n "+ eqi +"\n on "+ startdate + " at "+ starttime +" to "+ endtime+"."
    msg = MIMEText(msg_text)
    
    msg['Subject'] = subject
    s = smtplib.SMTP()
    s.connect(smtp_server)
    s.sendmail(sender, recipients, msg.as_string())
    s.close()

def add(request,errormsg):
    """
    The "add" function is check that your username in the database and is looking wethere you are a superuser or not. 
    A superuser can book for guest.

    
    
    
    @param request: xxxx
    @param errormsg: xxxx
    """
    c = {}
    c.update(csrf(request))
    if request.session.get('ldapU_is_auth'):
        if  request.session.get('user_ID'):
            context=True
            userID = request.session['user_ID']
            admin=False
            for p in Entry.objects.raw('SELECT U.id,U.is_superuser FROM buchung_django.auth_user as U WHERE U.id=%s',[userID]):
                is_superuser = p.is_superuser
                if is_superuser ==1:
		    admin=True
    else:
        return new(request)
    entries = Equipment.objects.filter(enabled=True).order_by('name')
    return render_to_response('ecalendar/add.html',{"error_message": errormsg, 'entries':entries,'context':context,'admin': admin },context_instance=RequestContext(request))


def check(request):
    """
    The "Check" function is checking the username and password with the ldap.


    
    @param request: xxxx
    """
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            if not request.session.get('ldapU_is_auth'):
                if ldapU(request, username=username, password=password):
                    check = User.objects.get(username=username)
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
    """
    The "dbadd" function is the main function for the booking. because the dbadd create your book or call u what is wrong, 
    for example that the choosed equipment is allready booked at this time. 


    @param request: xxxx
    @rtype:   page
    @return:  return the confirmation that you have booked this equipment
    """
    c = {}
    c.update(csrf(request))
    errormsg=""
#noFail is everytime true if you want to book a bookable equipment
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
            #Date and Time values from the bookpage as strings 
            Entrydate1 = request.POST['date_0']
            Entrydate2 = request.POST['enddate_0']
            Entrytime1 = request.POST['date_1']
            Entrytime2 = request.POST['enddate_1']
            #create RegEx 
            regex2 = re.compile("\A[0-2]\d:[0-5]\d$")
            regex = re.compile("\A[0-2]\d:[0-5]\d:[0-5]\d\Z$")
            is_guest = request.POST['forwho']
            """is_guest is the boolean value which contains the information is it a guest or not """
            if is_guest == "forguest":
	        g_firstname=request.POST['firstname']
                g_surname=request.POST['lastname']
                g_mail=request.POST['email']
            if regex2.search(Entrytime1):
                Entrytime1+=":00"
            if regex2.search(Entrytime2):
                Entrytime2+=":00"

#            inputcheck
            inputcheck=0

#            one equipment always in

            Eid = request.POST['equipment']
	    EidList = Eid.split(",")
        #after every "round" between the following code, is roundCount a comparable value with then large of list with all booked equipments 
	    roundCount = 0
	    errorlist = ""
	    for Eid in EidList:
        #after every round goes roundCount +1
		roundCount += 1
                myEquipList=[Eid]
                if not anzahlEquip =="":
                    countEquip = int(anzahlEquip)
                    equipSame=0
                    for i in range(2,countEquip+1):
                        equiPostName='equipment'+str(i)
                        equip =request.POST[equiPostName]
                        if equip =="":
                            inputcheck += 1
                            errormsg+="\nOne equipment is missing !\n"
                        for i in myEquipList:

                            if equip == i:
                                equipSame+= 1
                        if equipSame > 0:
                            return add(request,"\nThe Equipments are the same!\nPlease select another one!")
                        else:
                            myEquipList.append(equip)
#is_labmember is the boolean value which contains the information is it a labmember book or is it a guest book
	        is_labmember="true"
	        if is_guest =="forguest":
		    is_labmember = "false"
                    atsign = re.compile("@")
                    if g_firstname=="":
                        inputcheck +=1
		        errormsg+="\nWhere is the firstname from the guest?\n"
                    if g_surname=="":
		        inputcheck +=1
		        errormsg+="\nWhere is the Surname from the guest?\n"
                    if g_mail=="":
 		        inputcheck +=1
		        errormsg+="\nWhere is the email from the guest?\n"
		    if atsign.search(g_mail)==None:
                        inputcheck += 1
                        errormsg +="\nWhere is the (at) sign in the mail adress?\n"

                if Eid =="" :
                    inputcheck += 1
                    errormsg+="\nYou haven't entered any equipment !\n"


                if Entrydate1 =="" :
                    inputcheck += 1
                    errormsg+="\nThe start date is missing !\n"
                if Entrydate2 =="" :
                    inputcheck += 1
                    errormsg+="\nThe end date is missing !\n"
                if Entrytime1 =="" :
                    inputcheck += 1
                    errormsg+="\nThe start time is missing !\n"
                if Entrytime2 =="" :
                    inputcheck += 1
                    errormsg+="\nThe end time is missing !\n"
                if not regex.search(Entrytime1):
                    inputcheck += 1
                    errormsg+="\nThe start time has a wrong Format ! The right Format is: HH:MM\n"
                if not regex.search(Entrytime2):
                    inputcheck += 1
                    errormsg+="\nThe end time has a wrong Format ! The right Format is: HH:MM\n"
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
                    errormsg+="\nThe end time is before the start time !\n"
                    return add(request,errormsg)
                if sDT<nDT:
                    errormsg+="\nThe start time is in the past !\n"
                    return add(request,errormsg)
                for i in myEquipList:
                
		    
		    eqEn=Equipment.objects.get(id=Eid)
                    for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
                        if str(i) == str(e.equipment_id):
                            if sDT >= e.date and eDT <= e.enddate:
                                checknumber += 1
                                errormsg += eqEn.name + "\n\nis not available at this time!\n"
                            elif sDT >= e.date and sDT <= e.enddate and eDT >= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!\n"
                            elif sDT <= e.date and eDT >= e.date and eDT <= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!\n"
                            elif sDT <= e.date and eDT >= e.enddate:
                                checknumber += 1
                                errormsg += "\nThe Equipment is not available at this time!\n"
                
                    for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
                        if equipm.id == i:
                            if equipm.enabled == False:
                                checknumber += 1
                                errormsg+="\nThe Equipment is not available!\n"
                                return add(request,errormsg)

#            when the errorcounter is more than 0 the Reservation is not available
                    for i in myEquipList:
			if checknumber == 0:
                            eqEn=Equipment.objects.get(id=i)
                            usEn=User.objects.get(id=request.session['user_ID'])
                            if is_labmember=="true":
				#g1 is the guest object which contains the data from the guest. If you want to book something for your own g1==0, else g1 contains all the information about the guest
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
                            #add the equipment name to the mailList
			    mailList.append(eqEn.name)
                            #convert the mailList List to a String separated by comma
			    strmailList=", ".join(mailList)
                            #information for the mail()
     	 	            type="new"
                            Entrydate1
                            splitedDate=Entrydate1.split("-")
                            year = splitedDate[0]
                            month = splitedDate[1]
			    #if roundCount has the same length like the List of all choosen Equipments, will be call the mail()
			    if roundCount == len(EidList):
			        mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, strmailList, type, g1)
		        else:
			    #if nowhere happend any fail, then ist checknumber==0 and noFail is False
                            checknumber = 0
			    noFail=False
			#if noFail == False and roundCount == the length of the EidList is this function finsh.
		        if noFail == False: 
                            if roundCount == len(EidList):
                                return add(request, errormsg)

            return render_to_response('ecalendar/input.html',{'context':context,'year':year,'month':month}, context_instance=RequestContext(request))
    else:
        return render_to_response('ecalendar/add.html',{'context':context}, context_instance=RequestContext(request))


def history(request):
    """
    The history function is creating the history entries
 


    @param request: xxxx
    @rtype:   page
    @return:  return a page with all booking which u ever have made
    """
    
    if request.session.get('ldapU_is_auth'):
        context=True
	#usEn is getting the User object which contains the information which equipment has anybody booked
        usEn=User.objects.get(id=request.session['user_ID'])
	admin=False
	#if usEn.is_superuser == 1, then you'r a superuser which kann delete or change the bookings, which he has made for a guest. otherwihle you can just delete oder change your own bookings.
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
    """
    The logout function is just for the logout ;)  


    @param request: xxxx
    @rtype:   page
    @return:  return the index page as sign that you logged out
    """
   
    del request.session['ldapU_is_auth']
    del request.session['user_ID']
    logout_(request)
    return render_to_response('ecalendar/index.html', context_instance=RequestContext(request))


def change(request, evid):
    """
    The change function is for the rendering form the change page values.
 


    @param request: xxxx
    @rtype:   page
    @return:  return the values from a entry which you had made on a page
    """
    if request.session.get('ldapU_is_auth'):
        context=True
    errormsg=""
    splitstring= evid.split('|');
    evid=splitstring[0]
    if len(splitstring) >1:
        errormsg=splitstring[1]

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
    """
    The changeadd function is adding your changed values to the database and is check them for any fail.             
 


    @param request: xxxx   
    @rtype:   page
    @return:  return the confirmation that you have changed this entry
    """
    if request.session.get('ldapU_is_auth'):
        context=True
    mailList=[]
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        if request.session.get('ldapU_is_auth'):
            #checking the fields, of the Changeentry page
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
                errormsg+="\nThe equipment ID is missing !\n"
            if Entrydate1 =="" :
                inputcheck += 1
                errormsg+="\nThe start date is missing !\n"
            if Entrydate2 =="" :
                inputcheck += 1
                errormsg+="\nThe end date is missing !\n"
            if Entrytime1 =="" :
                inputcheck += 1
                errormsg+="\nThe start time is missing !\n"
            if Entrytime2 =="" :
                inputcheck += 1
                errormsg+="\nThe end time is missing !\n"
            if not regex.search(Entrytime1):
                inputcheck += 1
                errormsg+="\nThe start time has a wrong Format ! The right Format is: HH:MM:SS\n"
            if not regex.search(Entrytime2):
                inputcheck += 1
                errormsg+="\nThe end time has a wrong Format ! The right Format is: HH:MM:SS\n"
            if inputcheck > 0:
                return change(request,errormsg)

#            dateformat creating
            time_format = "%Y-%m-%d %H:%M:%S"
            Startdate=Entrydate1+" "+Entrytime1
            Enddate=Entrydate2+" "+Entrytime2

            sDT = datetime.fromtimestamp(time.mktime(time.strptime(Startdate, time_format)))
            eDT = datetime.fromtimestamp(time.mktime(time.strptime(Enddate, time_format)))

            if sDT>eDT:
                errormsg+="\nThe end time is before the start time !\n"
                return change(request,errormsg)


#            Checknumber is for the errorcounter
            checknumber = 0
            for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
                if str(e.id) !=Entryid:
                     

                    if Eid == str(e.equipment_id):


                        if sDT >= e.date and eDT <= e.enddate:
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!\n"
                            return change(request,errormsg)
                        elif sDT >= e.date and sDT <= e.enddate and eDT >= e.enddate :
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!\n"
                            return change(request,errormsg)
                        elif sDT <= e.date and eDT >= e.date and eDT <= e.enddate :
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!\n"
                            return change(request,errormsg)
                        elif sDT <= e.date and eDT >= e.enddate:
                            checknumber += 1
                            errormsg+="\nThe Equipment is not available at this time!\n"
                            return change(request,errormsg)
            for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
                if equipm.id == Eid:
                    if equipm.enabled == False:
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available!\n"
                        return change(request,errormsg)

#            when the errorcounter is more than 0 the Reservation is not available
            if checknumber > 0:
                return delete(request,errormsg)
            else:
                
                eqEn=Equipment.objects.get(id=Eid)
                usEn=User.objects.get(id=request.session['user_ID'])
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
		#information for the mail()
        	type="change"
		mailList.append(eqEn.name)
                strmailList=", ".join(mailList)
                mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, strmailList, type, g1)
                return render_to_response('ecalendar/changed.html',{'context':context}, context_instance=RequestContext(request))
        else:
            return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))
    else:
        return render_to_response('ecalendar/add.html',{'context':context}, context_instance=RequestContext(request))


def delete(request):
    """
    The delete function is just cancelation your booking, and delete it from the database
 


    @param request: xxxx
    @rtype:   page
    @return:  return the confirmation that you have deleted this entry
    """
    c = {}
    c.update(csrf(request))
    if request.session.get('ldapU_is_auth'):
        context=True
    if request.method == 'POST':
        if request.session.get('ldapU_is_auth'):
            Entryid = request.POST['entry']
            eNid = int(Entryid)
            g1 = 0
	    Entryobj= Entry.objects.get(id=Entryid)
            if Entryobj.guest_id != 0 :
                g1=Entryobj.guest
            for p in  Entry.objects.raw('SELECT ecalendar_entry.id,name, date, enddate FROM ecalendar_entry INNER JOIN ecalendar_equipment ON ecalendar_entry.equipment_id = ecalendar_equipment.id WHERE ecalendar_entry.id=%s',[eNid]):
		Entrydate1= p.date
		Entrydate2 = p.enddate
                eqEn = p.name
            usEntrydate1=str(Entrydate1)
            usEntrydate2=str(Entrydate2)
            Entrydate1 = usEntrydate1.split(" ")[0]
            Entrydate2 = usEntrydate2.split(" ")[0]
            Entrytime1 = usEntrydate1.split(" ")[1]
            Entrytime2 = usEntrydate2.split(" ")[1]
            Entry.objects.filter(id=Entryid).delete()
            #information for the mail()
            type="delete"
            usEn=User.objects.get(id=request.session['user_ID'])
            if Entryobj.guest_id != 0 :
                g1=Entryobj.guest
            mail(usEn, Entrydate1, Entrydate2, Entrytime1, Entrytime2, eqEn, type,g1)
            return render_to_response('ecalendar/delete.html',{'context':context}, context_instance=RequestContext(request))

        else:
            return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))
    else:
          return render_to_response('ecalendar/new.html',{'context':context}, context_instance=RequestContext(request))

