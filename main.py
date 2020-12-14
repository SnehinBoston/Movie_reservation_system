import pymysql.cursors
import getpass
import pandas as pd
from datetime import datetime
import csv

# Cover every input statement with try/catch blocks.
def user_registration(table):
    # connection = pymysql.connect(host='localhost',user='admin',password='password',db='movie_project',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
    cur  = connection.cursor()
    while(1):
        email = input("Enter the email: ")
        stmt = "select emailId from {table};".format(table = "`"+table+"`")
        cur.execute(stmt)
        rows = cur.fetchall()
        registered = False

        for mail in rows:
            # If the user has registered already
            if email == mail['emailId']: 
                password = getpass.getpass("Enter the password: ")

                check_pass = 'select password from {tab} where emailId={em};'.format(tab = "`"+table+"`",em = '"'+email+'"')
                
                cur.execute(check_pass)
                row = cur.fetchone()
                registered = True

                if row['password'] == password:
                    print("Login successful!")
                    return email
                else:
                    print("Wrong password.")
                    break
        # If not register the user
        if registered == False:
            print("Please give registration information")
            name = input("Enter the username: ")
            phone = input("Enter the phone number: ")
            password = getpass.getpass("Enter the password: ")
            stmt = "insert into {tab} values({em},{nm},{ph},{pwd});".format(tab = ("`"+table+"`"),em = "'"+email+"'", nm = "'"+name+"'", ph = "'"+phone+"'", pwd = "'"+password+"'")
            cur.execute(stmt)
            connection.commit()
            return email

def split_days(x):
    return str(x).split('days')[1]

def movie_view(email="abc@gmail.com"):
    connection = pymysql.connect(host='localhost',user='admin',password='password',db='movie_project',charset='utf8',cursorclass=pymysql.cursors.SSDictCursor)
    cur  = connection.cursor()
    print("Let's book tickets.")
    while(1):
        day = input("Enter the day: ")
        if day.lower() in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
            day = day.lower()
            
            cur.callproc("shows_display",args=[day])
            
            rows = cur.fetchall()
            keys = rows[0].keys()
            output_file = open('shows_d.csv', 'w', newline='')
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(rows)
            print(rows)
            shows_disp = pd.read_csv('shows_d.csv',header=None,delim_whitespace=True)
            
            # print(shows_disp)
            shows_disp['startTime'] = shows_disp['startTime'].apply(split_days)
            shows_disp['endTime'] = shows_disp['endTime'].apply(split_days)
            # Remove days using string manipulation
            
            while(1):
                try:
                    entry = int(input("Select a number from the show list: "))
                    if entry < len(shows_disp):
                        break
                    else:
                        print(f"Enter a number between 1 and %s",len(shows_disp))
                        continue
                except:
                    print(f"Enter a number between 1 and %s",len(shows_disp))
            
            theatreName,movieName,startTime, endTime = shows_disp.iloc[entry]
            # Search up the show_id list.
            
            stmt = "call select_show(%s,%s,%s,%s,%s)"
            cur.execute(stmt,(theatreName,movieName,str(startTime), str(endTime),day))
            shows = cur.fetchall()
            # print("These are the shows: ",pd.DataFrame(shows))
            stmt = "ALTER TABLE available_seats ORDER BY seatId ASC;"
            cur.execute(stmt)
            # Selecting from a class of tickets.
            stmt = "select seatId from seats;"
            cur.execute(stmt)
            
            seatClass = input("Select a class of tickets: ")
            num_ticket = int(input("Enter the number of tickets: "))
            # print(shows)
            bookable = False
            for i in range(0, len(shows)):
                # Lists the number of available seats   
                stmt = """select sum(availability) as vacant_seat_count from available_seats where showId = %s and availability = 1 and (seatId like %s);"""
                cur.execute(stmt,(shows[i]['showId'],seatClass+"%"))
                seat_count = cur.fetchall()
                if num_ticket <= int(seat_count[0]['vacant_seat_count']):
                    # Shows a list of available seats
                    count = 0
                    ticket_ids = []
                    bookable = True
                    while count < num_ticket:
                        stmt = """select seatId from available_seats where showId = %s and availability = 1 and (seatId like %s);"""
                        cur.execute(stmt,(shows[i]['showId'],seatClass+"%"))
                        available_seats = cur.fetchall()
                        vac_seats = []
                        for seat in available_seats:
                            vac_seats.append(seat['seatId'])
                        print("Available seats: ",vac_seats)
                        ###### DO VALIDATION OF ENTERED SEAT NUMBER
                        booked_seat = input("Select a seat number: ")
                        holdName = input("Enter the holder name: ")
                        # Check for availability. 
                        # Iterate through available seats and check for booked seat.
                        if booked_seat in vac_seats:
                            # Passing holdName, showId, seatId, email
                            # Make book tickets a function and return tid
                            stmt = "call book_tickets(%s,%s,%s,%s)"
                            cur.execute(stmt, (holdName, int(shows[i]['showId']),booked_seat,email))
                            stmt = "select ticketId from ticket order by ticketId desc limit 1;"
                            cur.execute(stmt)
                            ticket_ids.append(str(cur.fetchall()[0]['ticketId']))
                            count+=1
                    
                    stmt = "select * from ticket where ticketId in %s"
                    cur.execute(stmt, (tuple(ticket_ids),))
                    data = pd.DataFrame(cur.fetchall())
                    print("Here are your tickets\n")
                    print(data.to_string())
                    return 
            if not bookable:
                print("Tickets cannot be booked.")
                continue
        else:
            print("Incorrect day entered.")            

