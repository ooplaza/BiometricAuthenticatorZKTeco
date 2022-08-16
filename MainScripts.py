import tkinter
import tkinter.ttk
import mysql.connector
import customtkinter
from threading import *
from zk import *
from tkinter import messagebox
from tkinter import *


class BiometricAuthenticator(Thread):
    def __init__(self):
        """Initializing attributes."""
        self.ip_address_entry = None
        self.port_entry = None
        self.timeout_entry = None
        self.host_entry = None
        self.database_entry = None
        self.username_entry = None
        self.password_entry = None
        self.frame1 = None
        self.text_status = ""
        self.screen = None
        self.screen_configuration()

    def screen_configuration(self):
        """This function is responsible for the self.screen configuration"""
        # Screen and Notebook Configurations
        self.screen = Tk()
        self.screen.title("Biometrics Configurations")
        my_notebook = tkinter.ttk.Notebook(self.screen)
        my_notebook.pack()
        self.frame1 = Frame(my_notebook, width=500, height=250)
        frame2 = Frame(my_notebook, width=500, height=250)
        self.frame1.pack(fill="both", expand=1)
        frame2.pack(fill="both", expand=1)

        # Designate the Books
        my_notebook.add(self.frame1, text="Biometrics Configuration")
        my_notebook.add(frame2, text="Database Configuration")

        # Frame 1 Contents, Label and Entry
        # Label
        ip_address_label = StringVar()
        port_label = StringVar()
        timeout_label = StringVar()
        ip_address_label = Label(self.frame1, text='Ip Address:', pady=5).place(x=110, y=105)
        port_label = Label(self.frame1, text="Port:", pady=5).place(x=110, y=130)
        timeout_label = Label(self.frame1, text="Timeout", pady=5).place(x=110, y=155)

        # Entry
        self.ip_address_entry = Entry(self.frame1, width=30)
        self.ip_address_entry.place(x=185, y=110)
        self.port_entry = Entry(self.frame1, width=30)
        self.port_entry.place(x=185, y=135)
        self.timeout_entry = Entry(self.frame1, width=30)
        self.timeout_entry.place(x=185, y=160)

        # Frame 2 Contents, Label and Entry
        # Label
        host_label = Label(frame2, text="Host:", pady=5).place(x=110, y=80)
        database_label = Label(frame2, text="Database:", pady=5).place(x=110, y=105)
        username_label = Label(frame2, text="Username:", pady=5).place(x=110, y=130)
        password_label = Label(frame2, text="Password:", pady=5).place(x=110, y=155)

        # Entry
        self.host_entry = StringVar()
        self.database_entry = StringVar()
        self.username_entry = StringVar()
        self.password_entry = StringVar()
        self.host_entry = Entry(frame2, width=30)
        self.host_entry.place(x=185, y=85)
        self.database_entry = Entry(frame2, width=30)
        self.database_entry.place(x=185, y=110)
        self.username_entry = Entry(frame2, width=30)
        self.username_entry.place(x=185, y=135)
        self.password_entry = Entry(frame2, width=30)
        self.password_entry.place(x=185, y=160)

        # BUTTON
        save_config_button = customtkinter.CTkButton(self.screen, width=25, text="SAVE CONFIGURATION",
                                    command=Thread(target=self.trigger_checkValidiation).start)
        save_config_button.place(x=200, y=210)

        # Fields are autofill for BIOMETRIC AND DATABASE CONFIGURATION Everytime the Scripts get executed
        self.ip_address_entry.insert(0, "192.168.110.201")
        self.port_entry.insert(0, "4370")
        self.timeout_entry.insert(0, "1")
        self.host_entry.insert(0, "localhost")
        self.database_entry.insert(0, "hr_db")
        self.username_entry.insert(0, "root")

        # To continuously run the main frame
        self.screen.mainloop()

    def trigger_checkValidiation(self):
        """This function will trigger the check validation methods."""
        self.check_validation(self.ip_address_entry.get(), self.port_entry.get(),
                              self.timeout_entry.get(), self.host_entry.get(),
                              self.database_entry.get(), self.username_entry.get())

    def empty_entryField(self):
        """This function returns if there's an empty field."""
        error_message = messagebox.showinfo(title="Ops", message="Please don't leave any fields empty!")
        return error_message

    def success_entry(self, USER_ID, TIMESTAMP):
        """This function returns when the configuration is success."""
        success_message = messagebox.showinfo(title="Configuration Success", message=f"User ID: {USER_ID}\nTimestamp:"
                                                                                     f"{TIMESTAMP}")
        return success_message

    def configuration_success(self):
        """This function will trigger when successfully configured the biometric and database."""
        configuration_success = messagebox.showinfo(title="Success", message="Configuration Saved!")
        return configuration_success

    def show_error(self, error_message):
        """This function will be returning some error."""
        error_message = messagebox.showerror(title="Error", message=f"Process terminate: {error_message}")
        return error_message

    def check_validation(self, ip, port, timeout, host, database, uname):
        """This function check for all the entry inside the Frame2"""
        frame2_list = [ip, int(port), int(timeout), host, database, uname]
        for entry in frame2_list:
            if entry == "":
                self.empty_entryField()
            else:
                print(type(entry))
                # Display Connection Indicator
                configuration = Label(self.screen, text="Connected...", pady=5).place(x=240, y=240)

                # CALL zk_connection
                self.zk_connection()

    def zk_connection(self):
        """This function is use for connectivity from ZK_CONNECTION to DATABASE"""
        conn = None
        zk = ZK(str(self.ip_address_entry.get()), int(self.port_entry.get()), int(self.timeout_entry.get()),
                self.password_entry.get(), force_udp=False, ommit_ping=False)

        # MySql Connection
        my_connection = mysql.connector.connect(
            host=str(self.host_entry.get()),
            user=self.username_entry.get(),
            passwd=self.password_entry.get(),
            database=self.database_entry.get())

        cursor = my_connection.cursor()

        try:
            conn = zk.connect()
            # Disable Device to ensure no activity on the device while the process is running
            conn.disable_device()
            for attendance in conn.live_capture():
                if attendance is None:
                    pass
                else:
                    print(f"{attendance}")
                    attUser_id = attendance.user_id
                    attDate = attendance.timestamp

                    # INSERT INTO DB
                    SQL_QUERY_ADD = "INSERT INTO biometric_datas (biometric_id, date_time) VALUES (%s, %s)"
                    VAL = (attUser_id, attDate)

                    # EXECUTE
                    cursor.execute(SQL_QUERY_ADD, VAL)
                    my_connection.commit()

                    # Display USER_ID and TIMESTAMP
                    # Update every after Authenticated
                    attendance_userID = Label(self.screen, text=f"User ID: {attUser_id}", pady=5).place(x=160, y=40)
                    attendance_date = Label(self.screen, text=f"User Attendance: {attDate}", pady=5).place(x=160, y=60)
                    self.screen.update()

                    # # RE-ENABLE THE CONNECTED DEVICE TO ALLOW CONNECTIVITY AGAIN
            conn.test_voice()
            conn.enable_device()

        except Exception as message:
            self.show_error(message)
            print(message)

        except KeyboardInterrupt:
            # Trigger when Disconnected from running
            print("Keyboard Interrupt Handled!")

        except zk.exception.ZKErrorResponse:
            print("Can't Disconnect Error Handled!")

        finally:
            conn.disconnect()


if __name__ == "__main__":
    Threaded = BiometricAuthenticator()
