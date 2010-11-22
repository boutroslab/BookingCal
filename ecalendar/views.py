import time
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from bookingCal.ecalendar.models import Entry
from django.core.context_processors import request, csrf
from datetime import timedelta, datetime, date, tzinfo
import calendar
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from StdSuites.Type_Names_Suite import null


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
    lst =[]

    #create a list of months for each year, indication ones that contain entries and current
    for y in [year, year+1, year +2]:
        mlst=[]
        for n, month in enumerate(mnames):
            entry = current = False #and there entry for this month ; current mont?
            entries = Entry.objects.filter(date__year=y, date__month=n+1)

            if entries:
                entry = True
            if y == nowy and n+1 == nowm:
                current = True
            mlst.append(dict(n=n+1, name=month, entry=entry, current=current))
        lst.append((y, mlst))
    return render_to_response("ecalendar/index.html", dict(years=lst, year=year,
                                                   reminders=reminders(request)))

def month(request,year,month,change=None):
    """Listinng of days in 'month'. """
    year,month = int(year),int(month)

    #apply next/previos change
    if change in ("next", "prev"):

        if change == "next":
            now, mdelta = date(year, month, 1),timedelta(days=31)
            mod = mdelta
        elif change == "prev":
            now, mdelta = date(year, month, 1),timedelta(1)
            mod = -mdelta

        year, month = (now+mod).timetuple()[:2]

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
            fday=day
            checktime = datetime(year, month, fday)

            a=Entry.objects.all()
            entries=[]
            for en in a:
                startdate=datetime(en.date.year, en.date.month, en.date.day)
                enddate=datetime(en.enddate.year, en.enddate.month, en.enddate.day)

                if startdate<=checktime and enddate >=checktime:
                    check = Entry.objects.get(id=en.id)
                    if len(entries)==3:
                        check.title="and more"
                        entries.append(check)
                        break

                    entries.append(check)


            if day == nday and year == nyear and month == nmonth:
                current = True


        lst[week].append((day, entries, current))
        if len(lst[week]) == 7:
            lst.append([])
            week += 1


    return render_to_response("ecalendar/month.html", dict(year=year, month=month, month_days=lst, mname=mnames[month-1]))

def day(request, year, month, day):
    year,month,day = int(year),int(month),int(day)

    if day:
        fday=day
        checktime = datetime(year, month, fday)

        a=Entry.objects.all()
        entries=[]
        for en in a:
            startdate=datetime(en.date.year, en.date.month, en.date.day)
            enddate=datetime(en.enddate.year, en.enddate.month, en.enddate.day)

            if startdate<=checktime and enddate >=checktime:
                check = Entry.objects.get(id=en.id)
                entries.append(check)


    return render_to_response("ecalendar/day.html", dict(year=year, month=month, day=day, entries=entries))

def event(request, evid):

    if evid:
        entries= Entry.objects.get(id=evid)

    return render_to_response("ecalendar/event.html", dict(entries=entries))