def Theatre():
    print("In function theatre")
    arg = input("Select the operation: 1. Insert\n2. Update\n3. Delete")
    cur = connection.cursor()
    if arg == '1':
        while(1):
            theName = input("Enter theatreName: ")
            stmt = "insert into theatre(theatreName) values(%s);"
            try:
                cur.execute(stmt,theName.upper())
                connection.commit()
                break
            except:
                print("Duplicate record found.")
                continue
        stmt = "select theatreId from theatre order by theatreId desc limit 1;"
        cur.execute(stmt)
        Hall(arg,cur.fetchone()['theatreId'])
        print("Theatres have been inserted.")
    elif arg == '2':
        stmt = "select theatreId, theatreName from theatre;"
        
        cur.execute(stmt)
        print("Select the theatreId to update: \n",pd.DataFrame(cur.fetchall()).to_string())
        
        # CHECK IF THEATRE ID IS LESS THAN THE LARGEST THEATREIDS.
        oldthId = input()

        while(1):
            theName = input("Enter new theatreName: ")
            try:
                stmt = "update theatre set theatreName = %s  where theatreId = %s;"
                cur.execute(stmt, (theName,oldthId))
                connection.commit()
                break
            except:
                print("Duplicate record found.")
                continue
        print("Theatre has been updated.")
    
    elif arg == '3':
        stmt = "select theatreId, theatreName from theatre;"
        cur.execute(stmt)
        print("Select the theatreId to delete: ",pd.DataFrame(cur.fetchall()).to_string())
        oldthId = input()
        Hall(3,oldthId)
        stmt = "delete from theatre where theatreId = %s;"
        cur.execute(stmt, oldthId)
        connection.commit()
        print("Theatre has been deleted.")


