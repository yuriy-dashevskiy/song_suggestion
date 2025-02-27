from tkinter import *
from tkinter import ttk 
import tkinter as tk
from tkinter.constants import *
import hashlib
import sqlite3
import spotify_api_keys as keys
import spotipy
import logging
import re
from PIL import Image, ImageTk
import textwrap
import random
logging.basicConfig(level=logging.ERROR);

from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import HTTPError
musical_note_ascii = '''
⠀⠀⠀⠀⠀⢀⣼⣿⣆⠀⠀⠀
⠀⠀⠀⠀⠀⣾⡿⠛⢻⡆⠀⠀
⠀⠀⠀⠀⢰⣿⠀⠀⢸⡇⠀⠀
⠀⠀⠀⠀⠸⡇⠀⢀⣾⠇⠀⠀
⠀⠀⠀⠀⠀⣿⣤⣿⡟⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⠀⠀⠀⠀
⠀⠀⣠⣾⣿⡿⣏⠀⠀⠀⠀⠀
⠀⣴⣿⡿⠋⠀⢻⡉⠀⠀⠀⠀
⢰⣿⡟⠀⢀⣴⣿⣿⣿⣿⣦⠀
⢸⡿⠀⠀⣿⠟⠛⣿⠟⠛⣿⣧
⠘⣿⡀⠀⢿⡀⠀⢻⣤⠖⢻⡿
⠀⠘⢷⣄⠈⠙⠦⠸⡇⢀⡾⠃
⠀⠀⠀⠙⠛⠶⠤⠶⣿⠉⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢹⡇⠀⠀
⠀⠀⢀⣴⣾⣿⣆⠀⠈⣧⠀⠀
⠀⠀⠈⣿⣿⡿⠃⠀⣰⡏⠀⠀
⠀⠀⠀⠈⣙⠓⠒⠚⠉⠀⠀⠀
'''
class VerticalScrolledFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
 
        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=1,
                                width = 200, height = 300,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command = self.canvas.yview)
 
 
        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = ttk.Frame(self.canvas)
        self.interior.bind('<Configure>', self._configure_interior)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)
        self.canvas.bind('<Configure>', self._configure_canvas)

    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame.

            self.canvas.config(width = self.interior.winfo_reqwidth())
    def _configure_canvas(self, event):
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.clientID,

                                               client_secret=keys.clientSecret,

                                               redirect_uri=keys.reDirURL,

                                               scope='user-library-read'));
except HTTPError as e:
    error = '';
except spotipy.SpotifyException as e:
    exception = '';

def msGet_DB_Connection():
    #creates new connection using specified db location
    
    conn = sqlite3.connect('C:/SQLite/files/music_suggestion.db');
    return conn;

def msGet_DB_Cursor(conn):
    #returns db cursor
    
    c = conn.cursor();
    return c;

def msClose_DB_Connection(c, conn):
    #closes db connection

    c.close();
    conn.close();

def ms_Get_Record_Of_User_In_Users_Table(user_name):
    # returns empty array or one item array of the user in users table

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT * FROM users WHERE user_name = ?;',(user_name,));
    user_record = queryExecute.fetchone();
    msClose_DB_Connection(c, conn);
    return user_record;

def msGet_Playlists_Using_User_ID(user_id):
    #queries the playlist table to get list of playlists using user_id value

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    playlistsQueryExec = c.execute('SELECT playlist_id FROM playlists WHERE user_id = ?', (user_id,));
    playlists = playlistsQueryExec.fetchall();
    msClose_DB_Connection(c, conn);
    return playlists

def msGet_all_playlist_names(playlists):
    #prints every playlist name in playlists provided
    playlist_names = {};
    for playlist in playlists:
        try:
            playlist_id = str(playlist).replace('(', '').replace(')', '').replace(',', '').replace('\'', '');
            playlist_names[playlist_id] = sp.playlist(playlist[0])['name']
        except:
            pass
    return playlist_names;

root = tk.Tk()
root.title("Music Suggestion")
root.geometry("350x450")
root.resizable(0,0)

def check_login(userNameInput, userPassInput):
    #handles login of existing users

    userPassHash = hashlib.sha224(userPassInput.encode('utf-8')).hexdigest();
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT * FROM users WHERE user_name = ? AND password = ?', (userNameInput, userPassHash));
    result = queryExecute.fetchone()
    conn.commit();
    msClose_DB_Connection(c, conn);
    if(result is None):
        return False;
    else:
        return True;

def check_user_name_taken(user_name):
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT * FROM users WHERE user_name = ?', (user_name, ));
    result = queryExecute.fetchone()
    conn.commit();
    msClose_DB_Connection(c, conn);
    if(result is None):
        return False;
    else:
        return True;

def on_login_button_pressed(user_name, password):
    #check if login is valid and redirects to music suggestion main menu if valid
    
    if user_name == '' or password == '':
        handle_login_existing('Invalid Login')
    elif(not check_login(user_name, password)):
        handle_login_existing('Invalid Login')
    else:
        handle_music_suggestion_menu(user_name)

def insert_New_User_Into_Users(user_name,password):
    #inserts new user into users table

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT MAX(user_id) FROM users');
    maxID = int(queryExecute.fetchone()[0]);
    c.execute('INSERT INTO users(user_id, user_name, password) VALUES (?,?,?)',(maxID + 1, user_name, password));
    conn.commit();
    msClose_DB_Connection(c, conn);

