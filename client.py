import tkinter as tk  
from tkinter import ttk 
import asyncio
from CSC import ClientServerSocket
import _thread


class Application(tk.Tk):

    def __init__(self, *args):
        super().__init__(*args)  


        self.title("Tic Tac Toe ITacademy")
        self.minsize(700, 600)
        container = tk.Frame(self)
        self.PreviousFrame =  None

        # use full width and height and fill it. define the columbs and rows
        container.pack(side="top", fill="both", expand=True, anchor='center')
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # set the socket server connection variable to None, with will be initialize the ClientServerSocket class once the user successfully authenticates
        self.SocketConnection: ClientServerSocket = None
        self.frames = {}
        #open all tk.frames and return them one by one on the other
        for FView in (HomePage, JoinGamePage, GamePage, LeaderBoardPage, AuthenticationPage):
            # makes referance to the frame class and gave him required info. container is passed down tk. and the single view is updating every time when you switch views
            frame = FView(container, self)
            # saves the instance in self.frames
            self.frames[FView] = frame
            # adds the initial widget rendered.

        # Goes to the login page
        self.PreviousFrame = self.frames[AuthenticationPage]
        self.switch_frame_to(AuthenticationPage)

    def switch_frame_to(self, frame: tk.Frame):

        #This function allows navigation between frame (views).
        # tries to find the frame instance in self.frames
        frame = self.frames[frame]
        if frame != None:  # check if there is an initialize frame that has been created.
            self.PreviousFrame.grid_remove() # remove the last frame so the page will resize to best fit heigh and width
            frame.grid(row=0, sticky="news")
            self.PreviousFrame = frame
            # then re-build the frame but with the new frame.
            frame.render()  # each frame view should have this method, it allows me to re-render views with updated Data
            frame.tkraise()  # brings the fram to the front of the window.
        return

    def authenticate_user(self, Frame: tk.Frame, userCredentials, socketHostData):
        """
        Connect to the server socket by passing the address and port to ClientServerSocket.
        Then try to authenticate the client by passing user credentials in the login function in the CSS class.
        """
        try:
            if ((len(userCredentials[0]) > 0) and (len(userCredentials[1]) > 5)):
                print("Attempt to authenticate client", userCredentials[0])
                # initialize the CSS class and point to the socket server with its address and port
                self.SocketConnection = ClientServerSocket(socketHostData)
                # attempt to authenticate the client and wait for the login function to return.
                result = asyncio.run(
                    self.SocketConnection.login(userCredentials))
                if self.SocketConnection.isAuth == True:
                    print("Clinet authenticated: True")
                    # Switch to the home page
                    Frame.err_label.grid_remove()
                    self.switch_frame_to(HomePage)                    
                    return
                else:
                    print("Clinet authenticated: Fail")
                    # Display any additional information
                    Frame.ERROR_MSG.set(result)
                    Frame.err_label.grid()
            else:
                # display error message
                Frame.ERROR_MSG.set("Password must be 6 characters or more" if (len(
                    userCredentials[0]) > 0) else "Username must be 1 character or more")
                Frame.err_label.grid()
        except ConnectionError as e:
            print(e)
            Frame.ERROR_MSG.set("Can't Reach the Server Socket")
            Frame.err_label.grid()

    def register_user(self, Frame: tk.Frame, userCredentials, socketHostData):

        try:
            if ((len(userCredentials[0]) > 0) and (len(userCredentials[1]) > 5)):
                print("Attempt to create new user account", userCredentials[0])
                # initialize the CSS class 
                self.SocketConnection = ClientServerSocket(socketHostData)
                result = asyncio.run(
                    self.SocketConnection.register(userCredentials))  # attempt to create a new user in the database and wait for the register function to return.
                # Display any additional information
                Frame.ERROR_MSG.set(result)
                Frame.err_label.grid()
            else:
                # display error message
                Frame.ERROR_MSG.set("Password must be 6 characters or more") if (len(
                    userCredentials[0]) > 0) else Frame.ERROR_MSG.set("Username must be 1 character or more")
                Frame.err_label.grid()

        except ConnectionError as e:
            print(e)
            Frame.ERROR_MSG.set("Can't Reach the Server Socket")
            Frame.err_label.grid()