def Hall(arg=None,thId=None):
    cur = connection.cursor()
    if not arg:
        arg = input("Select the operation: 1. Insert\n2. Update\n3. Delete")
    if arg == '1':
        # hallId, hallName
        if not thId:
            table = "theatre"
            stmt = f"select * from %s;"%table
            cur.execute(stmt)
            data = pd.DataFrame(cur.fetchall())
            print(data.to_string())
            thId = input("Select a theatreId from the above theatre list ")
        no_halls = int(input("Enter the number of halls: "))
            
        for i in range(0,no_halls):
            while(1):
                try:
                    hName = input("Enter the hall name: ")
                    stmt = "insert into Hall(hallName,theatreId) values(%s,%s);"
                    cur.execute(stmt,(hName,int(thId)))
                    connection.commit()
                    break
                except Exception as e:
                    print(e)
                    continue
            stmt = "select hallId from Hall order by hallId desc limit 1;"
            cur.execute(stmt)
            Shows(arg, int(cur.fetchone()['hallId']))
        print("Halls have been inserted.")
    
    elif arg == '2':
        stmt = "select hallId, hallName from Hall;"
        cur.execute(stmt)
        print("Select the hallId to update halls: \n",pd.DataFrame(cur.fetchall()).to_string())
        oldhId = input()
        while(1):
            try:
                hName = input("Enter new hall name: ")
                stmt = "update hall set hallName = %s  where hallId = %s;"
                cur.execute(stmt, (hName,oldhId))
                connection.commit()
                break
            except:
                print("Duplicate record found.")
                continue
        print("Hall has been updated.")

    elif arg == '3':
        if thId:
            stmt = "delete from Hall where theatreId = %s;"
            cur.execute(stmt,thId)
            connection.commit()
        else:
            stmt = "select hallId, hallName from Hall;"
            cur.execute(stmt)
            print("Select the hallId to delete: \n",pd.DataFrame(cur.fetchall()).to_string())
            oldhId = input()
            Shows(arg,oldhId)
            stmt = "delete from hall where hallId = %s;"
            cur.execute(stmt, oldhId)
            connection.commit()
            print("Delete from Hall completed.")

def Movie(arg=None):
    cur = connection.cursor()
    if not arg:
        arg = input("Select the operation: 1. Insert\n2. Update\n3. Delete")
    if arg == '1':
        while(1):
            try:
                movName = input("Enter the movie name: ")
                direc = input("Enter the director's name: ")
                actors = input("Enter the actors name: ")
                stmt = "insert into movie(movieName, director, actors) values(%s,%s,%s);"
                cur.execute(stmt,(movName, direc, actors))
                connection.commit()
                stmt = "select movieId from Movie order by movieId desc limit 1;"
                cur.execute(stmt)
                Shows(arg,None,int(cur.fetchone()['movieId']))
                break
            except:
                print("Duplicate record found.")
                continue
        print("Movie has been inserted.")
    elif arg == '2':
        stmt = "select movieId, movieName from movie;"
        cur.execute(stmt)
        print("Select the movieId to update: \n",pd.DataFrame(cur.fetchall()).to_string())
        oldmId = input()
        while(1):
            try:
                mName = input("Enter new movie name: ")
                director = input("Enter the name of director: ")
                actors = input("Enter the name of actors: ")
                stmt = "update movie set movieName = %s,director = %s, actors = %s where movieId = %s;"
                cur.execute(stmt, (mName,director,actors,oldmId))
                connection.commit()
                break
            except:
                print("Duplicate record found.")
                continue
        print("Movie has been updated.")
    elif arg == '3':
        stmt = "select * from movie;"
        cur.execute(stmt)
        print("Select the movieId to delete: \n",pd.DataFrame(cur.fetchall()).to_string())
        oldmId = input()
        Shows(arg, None,oldmId)
        stmt = "delete from movie where movieId = %s;"
        cur.execute(stmt, oldmId)
        connection.commit()
        print("Movie has been deleted.")

def validate(time_text):
    try:
        if time_text != datetime.strptime(time_text, "%H:%M:%S").strftime('%H:%M:%S'):
            raise ValueError
        return True
    except ValueError:
        return False

def validate_week(day):
    small_day = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    try:
        if day.lower() not in small_day:
            raise ValueError
        return True
    except ValueError:
        return False