def on_create_button_pressed(user_name, password, password_confirm):
    #checks if entered user name, password and password confirm are valid

    if user_name == '' or password == '' or password_confirm == '':
        handle_create_new_user("Please enter info in every text box")                      
    elif check_user_name_taken(user_name):
        handle_create_new_user("User Name Taken")
    else:
        if password == password_confirm:
            user_pass_hash = hashlib.sha224(password.encode('utf-8')).hexdigest();
            insert_New_User_Into_Users(user_name,user_pass_hash);
            handle_music_suggestion_menu(user_name)
        else:
            handle_create_new_user("Passwords do not match")

def get_menu_details(user_name):
    #returns menu details

    menu = f'''
Welcome to Music Suggestions, {user_name}!
Please click one of the options listed below to proceed.
''';
    menu = textwrap.fill(menu, width=50);
    return menu;

def handle_music_suggestion_menu(user_name):
    root.title("Music Suggestion")
    #root.geometry("350x450")
    root.resizable(0,0)

    remove_widgets_from_root()

    m1 = Frame(root, width=300, height=450)
    m1.place(x=0,y=0)
    m1.pack(fill=BOTH)

    top = Frame(m1, width=350, height=100)
    menu_label = tk.Label(top, text=get_menu_details(user_name), justify="left")
    menu_label.pack()
    top.pack()

    left = Frame(m1, width=300, height=350)
    left.place(x=300,y=0)
    left.pack()

    option_1_button = tk.Button(left, text="Add Playlist", command=lambda :handle_music_suggestion_menu_option_1(user_name), width = 25)
    option_1_button.pack()

    option_2_button = tk.Button(left, text="Remove Playlist", command=lambda :handle_music_suggestion_menu_option_2(user_name), width = 25)
    option_2_button.pack()

    option_3_button = tk.Button(left, text="Display all Playlists", command=lambda :handle_music_suggestion_menu_option_3(user_name), width = 25)
    option_3_button.pack()

    option_4_button = tk.Button(left, text="Display all track of a playlist", command=lambda :handle_music_suggestion_menu_option_4(user_name), width = 25)
    option_4_button.pack()

    option_5_button = tk.Button(left, text="Get Track Suggestions", command=lambda :handle_music_suggestion_menu_option_5(user_name), width = 25)
    option_5_button.pack()

    option_6_button = tk.Button(left, text="Change user", command=lambda :handle_music_suggestion_menu_option_6(), width = 25)
    option_6_button.pack()

    option_7_button = tk.Button(left, text="Quit Music Suggestions", command=lambda :handle_music_suggestion_menu_option_7(), width = 25)
    option_7_button.pack()

    musical_note_label = tk.Label(left, text=musical_note_ascii, font=("Courier", 8), justify="left")
    musical_note_label.pack();

def remove_widgets_from_root():

    for widget in root.winfo_children():
        widget.destroy()

def handle_music_suggestion_menu_option_1(user_name):
    #handles music suggestion menu option 1

    remove_widgets_from_root()

    add_playlist_question_label = tk.Label(root, text=f'Would you like to add a playlist, {user_name}?', justify="left")
    add_playlist_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :handle_adding_playlist(user_name), width = 25)
    yes_button.pack()

    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()
    
def handle_adding_playlist(user_name):
    #handles adding playlist

    remove_widgets_from_root();

    add_playlist_question_label = tk.Label(root, text=f'Choose the following way you want to add the new playlist, {user_name}?', justify="left")
    add_playlist_question_label.pack()

    id_button = tk.Button(root, text="Spotify ID", command=lambda :handle_adding_playlist_by_id(user_name), width = 25)
    id_button.pack()

    url_button = tk.Button(root, text="Spotify URL", command=lambda :handle_adding_playlist_by_url(user_name), width = 25)
    url_button.pack()