class HomePage(tk.Frame):  # inherit from the tk frame


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # inits the inherited frame class
        # parent is the class that called this class

        self.controller = controller
        self.parent = parent
        self.ERROR_MSG = tk.StringVar()
        self.render()

    def render(self):

        if self.controller.SocketConnection != None:
            # "Welcome: " + username
            tk.Label(self, text=f"Welcome: {self.controller.SocketConnection.userData[0]}", font=(
                "arial", 15, "bold")).grid(row=0, column=0, ipadx=20, pady=10,  padx=60, sticky="news")
        tk.Button(self, text='Join A Game', font=("arial", 20, "bold"), command=lambda:  self.join_game(
        )).grid(row=1,  padx=130, ipadx=80, ipady=20, pady=10, sticky="news")
        tk.Button(self, text='Leader-board', font=("arial", 20, "bold"), command=lambda: self.controller.switch_frame_to(LeaderBoardPage)).grid(row=2,
                                                                                                                                                padx=130, ipadx=80, ipady=20, pady=90, sticky="news")
        self.err_label = tk.Label(
            self, textvariable=self.ERROR_MSG, font=("arial", 20, "bold"))
        self.err_label.grid(row=3, rowspan=2, ipadx=10, sticky="ews")

    def join_game(self):

        print("Join game queue")
        self.controller.switch_frame_to(JoinGamePage)
        # this allows the player to cancel at any time while waiting someone to join to play
        _thread.start_new_thread(self.waiting_to_Join, ())

    def waiting_to_Join(self):
        try:
            res = asyncio.run(self.controller.SocketConnection.joinGame())
        except AttributeError:  # this will send an error if client want to join party without authorize
            # send the client to the login page
            self.controller.switch_frame_to(AuthenticationPage)
            raise UserWarning("Currently not signed in")
        if self.controller.SocketConnection.isInGame is True:
            self.controller.switch_frame_to(GamePage)
            # start game loop
            asyncio.run(
                self.controller.SocketConnection.startGameLoop(self.controller.frames[GamePage]))
            self.ERROR_MSG.set("")
        else:
            self.controller.switch_frame_to(HomePage)
            self.ERROR_MSG.set(res)
        return


class JoinGamePage(tk.Frame):  # inherit from the tk frame

    #The Join game page - shown when the client attempts to join a game session and is waiting for a player to join the game.

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # inits the inherited frame class


        self.controller = controller
        self.parent = parent

        self.render()

    def render(self):
        tk.Label(self, text="Waiting For Another Player To Join...", font=("", 22,)).grid(
            row=0, column=0, columnspan=3, padx=80, ipadx=30, ipady=90, sticky="news")
        tk.Button(self, text="Cancel", font=("arial", 20, "bold"), command=self.cancel_game).grid(
            row=1, column=1, pady=20, ipadx=80, ipady=20, sticky="ews")

    def cancel_game(self):

        try:
            asyncio.run(self.controller.SocketConnection.cancelGame())
        except AttributeError:  # this will throw an error if the user manages to get un authenticated by the server and tries to leave game the queue
            # send the client to the login page
            self.controller.switch_frame_to(AuthenticationPage)
            raise UserWarning("Currently not signed in")