def Shows(arg=None, hId=None, mId = None):
    
    cur = connection.cursor()
    if not arg:
        arg = input("Select the operation: 1. Insert\n2. Update\n3. Delete")
    if arg == '1':
        no_shows = int(input("Enter the number of shows: "))
        for i in range(0,no_shows):
            while(1):
                stTime = input("Enter the start time of show(hh:mm:ss): ")
                if validate(stTime):
                    break
                else:
                    print("Please enter the start time in the format(hh:mm:ss)")
                    
            while(1):
                edTime = input("Enter the end time of show(hh:mm:ss): ")
                if validate(edTime):
                    break
                else:
                    print("Please enter the end time in the format(hh:mm:ss)")
            while(1):
                wkday = input("Enter the day: ")
                if validate_week(wkday):
                    break
                else:
                    print("Please enter the weekday in the correct format")
            # Directly choosing from the previous movie list or adding a new movie.
            
            # yn = input("Do you want to enter a new movie?[Y/N]")
            # if yn.lower()=='y' or yn.lower() == 'yes':
            #     while(1):
            #         try:
            #             movn = input("Enter new movie name: ")
            #             direc = input("Enter director name: ")
            #             actors = input("Enter actors name:")
            #             stmt = "insert into movie(movieName, director,actors) values(%s,%s,%s);"
            #             cur.execute(stmt,(movn,direc,actors))
            #             connection.commit()
            #         except:
            #             print("Duplicate record found.")
            #             continue
                
                stmt = "select movieId from movie order by movieId desc limit 1;"
                cur.execute(stmt)
                movId = cur.fetchone()['movieId']
            else:
                cur = connection.cursor()
                stmt =  "select * from movie;"
                cur.execute(stmt)
                print("select a movie from the following: \n",pd.DataFrame(cur.fetchall()))
                movId = int(input()) 
            if not hId:
                stmt = "select hallId from hall;"
                cur.execute(stmt)
                print("select a hall from the following: \n",cur.fetchall())
                hallId = int(input()) 
            else:
                hallId = hId
            
            if not mId:
                stmt = "select movieId from movie;"
                cur.execute(stmt)
                print("select a movieId from the following: \n",cur.fetchall())
                movId = int(input()) 
            else:
                movId = mId
            while(1):
                try:
                    stmt = "insert into shows(startTime, endTime, `weekday`, movieId, hallId) values(%s,%s,%s,%s,%s);"
                    cur.execute(stmt,(stTime,edTime,wkday,movId,hallId))
                    connection.commit()
                    break
                except:
                    print("Duplicate records found.")
                    return
            print("Show has been inserted.")
    elif arg == '2':
        stmt = "select * from shows;"
        cur.execute(stmt)
        print("Select the showId to update shows: ",pd.DataFrame(cur.fetchall()).to_string())
        oldshId = input()
        while(1):
            try:
                stTime, etime, wkday, mId, hId = input("Enter startTime, endTime, weekday, movieId, hallId: ").split()
                stmt = "update shows set startTime = %s,endTime = %s, weekday = %s, movieId = %s, hallId = %s where showId = %s;"
                cur.execute(stmt, (stTime,etime,wkday,mId,hId,oldshId))
                connection.commit()
                break
            except:
                print("Duplicate records found.")
                continue
        print("Show has been updated.")
    elif arg == '3':
        if hId:
            stmt = "select showId from Shows where hallId = %s"
            cur.execute(stmt,hId)
            list_ = cur.fetchall()
            show_list = []
            for show in list_:
                show_list.append(str(show['showId']))
            # print(show_list)
            print(show_list)
            format_strings = ','.join(['%s'] * len(show_list))
            try:
                cur.execute("delete from available_seats where showId in (%s);" % format_strings, tuple(show_list))
                cur.execute("delete from Shows where showId in (%s);" % format_strings,tuple(show_list))
                connection.commit()
                print("Show has been deleted.")
            # stmt = "delete from Shows where hallId = %d;"
            except:
                print("There are no available shows in this hall.")
            
        elif mId:
            stmt = "select showId from Shows where movieId = %s"
            cur.execute(stmt,mId)
            list_ = cur.fetchall()
            show_list = []
            for show in list_:
                show_list.append(str(show['showId']))
            format_strings = ','.join(['%s'] * len(show_list))
            try:
                cur.execute("delete from available_seats where showId in (%s);" % format_strings, tuple(show_list))
                connection.commit()
            except:
                print("There are no available shows for this movie.")
            # print("delete from Shows where showId in (%s);" % format_strings,tuple(show_list))
            cur.execute("delete from Shows where showId in (%s);" % format_strings,tuple(show_list))
            connection.commit()
            print("Show has been deleted.")

        else:
            stmt = "select * from shows;"
            cur.execute(stmt)
            print("Select the showId to delete: \n",pd.DataFrame(cur.fetchall()).to_string())
            oldshId = input()
            cur.execute("delete from available_seats where showId = (%s);", oldshId)
            connection.commit()
            stmt = "delete from shows where showId = %s;"
            cur.execute(stmt, oldshId)
            connection.commit()
            print("Show has been deleted.")

