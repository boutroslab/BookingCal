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
from django.contrib.auth import authenticate
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

mnames = "January February March April May June July August September October November December"
mnames = mnames.split()

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
    return render_to_response("ecalendar/index.html", dict(years=lst, year=year,
                              reminders=reminders(request),request=request))

def month(request, year, month, change=None):
    """Listinng of days in 'month'. """
    year, month = int(year), int(month)

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

            a = Entry.objects.all()
            entries = []
            for en in a:
                startdate = datetime(en.date.year, en.date.month, en.date.day)
                enddate = datetime(en.enddate.year, en.enddate.month, en.enddate.day)

                if startdate <= checktime and enddate >= checktime:
                    check = Entry.objects.get(id=en.id)
                    if len(entries) == 3:
                        check.title = "and more"
                        entries.append(check)
                        break

                    entries.append(check)

            if day == nday and year == nyear and month == nmonth:
                current = True

        lst[week].append((day, entries, current))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1


    return render_to_response("ecalendar/month.html", dict(year=year, month=month, month_days=lst, mname=mnames[month-1],request=request))

def day(request, year, month, day):
    year, month, day = int(year), int(month), int(day)

    if day:
        fday = day
        checktime = datetime(year, month, fday)

        a = Entry.objects.all()
        entries = []
        for en in a:
            startdate = datetime(en.date.year, en.date.month, en.date.day)
            enddate = datetime(en.enddate.year, en.enddate.month, en.enddate.day)

            if startdate <= checktime and enddate >= checktime:
                check = Entry.objects.get(id=en.id)
                entries.append(check)


    return render_to_response("ecalendar/day.html", dict(year=year, month=month, day=day, entries=entries ,request=request))

def event(request, evid):

    if evid:
        entries = Entry.objects.get(id=evid)

    return render_to_response("ecalendar/event.html", dict(entries=entries ,request=request))

def ldapU(request, username, password):
    c = {}
    c.update(csrf(request))
    
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

            print "Succcessfully bound - whoami says: "
        except ldap.INVALID_CREDENTIALS, err:
            print "LDAP Error: %s" % err
        
   
    print "Unbinding from directory ..."

    l.unbind()
    print "-" * 100
    print "\n\n"

    return ldapIn
    
def backendAuth(username):
    password = '123Secret'
    user = authenticate(username=username, password=password)
    if user is not None:
        return
    else:
        user = User.objects.create_user(username, '', password)
        user.groups.add(0)
        user.is_active = True
        user.is_staff = False
        user.save()
    return


def new(request):
    c = {}
    c.update(csrf(request))
    if not request.session.get('ldapU_is_auth', False):
        return render_to_response('ecalendar/new.html',{'request': request})
    else:
        return add(request,"")
    

def add(request,errormsg):
    c = {}
    c.update(csrf(request))
    
    if request.session.get('ldapU_is_auth', False):
        if  request.session.get('user_ID', False):
            print "user ID"
            print request.session['user_ID']
            print "LDAP AUTH"
            print request.session['ldapU_is_auth']
    else:
        return new(request)
    print errormsg
    entries = Equipment.objects.filter(enabled=True).order_by('name')

    return render_to_response('ecalendar/add.html', {"error_message": errormsg, 'entries':entries,'request': request},context_instance=RequestContext(request),request=request)

#    return HttpResponse(render_to_response('ecalendar/add.html', c,  {"msg": errormsg}) )