class GamePage(tk.Frame):  # inherit from the tk frame
    """
    The main page - run after user success loggin.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # inits the inherited frame class
        # parent is the class that called this class
        # print(self.__dict__) # shows me the attributes of this variable
        self.controller = controller
        self.parent = parent

        self.MSG = tk.StringVar()

        # render view
        self.render()

    def render(self):
        # game board section
        if self.controller.SocketConnection != None:
            gameBoard_section = tk.Frame(self)
            self.renderBoard(gameBoard_section)
            gameBoard_section.grid(sticky="news", row=0,
                                   column=0, padx=130, pady=20)
            tk.Label(self, text=f"Player 1: {self.controller.SocketConnection.gameData['player_data'][0][0]}", font=(
                "arial", 14)).grid(row=1, sticky="nsw",  padx=130)
            tk.Label(self, text=f"Player 2: {self.controller.SocketConnection.gameData['player_data'][1][0]}", font=(
                "arial", 14)).grid(row=2, sticky="nsw",  padx=130)
            tk.Label(self, text=f"Turn: Player {self.controller.SocketConnection.gameData['player_turn']}", font=(
                "arial", 14)).grid(row=3, sticky="nsw",  padx=130)

            # Setup  Message Label
            end_of_gmae_section = tk.Frame(self)

            self.end_game_btn = tk.Button(end_of_gmae_section, text="Go Back to home", font=(
                "arial", 14), command=lambda: self.controller.switch_frame_to(HomePage))
            self.end_game_btn.grid(
                row=0, column=1, ipadx=30, ipady=20, padx=10, pady=10)
            self.end_game_btn.grid_remove()
            self.msg_label = tk.Label(
                end_of_gmae_section, textvariable=self.MSG, font=("arial", 14))
            self.msg_label.grid(row=0, sticky="news")
            self.msg_label.grid_remove()
            end_of_gmae_section.grid(row=4, sticky="news")

    def renderBoard(self, boardSection):

        for row in range(len(self.controller.SocketConnection.gameData["board"])):
            for column in range(len(self.controller.SocketConnection.gameData["board"][row])):
                slotState = self.controller.SocketConnection.gameData["board"][row][column]
                if slotState == 2:
                    tk.Button(boardSection, text='X', state="disabled").grid(
                        row=row, column=column, ipadx=50, ipady=40, padx=10, pady=10)
                elif slotState == 1:
                    tk.Button(boardSection, text='O', state="disabled").grid(
                        row=row, column=column, ipadx=50, ipady=40, padx=10, pady=10)
                else:
                    # <difficulty> so i have to explicitly tell the lambda function that i want to use the variables in passed at the time of the button was created
                    tk.Button(boardSection, command=lambda row=row, col=column: self.take_turn(row, col)).grid(
                        row=row, column=column, ipadx=60, ipady=40, padx=10, pady=10)

    def take_turn(self, row, Column):
        rowColumn = (row, Column)
        try:
            if (self.controller.SocketConnection.userData[0] == self.controller.SocketConnection.gameData["player_data"][self.controller.SocketConnection.gameData["player_turn"]-1][0]):
                asyncio.run(
                    self.controller.SocketConnection.take_turn(rowColumn))
                self.msg_label.grid_remove()
        except:
            self.MSG.set("It is not your turn")
            self.msg_label.grid()
            pass


class LeaderBoardPage(tk.Frame):  # inherit from the tk frame

    #The leaderBoard page - shows the top 20 players, and lets the user search up any players rank
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # inits the inherited frame class
        # parent is the class that called this class

        self.controller = controller
        self.parent = parent

        # variables
        self.MSG = tk.StringVar()
        self.MSG.set("Your Rank Is:")
        self.userDatas = []

        # render view
        self.render()

    def render(self):
        if self.controller.SocketConnection != None:
            # username will be used to lookup a single user's ranking
            username = tk.StringVar()
            username.set(self.controller.SocketConnection.userData[0])

            asyncio.run(self.get_all_userData_sorted())
            Leaderboard = ttk.Treeview(self, columns=('username', 'wins', 'losses', 'games_played'))
            Leaderboard.column('#0', width=60, anchor='center')
            Leaderboard.heading('#0', text='Ranking')
            Leaderboard.column('username', width=120, anchor='center')
            Leaderboard.heading('username', text='Username')
            Leaderboard.column('wins', width=60, anchor='center')
            Leaderboard.heading('wins', text='Wins')
            Leaderboard.column('losses', width=60, anchor='center')
            Leaderboard.heading('losses', text='Losses')
            Leaderboard.column('games_played', width=120, anchor='center')
            Leaderboard.heading('games_played', text='Games Played')

            for index in range(0, (20 if (len(self.userDatas) > 19) else len(self.userDatas))):  # Display top 20 players!
                Leaderboard.insert("", tk.END, text=str(index+1), values=self.userDatas[index] )

            Leaderboard.grid(row=0,  padx=10, pady=20,
                              ipady=140, sticky="nw")

            # right hand side section
            right_action_section = tk.Frame(self)
            right_action_section.grid(
                row=0, rowspan=2, column=1, ipady=120, pady=20)

            tk.Button(right_action_section, text="Update Board", font=(
                "arial", 16), command=self.render).grid(row=0, columnspan=2, sticky="new", ipadx=10, ipady=10)

            # search player section
            search_player_section = tk.Frame(right_action_section)
            search_player_section.grid(
                row=1, rowspan=2, columnspan=2, padx=20, pady=70)

            tk.Label(
                search_player_section, text="Username:", font=("arial", 14)).grid(row=0, column=0, sticky="news")
            tk.Entry(
                search_player_section, textvariable=username).grid(row=0, column=1, pady=20, padx=10, ipady=10, ipadx=20, sticky="swe")

            tk.Button(search_player_section, text="Search \nPlayer Rank", font=(
                "arial", 16), command=lambda: self.findUserRank(username.get())).grid(row=1, column=0, sticky="new", padx=5, ipadx=20)
            tk.Button(search_player_section, text="Get My \nPosition", font=(
                "arial", 16), command=lambda: self.findUserRank(self.controller.SocketConnection.userData[0])).grid(row=1, column=1, sticky="new", padx=5, ipadx=20)

            tk.Button(search_player_section, text="Go Back to home", font=(
                "arial", 14), command=lambda: self.controller.switch_frame_to(HomePage)).grid(row=3, columnspan=2, column=0, pady=10, padx=20, ipadx=30, ipady=20)
            tk.Label(search_player_section, textvariable=self.MSG, wrap=255, font=(
                "arial", 14)).grid(row=4, columnspan=2, sticky="sw", pady=20)

    async def get_all_userData_sorted(self):

        #get all user datas from the database
        try:
            self.MSG.set("")
            fetch_all_user_stats = await self.controller.SocketConnection.getAllPlayerData()
            if fetch_all_user_stats != True:
                self.MSG.set(fetch_all_user_stats)
            self.userDatas = self.controller.SocketConnection.leaderboard
        except:
            raise

    def findUserRank(self, username: str):
        for i, userdata in enumerate(self.userDatas):
            if userdata[0] == username:
                return self.MSG.set(f"Rank of {username}: {i+1} ")
            else:
                pass
        return self.MSG.set(f"Could not find {username}")


class AuthenticationPage(tk.Frame):  # inherit from the tk frame
    """
    The main page - show when the user is successfully authenticated
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)  # inits the inherited frame class
        # parent is the class that called this class
        self.controller = controller
        self.parent = parent
        self.ERROR_MSG = tk.StringVar()
        self.render()

    def render(self):
        """
        Render the authentication page view
        """
        # variables
        username = tk.StringVar()
        password = tk.StringVar()
        hostname = tk.StringVar()
        port_number = tk.IntVar()

        # testing login info:
        # username.set("test1")
        # password.set("test12")
 
        # set up default server connection value
        # server is running on the current computer
        port_number.set(65432) # on this port number

        # authentication section
        authentication_section = tk.LabelFrame(
            self, text="Authentication", font=("arial", 20, "bold"))

        username_label = tk.Label(
            authentication_section, text="Username:", font=("arial", 14))
        username_entry = tk.Entry(
            authentication_section, textvariable=username)
        password_label = tk.Label(
            authentication_section, text="Password:", font=("arial", 14))
        password_entry = tk.Entry(
            authentication_section,  show="*", textvariable=password)

        """
            alignment:
            - sticky = n="top", e="right", s="bottom", w="left" alignment
            padding:
            - padx =  the extra space around the x line 
            - pady =  the extra space around the y line 
            - ipadx =  the extra space inside the widget on the x line 
            - ipady =  the extra space inside the widge on the y lines
            """
        username_label.grid(row=0, column=0, sticky="nsw", ipadx=40, ipady=10)
        username_entry.grid(row=0, column=1, sticky="nsw",
                            ipadx=40, ipady=10, padx=10, pady=10)
        password_label.grid(row=1, column=0, sticky="nsw", ipadx=40, ipady=10)
        password_entry.grid(row=1, column=1, sticky="nsw",
                            ipadx=40, ipady=10, padx=10, pady=10)
        authentication_section.grid(
            row=0, sticky="news",  padx=130, ipadx=20, pady=20, ipady=10)

        # server info section
        server_info_section = tk.LabelFrame(
            self, text="Server Info", font=("arial", 20, "bold"))

        hostname_label = tk.Label(
            server_info_section, text="Host name:",  font=("arial", 15))
        hostname_entry = tk.Entry(server_info_section, textvariable=hostname)
        port_number_label = tk.Label(
            server_info_section, text="Port number:",  font=("arial", 15))
        port_number_entry = tk.Entry(
            server_info_section, textvariable=port_number)

        hostname_label.grid(row=0, column=0, sticky="nsw", ipadx=40, ipady=10)
        hostname_entry.grid(row=0, column=1, sticky="nsw",
                            ipadx=40, ipady=10, padx=10, pady=10)
        port_number_label.grid(
            row=1, column=0, sticky="nsw", ipadx=40, ipady=10)
        port_number_entry.grid(row=1, column=1, sticky="nsw",
                               ipadx=40, ipady=10, padx=10, pady=10)
        server_info_section.grid(row=1, sticky="news",
                                 padx=130, ipadx=20, pady=20, ipady=10)

        # action section
        action_section = tk.Frame(self)
        # make the action section share single column
        action_section.grid_columnconfigure(0, weight=1)
        action_section.grid_columnconfigure(1, weight=1)
        action_section.grid_rowconfigure(0, weight=1)
        action_section.grid_rowconfigure(1, weight=1)

        # Make sure that the fields are not empty
        loginBtn = tk.Button(action_section, text='Login', font=("arial", 20, "bold"), command=lambda: self.controller.authenticate_user(
            self, (username.get(), password.get()), (hostname.get(), port_number.get())))
        registerBtn = tk.Button(action_section, text='Register', font=("arial", 20, "bold"), command=lambda: self.controller.register_user(
            self, (username.get(), password.get()), (hostname.get(), port_number.get())))

        loginBtn.grid(row=0, column=0, sticky="news",
                      ipadx=5, pady=5, ipady=10, padx=10)
        registerBtn.grid(row=0, column=1, sticky="news",
                         ipadx=5, pady=5, ipady=10,  padx=10)
        action_section.grid(row=2, sticky="news",  padx=130,
                            ipadx=20, pady=20, ipady=10)

        # Setup Error Message Label
        self.err_label = tk.Label(self, textvariable=self.ERROR_MSG)
        self.err_label.grid(row=3, sticky="news")
        self.err_label.grid_remove()


if __name__ == "__main__":  
    try:
        # start application
        app = Application()
        app.mainloop()
    except:

        pass