def handle_adding_playlist_by_id(user_name):
    #handles adding playlist

    remove_widgets_from_root();

    id_entry_label = tk.Label(root, text = 'Enter your spotify playlist ID')
    id_entry_label.pack();

    id_entry = tk.Entry(root, width = 20)
    id_entry.pack();

    id_submit_button = tk.Button(root, text="Submit", command=lambda :check_playlist_id_entry(user_name,id_entry.get()), width = 25)
    id_submit_button.pack()

    no_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def check_playlist_id_entry(user_name,playlist_id):

    remove_widgets_from_root();

    if is_valid_playlist_id(playlist_id):

        valid_id_label = tk.Label(root, text = 'Valid Spotify Playlist ID entered')
        valid_id_label.pack();

        add_playlist_label = tk.Label(root, text = 'Would you like to add this playlist to your records?')
        add_playlist_label.pack();

        id_button = tk.Button(root, text = "Yes", command=lambda: check_if_playlist_id_in_records(user_name,playlist_id),width = 25)
        id_button.pack();

        main_menu_button = tk.Button(root,text='No', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();

    else:

        not_valid_label = tk.Label(root, text = 'Not Valid ID')
        not_valid_label.pack();

        re_entry_id_question_label = tk.Label(root, text = 'Would you like to re-enter new ID or return to main menu?')
        re_entry_id_question_label.pack();

        id_button = tk.Button(root, text = "Try a different Spotify ID", command=lambda: handle_adding_playlist_by_id(user_name),width = 25)
        id_button.pack();

        main_menu_button = tk.Button(root,text='Return to main menu', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();

def check_if_playlist_id_in_records(user_name,playlist_id):

    remove_widgets_from_root()

    playlist_record = msGet_Playlist_In_Playlists_Table(playlist_id, user_name);

    if(playlist_record is None):

        added_new_playlist_record_label = tk.Label(root, text='Successfully added playlist to your records')
        added_new_playlist_record_label.pack()
        main_menu_button = tk.Button(root,text='Return to main menu', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();
        msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name);
    
    else:

        existing_playlist_record_label = tk.Label(root, text='Playlist is already in your records')
        existing_playlist_record_label.pack()
        main_menu_button = tk.Button(root,text='Return to main menu', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();

def is_valid_playlist_id(playlist_id):
    # returns boolean if playlist id is a valid spotify playlist id

    try:
        sp.playlist(playlist_id) ;
        return True;
    except spotipy.exceptions.SpotifyException as e:
        return False;
    except HTTPError:
        return False; 
  
def msGet_User_Id_Using_User_Name(user_name):
    #queries the users table to get user_id using user_name value

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    userIDGetQueryExecute = c.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,));
    user_id = userIDGetQueryExecute.fetchone()[0];
    conn.commit();
    msClose_DB_Connection(c, conn);
    return user_id;   

def msGet_Playlist_In_Playlists_Table(playlist_id, user_name):
    #queries the table to return specific record using playlist_id and user_id(which is queried also using user_name parameter)

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    user_id = msGet_User_Id_Using_User_Name(user_name);
    playlistIdQueryCheckExecute = c.execute('SELECT * FROM playlists WHERE user_id = ? AND playlist_id = ?', (user_id,playlist_id));
    playlist_record = playlistIdQueryCheckExecute.fetchone();
    conn.commit();
    msClose_DB_Connection(c, conn);
    return playlist_record;

def ms_Get_Record_Of_User_In_Users_Table(user_name):
    # returns empty array or one item array of the user in users table

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT * FROM users WHERE user_name = ?;',(user_name,));
    user_record = queryExecute.fetchone()[0];
    msClose_DB_Connection(c, conn);
    return user_record;

def msGet_Playlists_Using_User_ID(user_id):
    #queries the playlist table to get list of playlists using user_id value

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    playlistsQueryExec = c.execute('SELECT playlist_id FROM playlists WHERE user_id = ?', (user_id,));
    playlists = playlistsQueryExec.fetchall();
    msClose_DB_Connection(c, conn);
    return playlists

def msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name):
    #inserts new playlist record into playlists table

    user_id = msGet_User_Id_Using_User_Name(user_name);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    c.execute('INSERT INTO playlists(user_id, playlist_id) VALUES (?,?)',(user_id, playlist_id));
    conn.commit();
    msClose_DB_Connection(c, conn);

def handle_adding_playlist_by_url(user_name):
    
    #handles adding playlist

    remove_widgets_from_root();

    url_entry_label = tk.Label(root, text = 'Enter your spotify Playlist URL')
    url_entry_label.pack();

    url_entry = tk.Entry(root, width = 20)
    url_entry.pack();

    url_submit_button = tk.Button(root, text="Submit", command=lambda :check_playlist_url_entry(user_name,url_entry.get()), width = 25)
    url_submit_button.pack()

    return_to_main_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_button.pack()