def check(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            if not request.session.get('ldapU_is_auth', False):
                if ldapU(request, username=username, password=password):
                    backendAuth(username)
                    check = User.objects.get(username=username)
                    if check:
                        request.session['user_ID'] = check.id
                    else:
                        return new(request)
                    return add(request,"")
                else:
                    return new(request)
            else:
                 return new(request)
        else:
            return new(request)
    else:
        return new(request)

def dbadd(request):
    c = {}
    c.update(csrf(request))
    errormsg=""
    if request.method == 'POST':
        if request.session.get('ldapU_is_auth', False):
           
            Eid = request.POST['equipment']
            Entrytitle = request.POST['title']
            Entryinfo = request.POST['body']

#            dateinformation
            Entrydate1 = request.POST['date_0']
            Entrydate2 = request.POST['enddate_0']
            Entrytime1 = request.POST['date_1']
            Entrytime2 = request.POST['enddate_1']

#            inputcheck
            inputcheck=0
            if Eid =="" :
                inputcheck += 1
                errormsg+="\nThe equipment ID is missing !"
            if Entrytitle =="" :
                inputcheck += 1
                errormsg+="\nThe title is missing !"
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
            if inputcheck > 0:
                return add(request,errormsg)

#            dateformat creating
            time_format = "%Y-%m-%d %H:%M:%S"
            Startdate=Entrydate1+" "+Entrytime1
            sDT = datetime.fromtimestamp(time.mktime(time.strptime(Startdate, time_format)))

            Enddate=Entrydate2+" "+Entrytime2
            eDT = datetime.fromtimestamp(time.mktime(time.strptime(Enddate, time_format)))

            if sDT>eDT:
                errormsg+="\nThe end time is before the start time !"
                return add(request,errormsg)
          
#            print "Equiptment ID"
#            print Eid
#            print"Entry Title"
#            print Entrytitle
#            print"Entry INformation"
#            print Entryinfo
#
#            print"DATEEEEE"
#            print"date Start "
#            print Entrydate1
#            print"time Start"
#            print Entrytime1
#            print"date ende"
#            print Entrydate2
#            print"time ende"
#            print Entrytime2
#            print "\nDateTime chagned"
#            print "DateTime Start"
#            print sDT
#            print "DateTime Ende"     
#            print eDT

#            Checknumber is for the errorcounter
            checknumber = 0
            for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):

#                print "equipment check"
#                print Eid+ " == "
#                print str(e.equipment_id)

                if Eid == str(e.equipment_id):

#                    print "DAte check"
#                    print str(sDT) +" >= "+str(e.date)+" and "+str(eDT)+" <= "+str(e.enddate)
#                    print str(sDT) +" >= "+str(e.date)+" and "+str(sDT)+" <= "+str(e.enddate)+" and "+str(eDT)+ " >= " +str(e.enddate)
#                    print str(sDT) +" <= "+str(e.date)+" and "+str(eDT)+" >= "+str(e.date)+" and "+str(eDT)+ " <= " +str(e.enddate)
#                    print str(sDT) +" <= "+str(e.date)+" and "+str(eDT)+" >= "+str(e.enddate)

                    if sDT >= e.date and eDT <= e.enddate:
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available at this time!"
                        return add(request,errormsg)
                    elif sDT >= e.date and sDT <= e.enddate and eDT >= e.enddate :
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available at this time!"
                        return add(request,errormsg)
                    elif sDT <= e.date and eDT >= e.date and eDT <= e.enddate :
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available at this time!"
                        return add(request,errormsg)
                    elif sDT <= e.date and eDT >= e.enddate:
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available at this time!"
                        return add(request,errormsg)
            for equipm in Equipment.objects.raw('SELECT * FROM ecalendar_equipment'):
                if equipm.id == Eid:
                    if equipm.enabled == False:
                        checknumber += 1
                        errormsg+="\nThe Equipment is not available!"
                        return add(request,errormsg)

#            when the errorcounter is more than 0 the Reservation is not available
            if checknumber > 0:
                return add(request,errormsg)
            else:
                print"Now the db input"
                print request.session['user_ID']
                eqEn=Equipment.objects.get(id=Eid)
                usEn=User.objects.get(id=request.session['user_ID'])
                print eqEn
                print usEn
                eNew= Entry(
                    equipment = eqEn,
                    title = Entrytitle,
                    body = Entryinfo,
                    date = sDT,
                    enddate = eDT,
                    creator = usEn
                )
                eNew.save()

            return render_to_response('ecalendar/input.html',{'request': request,c:c})
        else:
            return render_to_response('ecalendar/new.html',{'request': request,c:c})
    else:
        return render_to_response('ecalendar/add.html',{'request': request,c:c})



def history(request):
    
    if request.session.get('ldapU_is_auth', False):
        usEn=User.objects.get(id=request.session['user_ID'])
        if usEn:
            entries = Entry.objects.filter(creator=usEn).order_by('-enddate')
            return render_to_response("ecalendar/history.html",dict(entries=entries))
        else:
             return add(request,"Your User is not available!\n ")
    else:
        return render_to_response('ecalendar/new.html',{'request': request,c:c})

