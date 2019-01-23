from app.utils.gappshelper import GappsHelper
import time
from datetime import datetime, date, timedelta

from config import get_env

import inspect


class Actions:
    def __init__(self, slackhelper, user_info=None):
        self.gappshelper = GappsHelper()
        self.file = self.gappshelper.client.open(get_env("GAPPS_SHEET_NAME")).sheet1
        self.sheet = self.gappshelper.open_sheet()
        self.user_info = user_info
        self.slackhelper = slackhelper
        self.months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

    
    def make_months_dict(self, months):
        ms = dict()
        count = 0
        while True:
            ms[months[count]] = count
            count += 1
            if count == 12:
                break
        return ms

    def __num_suffix(self, check_in_date):
        """
        Strip the date suffix and return the date
        Before comparing the date
        """
        date_value = str(check_in_date).split(' ')
        day_value = date_value[0][:-2]
        date_value[0] = day_value
        return ' '.join(date_value)

    def __convert_to_date(self, date_string):
        today = date.today()
        if date_string == today:
            return today
        elif date_string == "yesterday":
            return today - timedelta(day=1)
        else:
            if date_string == "tomorrow":
                return today + timedelta(day=1)

    def __perform_send_action(self, task_cells):
        recipient = self.user_info["user"]["id"]
        for index, row in enumerate(task_cells):
            task_id, next_checkin, name = str(index + 1), row['Next Check-In'], row['Name']
            learned = row['Most Recent Learning Experience you\'d like to write about']
            text_detail = (
                f"*Task #{task_id} for {next_checkin}:* \n\n"
                f"*Hey {name},* Today is the check-in day for your writeup titled\n"
                f"`{learned}`.\n\n"
                "Whats the status of the article?\n"
                "PS: Please reply to this thread, the managers will review and reply you ASAP")
            self.slackhelper.post_message(text_detail, recipient)
        return None


    def show_tasks(self, date=None):
        if date in ["today", "tomorrow", "yesterday"]:
            day_date_param = self.__convert_to_date(date)
            task_cells = list(filter(lambda x: datetime.strptime(self.__num_suffix(x['Next Check-In']), '%d %B %Y').date() == day_date_param, self.sheet))
            if task_cells:
                self.__perform_send_action(task_cells)
            else:
                return {"text": f"No task assigned to be checked in {date}, try another date"}
        else:
            date_param = date.replace("-", " ")
            task_cells = list(filter(lambda x: x['Next Check-In'] == date_param, self.sheet))
            if task_cells: 
                self.__perform_send_action(task_cells)
            else:
             return {"text": "No task assigned to be checked in on this date, try another date"}

    def help(self):
        """
        Return the available commands that a user can use
        """
        recipient = self.user_info['user']['id']
        text_detail = (
                'Available Commands: \n `/ranti my-task e.g. /ranti my-task` \n To get task assigned to you.\n'
                ' \n `/ranti show-task [date]{dth-month-year} e.g. /ranti show-task 5th-june-2018` \n Show all tasks for a particular date \n'
                '\n `/ranti show-task [today] e.g. /ranti show-task today` \n Show all tasks for today \n'
                '\n `/ranti show-task [tomorrow] e.g. /ranti show-task tomorrow` \n Show all tasks for tomorrow \n'
                '\n `/ranti help` \n This help information \n \n Miyagi Ver: 1.0')

        self.slackhelper.post_message(text_detail, recipient)
        return None

    def my_tasks(self):
        email = self.user_info["user"]["profile"]["email"]
        recipient = self.user_info['user']['id']
        task_cells = list(filter(lambda x: x["Email Address"] == email, self.sheet))
        for index, row in enumerate(task_cells):
            index, checkin, name = str(index + 1), row['Next Check-In'], row['Name']
            learnigs = row['Most Recent Learning Experience you\'d like to write about']
            text_detail = (
                f"*Task #{index} for {checkin}:* \n\n"
                f"*Hey {name},* Today is the check-in day for your writeup titled\n"
                f"`{learnigs}`.\n\n"
                "Whats the status of the article?\n"
                "PS: Please reply to this thread, the managers will review and reply you ASAP"
            )
            self.slackhelper.post_message(text_detail, recipient)
        return None

    def update_sheet(self):
        # writer = self.user_info['user']['id']
        writer = "cedriclusiba@gmail.com"
        my_tasks = list(filter(lambda x: x["Email Address"] == writer, self.sheet))
        print(f"my tasks now: {my_tasks}\n\n")
        for task in my_tasks:
            if task["Next Check-In"] == "5th june 2018" :

                print(f"Changing task {task!r}\n\n")

                task["Most Recent Learning Experience you'd like to write about"] = "I learnt React Native. I enjoyed learning it!"
        print(f"my tasks after: {my_tasks}\n\n")

        print("this runs but ehh>>>", self.sheet[0], "\n\n")
        l = list(self.sheet)
        
        print(">>>>????", self.file.acell("C2"), self.file.row_values(2)[2])
        # self.file.acell("C2").value = "I learnt React Native. I enjoyed learning it!"
        self.file.update_acell("C2", "I learnt React Native. I enjoyed learning it!")

        print("\n\n>>>>>>>>>>", self.file.row_values(2)[2])
        # index = 0
        # for row in l:
        #     print(self.sheet.row_values(index +1), "\n\n")
        #     print( row,"\n\n", index)
        #     if row["Email Address"] == writer and row["Next Check-In"] == "5th june 2018":
        #         x = index
        #         print("this runs>>>", index)
        #         self.sheet[index]["Most Recent Learning Experience you'd like to write about"] = "I learnt React Native. I enjoyed learning it!"
        #         print("this runs here too>>>", x)
        #         index += 1
        # print(f"Updated sheet row =: {self.sheet[x]}")

        return my_tasks

    def welcome(self):
        recipient = self.user_info['user']['id']
        text_detail = "Welcome to the miyagi-bot, type `/miyagi help` to see a list of available commands"
        self.slackhelper.post_message(text_detail, recipient)
        return None


    def notify_channel(self):
        print('Worker is running..., waiting till 8:00')
        while True:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute

            
            if current_hour - 8 > 0:
                sleep_time = 24 - current_hour + 8 - (current_minute/60)
            elif current_hour - 8 < 0:
                sleep_time = 8 - current_hour - (current_minute/60)
            elif current_hour == 8 and current_minute == 0:
                    sleep_time = 0
            else:
                if current_minute != 0:
                    sleep_time = 24 - current_hour + 8 - (current_minute/60)


            for index, row in enumerate(self.sheet):
                
                months = self.make_months_dict(self.months)

                day = len(str(row["Next Check-In"][0])) > 1 and str(row["Next Check-In"][0]) or "0" + str(row["Next Check-In"][0])
                month = str(self.months.index(row["Next Check-In"][3: 7].strip()))
                month_str = len(month) > 1 and month or "0" + month
                
                date_string = day +"/"+ month_str +"/"+str(row["Next Check-In"][9:])
                check_date = datetime.strptime(date_string, "%d/%m/%Y").date()
                
                todays_date = datetime.now().date()
                send_notif_date = check_date - todays_date

                if send_notif_date != 0:
                    id_no, checkin, name = str(index + 1), row["Next Check-In"], row["Name"]
                    title = row["Most Recent Learning Experience you\'d like to write about"]
                    text_detail = (
                        f"*Task #{id_no} for {checkin}:* \n\n"
                        f"*Hey {name},* Today is the check-in day for your writeup titled\n"
                        f"`{title}`.\n\n"
                        'Whats the status of the article?\n'
                        'PS: Please reply to this thread, the managers will review and reply you ASAP')
                    
                    self.slackhelper.post_message_to_channel(text_detail)


                print('message sent or no tasks for today-waiting till 8:00a.m next day')  
                # time.sleep(3600)
 
                time.sleep(sleep_time * 3600)
        