def check_playlist_url_entry(user_name, url_entry):

    remove_widgets_from_root();

    playlist_id = '';
    if url_entry != '':
        
        if url_entry.find('open.spotify.com/playlist/') != -1:

            url_parts = url_entry.split('playlist/')[-1];
            match = re.search(r'[^a-zA-Z0-9]', url_parts);

            if match:

                playlist_id = url_parts[:match.start()];
            
            else:

                playlist_id = (url_parts);

            if is_valid_playlist_id(playlist_id):

                valid_id_label = tk.Label(root, text = 'Valid Spotify Playlist URL entered')
                valid_id_label.pack();

                add_playlist_label = tk.Label(root, text = 'Would you like to add this playlist to your records?')
                add_playlist_label.pack();

                url_button = tk.Button(root, text = "Yes", command=lambda: check_if_playlist_id_in_records(user_name,playlist_id),width = 25)
                url_button.pack();

                main_menu_button = tk.Button(root,text='No', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
                main_menu_button.pack();

            else:
                
                not_valid_label = tk.Label(root, text = 'Invalid spotify url has been entered')
                not_valid_label.pack();

                re_entry_id_question_label = tk.Label(root, text = 'Would you like to re-enter new url or return to main menu?')
                re_entry_id_question_label.pack();

                id_button = tk.Button(root, text = "Try a different Spotify playlist url", command=lambda: handle_adding_playlist_by_url(user_name),width = 25)
                id_button.pack();
        
        else:

            empty_url_label = tk.Label(root, text = 'Invalid spotify url has been entered')
            empty_url_label.pack()

            id_button = tk.Button(root, text = "Try a different Spotify playlist url", command=lambda: handle_adding_playlist_by_url(user_name),width = 25)
            id_button.pack();
    
    else:

        empty_url_label = tk.Label(root, text = 'No spotify url has been entered')
        empty_url_label.pack()
        id_button = tk.Button(root, text = "Try a different Spotify playlist url", command=lambda: handle_adding_playlist_by_url(user_name),width = 25)
        id_button.pack();
    
    main_menu_button = tk.Button(root,text='Return to main menu', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
    main_menu_button.pack();

def handle_music_suggestion_menu_option_2(user_name):
    #handles music suggestion menu option 2

    remove_widgets_from_root()

    add_playlist_question_label = tk.Label(root, text=f'Would you like to remove a playlist, {user_name}?', justify="left")
    add_playlist_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :handle_removing_playlist(user_name), width = 25)
    yes_button.pack()

    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def handle_removing_playlist(user_name):
    #handles removing playlist

    remove_widgets_from_root()

    user_id = ms_Get_Record_Of_User_In_Users_Table(user_name)
    playlists = msGet_Playlists_Using_User_ID(user_id)

    if playlists != []:

        playlist_remove_question_label = tk.Label(root, text='Which playlist would you like to remove');
        playlist_remove_question_label.pack()

        playlist_button_question_2_label = tk.Label(root, text='Enter the number next to the playlist name to continue')
        playlist_button_question_2_label.pack()

        playlist_names = msGet_all_playlist_names(playlists)

        if len(playlist_names) <= 19:
            i = 1
            for playlist in playlist_names:
                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_numbered = str(i) + ') ' + playlist_name
                playlist_label = tk.Label(root, text = playlist_name_numbered)
                playlist_label.pack()
                i+=1
        elif len(playlist_names) > 19 and len(playlist_names)<=21:
            i = 1
            text_area = Frame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
        else:
            i = 1
            text_area = VerticalScrolledFrame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area.interior, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;

        playlist_entry_frame = tk.Frame(root)
        playlist_entry_frame.pack()

        playlist_entry_label = tk.Label(playlist_entry_frame, text='Playlist Choice')
        playlist_entry_label.pack(side='left')

        playlist_entry = tk.Entry(playlist_entry_frame)
        playlist_entry.pack(side = 'left')

        playlist_entry_submit = tk.Button(root, text = 'Submit',command=lambda:check_if_playlist_remove_entry_option_valid(user_name,playlist_entry.get(), playlists))
        playlist_entry_submit.pack()

    else:

        no_playlist_found_label = tk.Label(root, text = 'You have no playslists saved.')
        no_playlist_found_label.pack()

        no_playlist_found_pt2_label = tk.Label(root, text = 'Please add a new playlist to your records to use this feature!')
        no_playlist_found_pt2_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def check_if_playlist_remove_entry_option_valid(user_name, entry_choice, playlists):

    remove_widgets_from_root()

    try:
        entry_choice = int(entry_choice)
        new_entry_choice = entry_choice - 1
        if new_entry_choice < len(playlists) and new_entry_choice >= 0:

            playlist_id = playlists[new_entry_choice][0]
            playlist_name = sp.playlist(playlist_id)['name']
            
            playlist_remove_question_label = tk.Label(root, text='Valid choice entered')
            playlist_remove_question_label.pack()

            playlist_name_question_label = tk.Label(root, text = 'Are you sure you want to delete the chosen playlist below?')
            playlist_name_question_label.pack()

            playlist_name_label = tk.Label(root, text=playlist_name)
            playlist_name_label.pack()

            yes_for_remove_button = tk.Button(root, text='Yes',command=lambda :remove_specific_playlist(user_name,playlist_id), width = 25)
            yes_for_remove_button.pack();
            
        else:

            label = tk.Label(root,text ='Invalid entry entered. Continue with one of the options listed below.')
            label.pack();

            return_to_playlist_remove_choice_button = tk.Button(root,text = 'Return to playlist remove choice', command=lambda: handle_removing_playlist(user_name))
            return_to_playlist_remove_choice_button.pack()
    
    except (ValueError, AttributeError):

        invalid_entry_label = tk.Label(root,text='Please enter a valid number for choosing playlist')
        invalid_entry_label.pack();

        return_to_playlist_choice_button = tk.Button(root, text='Return to Playlist Choice', command=lambda: handle_removing_playlist(user_name), width = 25)
        return_to_playlist_choice_button.pack();

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()
    
def msDelete_Playlist_Record_Into_Playlists(playlist_id, user_name):
    #deletes specified playlist record from playlists table

    user_id = msGet_User_Id_Using_User_Name(user_name);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    c.execute('DELETE FROM playlists WHERE user_id = ? AND playlist_id = ?',(user_id, playlist_id));
    conn.commit();
    msClose_DB_Connection(c, conn);

def remove_specific_playlist(user_name, playlist_id):

    remove_widgets_from_root()

    remove_successful_label = tk.Label(root, text = 'Successfully removed playlist from your records')
    remove_successful_label.pack()

    msDelete_Playlist_Record_Into_Playlists(playlist_id, user_name)

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_3(user_name):
    #handles music suggestion menu option 3
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to display all playlists for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :display_all_playlists(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def display_all_playlists(user_name):
    #displays all playlists

    remove_widgets_from_root()

    user_id = ms_Get_Record_Of_User_In_Users_Table(user_name)
    playlists = msGet_Playlists_Using_User_ID(user_id)
    if playlists != []:
        display_playlists_label = tk.Label(root, text=f'Displaying all playlists for {user_name}', justify="left")
        display_playlists_label.pack()   
        playlist_names = msGet_all_playlist_names(playlists)
        if len(playlist_names) <= 19:
            i = 1
            for playlist in playlist_names:
                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_numbered = str(i) + ') ' + playlist_name
                playlist_label = tk.Label(root, text = playlist_name_numbered)
                playlist_label.pack()
                i+=1
        elif len(playlist_names) > 19 and len(playlist_names)<=21:
            i = 1
            text_area = Frame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
        else:
            i = 1
            text_area = VerticalScrolledFrame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area.interior, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
            
    else:
        empty_playlists_label = tk.Label(root, text = 'You need at least one playlist saved to display playlist names')
        empty_playlists_label.pack()
    
    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_4(user_name):
    
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to display all tracks of a specific playlist for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :query_which_playlist_to_display_tracks(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def query_which_playlist_to_display_tracks(user_name):
    # displays all tracks of a playlist 

    remove_widgets_from_root()

    user_id = ms_Get_Record_Of_User_In_Users_Table(user_name)
    playlists = msGet_Playlists_Using_User_ID(user_id)
    
    if playlists != []:

        display_playlists_question_label = tk.Label(root, text=f'Which playlist would you want to view all tracks? {user_name}', justify="left")
        display_playlists_question_label.pack()

        playlist_names = msGet_all_playlist_names(playlists)

        if len(playlist_names) <= 19:
            i = 1
            for playlist in playlist_names:
                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_numbered = str(i) + ') ' + playlist_name
                playlist_label = tk.Label(root, text = playlist_name_numbered)
                playlist_label.pack()
                i+=1
        elif len(playlist_names) > 19 and len(playlist_names)<=21:
            i = 1
            text_area = Frame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
        else:
            i = 1
            text_area = VerticalScrolledFrame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area.interior, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;

        playlist_entry_frame = tk.Frame(root)
        playlist_entry_frame.pack()

        playlist_entry_label = tk.Label(playlist_entry_frame, text='Playlist Choice')
        playlist_entry_label.pack(side='left')

        playlist_entry = tk.Entry(playlist_entry_frame)
        playlist_entry.pack(side = 'left')

        playlist_entry_submit = tk.Button(root, text = 'Submit',command=lambda:check_if_playlist_track_display_option_valid(user_name,playlist_entry.get(), playlists))
        playlist_entry_submit.pack()

    else:

        empty_playlists_label = tk.Label(root, text = 'You need at least one playlist saved to display tracks')
        empty_playlists_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def check_if_playlist_track_display_option_valid(user_name, entry_choice,playlists):

    remove_widgets_from_root()

    try:
        entry_choice = int(entry_choice)
        new_entry_choice = entry_choice - 1
        if new_entry_choice < len(playlists) and new_entry_choice >= 0:

            playlist_id = playlists[new_entry_choice][0]
            playlist_name = sp.playlist(playlist_id)['name']
            
            playlist_choice_valid_label = tk.Label(root, text='Valid choice entered')
            playlist_choice_valid_label.pack()

            playlist_display_question_label = tk.Label(root, text = 'Are you sure you want to display playlist below?')
            playlist_display_question_label.pack()

            playlist_name_label = tk.Label(root, text=playlist_name)
            playlist_name_label.pack()

            yes_for_display_button = tk.Button(root, text='Yes',command=lambda :display_all_tracks_using_specified_playlist(user_name,playlist_id), width = 25)
            yes_for_display_button.pack();
            
        else:

            label = tk.Label(root,text ='Invalid entry entered. Continue with one of the options listed below.')
            label.pack();

            return_to_playlist_track_display_choice_button = tk.Button(root,text = 'Return to playlist track display choice', command=lambda: query_which_playlist_to_display_tracks(user_name))
            return_to_playlist_track_display_choice_button.pack()
    
    except (ValueError, AttributeError):

        invalid_entry_label = tk.Label(root,text='Please enter a valid number for choosing playlist')
        invalid_entry_label.pack();

        return_to_playlist_choice_button = tk.Button(root, text='Return to Playlist Choice', command=lambda: query_which_playlist_to_display_tracks(user_name), width = 25)
        return_to_playlist_choice_button.pack();

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def display_all_tracks_using_specified_playlist(user_name,playlist_id):

    remove_widgets_from_root();

    playlist= sp.playlist(playlist_id);

    playlist_name = playlist['name'];

    playlist_name_label = tk.Label(root,text = playlist_name)
    playlist_name_label.pack();

    playlistTracks = playlist['tracks']['items'];
    
    if len(playlistTracks) > 19:

        text_area = VerticalScrolledFrame(root)
        text_area.pack(expand=True,fill="both")
        num_tracks = 1;

        for track in playlistTracks:

            try:
                track_name = str(num_tracks) + ') ' + track['track']['name'];
                track_name_wrap = textwrap.fill(track_name, width=50)
                track_name_label = ttk.Label(text_area.interior, text=track_name_wrap)
                track_name_label.pack()
                num_tracks += 1;
            
            except:
                pass

    elif len(playlistTracks) <= 19 and len(playlistTracks) > 17:
        text_area = Frame(root)
        text_area.pack(expand=True,fill="both")
        num_tracks = 1;

        for track in playlistTracks:

            try:
                track_name = str(num_tracks) + ') ' + track['track']['name'];
                track_name_wrap = textwrap.fill(track_name, width=50)
                track_name_label = ttk.Label(text_area, text=track_name_wrap)
                track_name_label.pack()
                num_tracks += 1;
            
            except:
                pass
    else:

        num_tracks = 1;
        for track in playlistTracks:
            try:
                track_name = str(num_tracks) + ') ' + track['track']['name'];
                track_name_label = tk.Label(root, text = track_name);
                track_name_label.pack()
                num_tracks += 1;
            except:
                pass

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()


def handle_music_suggestion_menu_option_5(user_name):
    
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to get track suggestions for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :handle_playlist_choice_for_track_suggestion(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def handle_playlist_choice_for_track_suggestion(user_name):
    #gets track suggestions

    remove_widgets_from_root()

    user_id = ms_Get_Record_Of_User_In_Users_Table(user_name)
    playlists = msGet_Playlists_Using_User_ID(user_id)
    if playlists != []:
        display_playlists_question_label = tk.Label(root, text='Which playlist would you like to get track suggestions?', justify="left")
        display_playlists_question_label.pack()
        playlist_names = msGet_all_playlist_names(playlists)
        if len(playlist_names) <= 17:
            i = 1
            for playlist in playlist_names:
                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_numbered = str(i) + ') ' + playlist_name
                playlist_label = tk.Label(root, text = playlist_name_numbered)
                playlist_label.pack()
                i+=1
        elif len(playlist_names) > 17 and len(playlist_names)<=19:
            i = 1
            text_area = Frame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
        else:
            i = 1
            text_area = VerticalScrolledFrame(root)
            text_area.pack(expand=True,fill="both")
            for playlist in playlist_names:

                playlist_name = sp.playlist(playlist)['name'];
                playlist_name_v2 = str(i) + ') ' + playlist_name

                playlist_name_label = ttk.Label(text_area.interior, text=playlist_name_v2)
                playlist_name_label.pack()
                i += 1;
        
        playlist_entry_frame = tk.Frame(root)
        playlist_entry_frame.pack()

        playlist_entry_label = tk.Label(playlist_entry_frame, text='Playlist Choice')
        playlist_entry_label.pack(side='left')

        playlist_entry = tk.Entry(playlist_entry_frame)
        playlist_entry.pack(side = 'left')

        playlist_entry_submit = tk.Button(root, text = 'Submit',command=lambda:check_if_playlist_track_suggestion_option_valid(user_name,playlist_entry.get(), playlists))
        playlist_entry_submit.pack()
            
    else:
        empty_playlists_label = tk.Label(root, text = 'You need at least one playlist saved to display playlist names')
        empty_playlists_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def check_if_playlist_track_suggestion_option_valid(user_name, entry_choice, playlists):
    remove_widgets_from_root()

    try:
        entry_choice = int(entry_choice)
        new_entry_choice = entry_choice - 1

        if new_entry_choice < len(playlists) and new_entry_choice >= 0:

            playlist_id = playlists[new_entry_choice][0]
            playlist_name = sp.playlist(playlist_id)['name']
            
            playlist_choice_valid_label = tk.Label(root, text='Valid choice entered')
            playlist_choice_valid_label.pack()

            playlist_display_question_label = tk.Label(root, text = 'Do you want to get track suggestions for the playlist below?')
            playlist_display_question_label.pack()

            playlist_name_label = tk.Label(root, text=playlist_name)
            playlist_name_label.pack()

            yes_for_display_button = tk.Button(root, text='Yes',command=lambda :handle_random_or_specific_artist_choice(user_name,playlist_id), width = 25)
            yes_for_display_button.pack();
            
        else:

            label = tk.Label(root,text ='Invalid entry entered. Continue with one of the options listed below.')
            label.pack();

            return_to_playlist_track_display_choice_button = tk.Button(root,text = 'Return to playlist track suggestion choice', command=lambda: handle_playlist_choice_for_track_suggestion(user_name))
            return_to_playlist_track_display_choice_button.pack()
    
    except (ValueError, AttributeError):

        invalid_entry_label = tk.Label(root,text='Please enter a valid number for choosing playlist')
        invalid_entry_label.pack();

        return_to_playlist_choice_button = tk.Button(root, text='Return to Playlist Choice', command=lambda: handle_playlist_choice_for_track_suggestion(user_name), width = 25)
        return_to_playlist_choice_button.pack();

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()
def handle_random_or_specific_artist_choice(user_name,playlist_id):
    
    remove_widgets_from_root();

    track_suggestion_type_question_label = tk.Label(root, text = 'Choose one of the options below to choose between specific or random')
    track_suggestion_type_question_label.pack()

    random_artist_suggestion_button = tk.Button(root, text = 'Random Artist', command=lambda:handle_top_or_all_tracks_query(user_name,playlist_id,'random'))
    random_artist_suggestion_button.pack();

    specific_artist_suggestion_button = tk.Button(root, text = 'Specific Artist', command=lambda:handle_top_or_all_tracks_query(user_name,playlist_id,'specific'))
    specific_artist_suggestion_button.pack();

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_top_or_all_tracks_query(user_name, playlist_id, artist_type):

    remove_widgets_from_root();

    track_suggestion_type_question_label = tk.Label(root, text = 'Choose between all or top tracks of the artist')
    track_suggestion_type_question_label.pack()

    all_track_suggestion_button = tk.Button(root, text = 'All Tracks', command=lambda:handle_track_suggestions(user_name,playlist_id, artist_type,'all'))
    all_track_suggestion_button.pack();

    top_track_suggestion_button = tk.Button(root, text = 'Top Tracks', command=lambda:handle_track_suggestions(user_name,playlist_id, artist_type,'top'))
    top_track_suggestion_button.pack();

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_track_suggestions(user_name, playlist_id, artist_type, track_type):

    remove_widgets_from_root()

    playlist_artist_dict = get_playlist_artist_dict(playlist_id);

    artist_list = [];
    artist_id = '';
    num_artists = 1;

    for artist in playlist_artist_dict:
        artist_list.append([artist]);
        num_artists += 1;
        
    if artist_type == 'random':
        
        artist_choice = random.randint(1,num_artists);
        artist_id = artist_list[artist_choice-1][0];
        songs_list = get_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id)

        random_artist_name_label = tk.Label(root, text = f'Artist {playlist_artist_dict[artist_id]} has been picked at random')
        random_artist_name_label.pack()

        if track_type == 'all':
            
            total_track_text_label = tk.Label(root,text ='Suggested songs to add/listen to from all their tracks');
            total_track_text_label.pack()

            tracks = get_All_Artist_Songs(artist_id)
            print_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list)

        else:

            top_track_text_label = tk.Label(root,text ='Suggested songs to add/listen to from their top tracks');
            top_track_text_label.pack()

            tracks = sp.artist_top_tracks(artist_id)['tracks'];
            handle_artist_top_track_suggestion(tracks, songs_list)

        return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
        return_to_main_menu_button.pack()   

    else:

        playlist_name = sp.playlist(playlist_id)['name']

        artist_names_list_label = tk.Label(root, text = f'Artists in playlist {playlist_name}', justify = 'left')
        artist_names_list_label.pack();

        pad = playlist_artist_dict 
        
        if len(artist_list) > 19:
            
            text_area = VerticalScrolledFrame(root)
            text_area.pack(expand=True,fill="both")   
            i = 1;
            for artist in pad:
                print(type(artist))
                if(isinstance(artist, str)):
                    artist_name = sp.artist(artist)['name']
                    
                    artist_name_numbered = str(i) + ') ' + artist_name

                    artist_name_label = ttk.Label(text_area.interior , text = artist_name_numbered)
                    artist_name_label.pack()
                    i+=1;

        elif len(artist_list) > 17 and len(artist_list) <= 19:
            i = 1;
            text_area = Frame(root, borderwidth = 1)
            text_area.pack(expand=True,fill="both")

            for artist in pad:
                if(isinstance(artist, str)):
                    artist_name = sp.artist(artist)['name']
                    artist_name_numbered = str(i) + ') ' + artist_name

                    artist_name_label = ttk.Label(text_area , text = artist_name_numbered)
                    artist_name_label.pack()
                    i+=1;
                
        else:
            i = 1;
            for artist in pad:
                if(isinstance(artist, str)):
                    artist_name = sp.artist(artist)['name']
                    artist_name_numbered = str(i) + ') ' + artist_name

                    artist_name_label = tk.Label(root, text = artist_name_numbered)
                    artist_name_label.pack()
                    i+=1;

        artist_entry_frame = tk.Frame(root)
        artist_entry_frame.pack()

        artist_entry_label = tk.Label(artist_entry_frame, text='Playlist Choice')
        artist_entry_label.pack(side='left')

        artist_entry = tk.Entry(artist_entry_frame)
        artist_entry.pack(side = 'left')

        playlist_entry_submit = tk.Button(root, text = 'Submit',command=lambda:handle_music_suggestion_specific_artist(user_name,artist_entry.get(),playlist_id, track_type,artist_list, artist_type))
        playlist_entry_submit.pack()

        return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
        return_to_main_menu_button.pack() 

def handle_music_suggestion_specific_artist(user_name, artist_choice, playlist_id, track_type, artist_list, artist_type):

    remove_widgets_from_root()

    try:

        entry_choice = int(artist_choice)

        new_entry_choice = entry_choice - 1

        if new_entry_choice < len(artist_list) and new_entry_choice >= 0:

            artist_id = artist_list[new_entry_choice][0];

            songs_list = get_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id)
            
            if track_type == 'all':

                total_track_text_label = tk.Label(root,text ='Suggested songs to add/listen to from all their tracks');
                total_track_text_label.pack()

                tracks = get_All_Artist_Songs(artist_id)
                print_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list)   
                
            else:

                top_track_text_label = tk.Label(root,text ='Suggested songs to add/listen to from their top tracks');
                top_track_text_label.pack()

                tracks = sp.artist_top_tracks(artist_id)['tracks'];
                handle_artist_top_track_suggestion(tracks, songs_list)

        else:

            invalid_entry_label = tk.Label(root,text='Please enter a valid number for choosing artist')
            invalid_entry_label.pack();
    
            return_to_artist_choice_button = tk.Button(root, text='Return to Artist Choice', command=lambda:  handle_track_suggestions(user_name, playlist_id, artist_type, track_type), width = 25)
            return_to_artist_choice_button.pack();

    except (ValueError, AttributeError):
        invalid_entry_label = tk.Label(root,text='Please enter a valid number for choosing artist')
        invalid_entry_label.pack();

        return_to_artist_choice_button = tk.Button(root, text='Return to Artist Choice', command=lambda:  handle_track_suggestions(user_name, playlist_id, artist_type, track_type), width = 25)
        return_to_artist_choice_button.pack();
       
    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()    