def logout(request):
    del request.session['ldapU_is_auth']
    del request.session['user_ID']
    return render_to_response('ecalendar/index.html',{'request': request,c:c})

def change(request, evid):
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

    return render_to_response("ecalendar/change.html", {"error_message": errormsg, 'entries':entries,'entries2':entries2,'startdate':sd,'starttime':st,'enddate':ed,'endtime':et,'request': request},context_instance=RequestContext(request))
            
            
def changeadd(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        if request.session.get('ldapU_is_auth', False):

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

#            inputcheck
            inputcheck=0
            if Eid =="" :
                inputcheck += 1
                errormsg+="\nThe equipment ID is missing !"
            if Entrytitle =="" :
                inputcheck += 1
                errormsg+="\nThe title is missing !"
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
            if inputcheck > 0:
                return change(request,errormsg)

#            dateformat creating
            time_format = "%Y-%m-%d %H:%M:%S"
            Startdate=Entrydate1+" "+Entrytime1
            sDT = datetime.fromtimestamp(time.mktime(time.strptime(Startdate, time_format)))

            Enddate=Entrydate2+" "+Entrytime2
            eDT = datetime.fromtimestamp(time.mktime(time.strptime(Enddate, time_format)))

            if sDT>eDT:
                errormsg+="\nThe end time is before the start time !"
                return change(request,errormsg)
          
#            print "Equiptment ID"
#            print Eid
#            print"Entry Title"
#            print Entrytitle
#            print"Entry INformation"
#            print Entryinfo
#
#            print"DATEEEEE"
#            print"date Start "
#            print Entrydate1
#            print"time Start"
#            print Entrytime1
#            print"date ende"
#            print Entrydate2
#            print"time ende"
#            print Entrytime2
#            print "\nDateTime chagned"
#            print "DateTime Start"
#            print sDT
#            print "DateTime Ende"     
#            print eDT

#            Checknumber is for the errorcounter
            checknumber = 0
            for e in Entry.objects.raw('SELECT * FROM ecalendar_entry'):
                if str(e.id) !=Entryid:
                    print str(e.id) +" != "+ Entryid
#                print "equipment check"
#                print Eid+ " == "
#                print str(e.equipment_id)

                    if Eid == str(e.equipment_id):

#                    print "DAte check"
#                    print str(sDT) +" >= "+str(e.date)+" and "+str(eDT)+" <= "+str(e.enddate)
#                    print str(sDT) +" >= "+str(e.date)+" and "+str(sDT)+" <= "+str(e.enddate)+" and "+str(eDT)+ " >= " +str(e.enddate)
#                    print str(sDT) +" <= "+str(e.date)+" and "+str(eDT)+" >= "+str(e.date)+" and "+str(eDT)+ " <= " +str(e.enddate)
#                    print str(sDT) +" <= "+str(e.date)+" and "+str(eDT)+" >= "+str(e.enddate)

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
                return change(request,errormsg)
            else:
                print"Now the db input"
                print request.session['user_ID']
                eqEn=Equipment.objects.get(id=Eid)
                usEn=User.objects.get(id=request.session['user_ID'])
                print eqEn
                print usEn
                eChange=Entry.objects.filter(id=Entryid)
                eChange.update(
                    equipment = eqEn,
                    title = Entrytitle,
                    body = Entryinfo,
                    date = sDT,
                    enddate = eDT,
                    creator = usEn
                )

                return render_to_response('ecalendar/changed.html',{'request': request,c:c})
        else:
            return render_to_response('ecalendar/new.html',{'request': request,c:c})
    else:
        return render_to_response('ecalendar/add.html',{'request': request,c:c})

def delete(request):
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        if request.session.get('ldapU_is_auth', False):

            Entryid = request.POST['entry']
            Entry.objects.filter(id=Entryid).delete()

            return render_to_response('ecalendar/delete.html',{'request': request,c:c})

        else:
            return render_to_response('ecalendar/new.html',{'request': request,c:c})
    else:
          return render_to_response('ecalendar/new.html',{'request': request,c:c})