def Seats(arg=None):
    cur = connection.cursor()
    if not arg:
        arg = input("Select the operation: 1. Insert\n2. Update")
    if arg == '1':
        # SeatId, Price
        ## CHECK FOR SEAT SERIES OTHER THAN A, B AND C
        while(1):
            try:
                sId = input("Enter the seat series: ")
                price = input("Enter the price: ")
                break
            except:
                print("Duplicate records found.")
                continue
        try:
            for i in range(1,10):
                cur.execute("insert into seats values('%s0%s',%s);"%(sId,i,price))
                connection.commit()
            for i in range(10,31):            
                cur.execute("insert into seats values('%s%s',%s);"%(sId,i,price))
                connection.commit()
        except:
            print("Duplicate records found.")
            return
        print("Seats have been inserted.")
    elif arg == '2':
        while(1):
            try:
                sId = input("Enter the seat series: ")
                price = input("Enter the price: ")
                stmt = "update seats set price = %s where seatId like %s;"
                cur.execute(stmt, (price,sId+'%'))
                connection.commit()        
                break
            except:
                print("Duplicate records found.")
                continue
        print("Seats have been updated.")
    
def numbers_to_write_table(argument):
    switcher = {
        "1": Theatre,
        "2": Hall,
        "3": Movie,
        "4": Shows,
        "5": Seats
    }
    # Get the function from switcher dictionary
    # print(argument)
    # Execute the function
    func = switcher.get(argument, lambda: "Invalid month")
    func()

def numbers_to_read_table(argument):
    switcher = {
        '1': "Theatre",
        '2': "Hall",
        '3': "Movie",
        '4': "Shows",
        '5': "Seats",
        '6': "user"  
    }
    # Get the function from switcher dictionary
    table = switcher[argument]
    # Execute the function
    # print(f"This is switcher: %s"%table)
    cur = connection.cursor()
    stmt = f"select * from %s;"%table
    cur.execute(stmt)
    data = pd.DataFrame(cur.fetchall())
    print(data.to_string())

def interesting_queries():
    # Interesting queries
    # Shows availability of a particular seat class of tickets for a show.
    stmt = """select sum(availability) as vacant_seat_count from available_seats where showId = %s and availability = 1 and (seatId like %s);"""
    cur.execute(stmt,(50,'A'+"%"))
    seat_count = cur.fetchall()
    print(pd.DataFrame(seat_count).to_string())
    # Displays shows with a particular starttime, endtime, weekday and movieId across all halls and theatres.
    stmt = """select showId from shows where (startTime = %s and endTime = %s and `weekday` = %s and movieId = %s;"""
    cur.execute(stmt,('12:00:00','15:00:00','Monday','2'))
    shows = cur.fetchall()
    print(pd.DataFrame(shows).to_string())
    # Displays all the tickets bought for a particular show.
    stmt = ""

connection = pymysql.connect(host='localhost',user='admin',password='password',db='movie_project',charset='utf8',cursorclass=pymysql.cursors.DictCursor,autocommit=True)

if __name__ == "__main__":
    
    while(1):
        person = input("Choose the type of user: 1. User 2. Admin")
        if person == 1 or person == '1':
            while(1):
                # email = user_registration(table = "user")
                movie_view()
                break
        elif person == 2 or person == '2':
            # email = user_registration(table = "admin")
            while(1):
                operations = input("Select one of the following: 1. Read records. 2. Insert/Update/Delete records")
                if operations == '1':
                    arg = input("Select the table: 1. Theatre\n2. Hall\n3.Movie\n4.Shows\n5.Seats\n6.User")
                    numbers_to_read_table(arg)
                elif operations == '2':
                    arg = input("Select the table: 1. Theatre\n2. Hall\n3.Movie\n4.Shows\n5.Seats")
                    numbers_to_write_table(arg)