def handle_artist_top_track_suggestion(tracks, songs_list):
    #prints tracks not in songs list

    for track in tracks:
            if track['name'] not in songs_list:
                track_name = tk.Label(root, text = track['name'])
                track_name.pack()

def handle_music_suggestion_menu_option_6():
    #exits the program
    handle_initial_menu()

def handle_music_suggestion_menu_option_7():
    
    root.destroy()

def get_login_result_label():

    text_var = tk.StringVar(value="")
    label = tk.Label(root, text=text_var)
    label.place(x = 50, y = 75)
    return label

def get_playlist_artist_dict(playlist_id):
    
    artist_id_list = {};
    playlist =  sp.playlist(playlist_id);
    playlistTracks = playlist['tracks']['items'];

    for track in playlistTracks:
        try:
            temp = track['track']['artists'][0]['id'];
            tempName = track['track']['artists'][0]['name'];
            artist_id_list[temp] = tempName;
        except:
            pass
    new_artist_id_list = dict(sorted(artist_id_list.items(), key = lambda item: item[1]));        
    return new_artist_id_list
            
def get_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id):
    #returns list of specific artist songs in specific playlist

    songs_list = [];
    playlist= sp.playlist(playlist_id);
    playlistTracks = playlist['tracks']['items'];

    for track in playlistTracks:
        try:
            specific_track = track['track']['artists'][0];
            if specific_track['id'] == artist_id:
                songs_list.append(track['track']['name']);
        except:
            pass
        
    return songs_list;

def get_All_Artist_Songs(artist_id):
    #returns a list of all songs of a specific artist using their artist_id

    songs = []

    # Get artist's albums
    albums = sp.artist_albums(artist_id, album_type='album,single,appears_on')
    for album in albums['items']:
        # Get tracks for each album
        tracks = sp.album_tracks(album['id'])
        for track in tracks['items']:
            songs.append(track['name']);

    return songs;

def print_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list):

#prints ten random tracks of a specific artists tracks not in songs list

    songs_not_in_list = [];
    for track in tracks:
        if track not in songs_list:
            songs_not_in_list.append(track);
    size = len(songs_not_in_list);
    if size < 11:
        i = 1;
        for track in songs_not_in_list:
            track_numbered = str(i) + ') ' + track
            track_name_label = tk.Label(root, text=track_numbered)
            track_name_label.pack()
    else:
        num_tracks = 1;
        index_list = [];
        while num_tracks < 11:
            random_index =  random.randint(0, len(songs_not_in_list)-1);
            if random_index not in index_list:
                track_numbered = str(num_tracks) + ') ' + songs_not_in_list[random_index] 
                track_name_label = tk.Label(root, text=track_numbered)
                track_name_label.pack()
                index_list.append(random_index);
                num_tracks += 1;

def handle_initial_menu():

    remove_widgets_from_root()

    music_suggestion_label = tk.Label(root, text = 'Music Suggestion')
    music_suggestion_label.config(font=("Courier", 25))
    music_suggestion_label.place(x = 17, y = 25)

    musical_note_label = tk.Label(root, text=musical_note_ascii, font=("Courier", 8), justify="left")
    musical_note_label.place(x = 125, y = 65)

    new_user_button = tk.Button(root, text = 'Create New User', command=lambda: handle_create_new_user(), width = 15)
    new_user_button.place(x = 60, y = 350)

    existing_user_button = tk.Button(root, text = 'Existing User', command=lambda: handle_login_existing(), width = 15)
    existing_user_button.place(x = 180, y = 350)

    developer_name_label = tk.Label(root,text = 'Developed by Yuriy Dashevskiy')
    developer_name_label.place(x = 100, y = 425)

def handle_login_existing(login_status = ''):

    remove_widgets_from_root()

    music_note_label = tk.Label(root, text = musical_note_ascii)
    music_note_label.place(x = 20, y = 65)
    new_user_label = tk.Label(root, text = 'Existing User')
    new_user_label.config(font=("Courier", 33))
    new_user_label.place(x = 5, y = 20)

    label1 = tk.Label(root, text="User Name:")
    label1.place(x=140, y=170)
    user_name_entry = tk.Entry(root, width = 17)
    user_name_entry.place(x=225, y=170)

    password_label = tk.Label(root, text="Password:")
    password_label.place(x=140, y=190)
    password_entry = tk.Entry(root, show = "*", width= 17)
    password_entry.place(x=225, y=190)

    if login_status != '':
        label3 = tk.Label(root, text=login_status)
        label3.place(x=140, y=140)
    
    login_button = tk.Button(root, text="Submit", command=lambda :on_login_button_pressed(user_name_entry.get(), password_entry.get()))
    login_button.place(x=225,y=220)

    new_user_button = tk.Button(root, text = 'Create New User', command=lambda: handle_create_new_user())
    new_user_button.place(x=230, y=410)

    main_menu_button = tk.Button(root, text = 'Main Menu', command=lambda:handle_initial_menu())
    main_menu_button.place(x=20, y=410)

def handle_create_new_user(create_status = ''):

    remove_widgets_from_root()
    
    music_note_label = tk.Label(root, text = musical_note_ascii)
    music_note_label.place(x = 20, y = 65)
    new_user_label = tk.Label(root, text = 'New User')
    new_user_label.config(font=("Courier", 33))
    new_user_label.place(x = 70, y = 20)

    label1 = tk.Label(root, text="User Name:")
    label1.place(x=140, y=170)
    user_name_entry = tk.Entry(root, width = 17)
    user_name_entry.place(x=225, y=170)

    password_label = tk.Label(root, text="Password:")
    password_label.place(x=140, y=190)
    password_entry = tk.Entry(root, show = "*", width= 17)
    password_entry.place(x=225, y=190)

    password_confirm_label = tk.Label(root, text="Confirm Pass:")
    password_confirm_label.place(x=140, y=210)
    password_confirm_entry = tk.Entry(root, show = "*", width= 17)
    password_confirm_entry.place(x=225, y=210)

    if create_status != '':
        label3 = tk.Label(root, text=create_status)
        label3.place(x=140, y=140)
    
    submit_button = tk.Button(root, text="Submit", command=lambda :on_create_button_pressed(user_name_entry.get(), password_entry.get(), password_confirm_entry.get()))
    submit_button.place(x=225,y=240)

    existing_user_button = tk.Button(root, text = 'Login Existing', command=lambda: handle_login_existing())
    existing_user_button.place(x=250, y=410)

    main_menu_button = tk.Button(root, text = 'Main Menu', command=lambda:handle_initial_menu())
    main_menu_button.place(x=20, y=410)

def main():

    # Create labels and entry fields

    handle_initial_menu()
    root.mainloop()

main();