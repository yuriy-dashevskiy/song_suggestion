from tkinter import * 
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import hashlib
import sqlite3
import spotify_api_keys as keys
import spotipy
import logging
from PIL import Image, ImageTk
import textwrap
logging.basicConfig(level=logging.ERROR);

from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import HTTPError

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
            print('404 for record');
    return playlist_names;

root = tk.Tk()
root.title("MS")
root.geometry("200x150")
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
     
def on_login_button_pressed(entry1, entry2):
    loginResult = check_login(entry1.get(), entry2.get());
    label = get_login_result_label();
    user_name = entry1.get();
    if(loginResult == False):
        label.place(x = 75, y = 100)
        label.config(text="Unsuccessful")
    else:
        remove_widgets_from_root()

        root.after(1000,handle_music_suggestion_menu, user_name);
        label = tk.Label(root, text="Success")
        label.place(x=75, y=5)
        label2 = tk.Label(root, text="Login Result:")
        label2.place(x=5, y=5)
        label.after(1500, label.destroy)
        label2.after(1500, label2.destroy)

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
    root.geometry("350x450")
    root.resizable(0,0)
    remove_widgets_from_root()
    m1 = Frame(root, width=300, height=450)
    m1.place(x=0,y=0)
    m1.pack(fill=BOTH)
    top = Frame(m1, width=350, height=100)
    menu_label = tk.Label(top, text=get_menu_details(user_name), justify="left")
    menu_label.pack()
    top.pack()
    #m1.add(left)
    left = Frame(m1, width=300, height=350)
    left.place(x=300,y=0)
    left.pack()
    #m1.add(m2)
    
    #right = Frame(m2, width=200, height=400, bg='#eeeeee')
    global option_1_button, option_2_button, option_3_button, option_4_button, option_5_button, option_6_button

    option_1_button =  tk.Button(left, text="Add Playlist", command=lambda :handle_music_suggestion_menu_option_1(user_name), width = 25)
    option_2_button =  tk.Button(left, text="Remove Playlist", command=lambda :handle_music_suggestion_menu_option_2(user_name), width = 25)
    option_3_button =  tk.Button(left, text="Display all Playlists", command=lambda :handle_music_suggestion_menu_option_3(user_name), width = 25)
    option_4_button =  tk.Button(left, text="Display all track of a playlist", command=lambda :handle_music_suggestion_menu_option_4(user_name), width = 25)
    option_5_button =  tk.Button(left, text="Get Track Suggestions", command=lambda :handle_music_suggestion_menu_option_5(user_name), width = 25)
    option_6_button =  tk.Button(left, text="Quit Music Suggestions", command=lambda :handle_music_suggestion_menu_option_6(), width = 25)
    #music_note_image = Image.open("music_note.png")
    #music_note_image_photo = ImageTk.PhotoImage(music_note_image)
    #music_note_label = tk.Label(m2, image=music_note_image_photo)
    #music_note_label.pack();

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
    musical_note_label = tk.Label(left, text=musical_note_ascii, font=("Courier", 8), justify="left")
    option_1_button.pack()
    option_2_button.pack()
    option_3_button.pack()
    option_4_button.pack()
    option_5_button.pack()
    option_6_button.pack()
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

    remove_widgets_from_root()

    add_playlist_question_label = tk.Label(root, text=f'Choose the following way you want to add the new playlist, {user_name}?', justify="left")
    add_playlist_question_label.pack()
    id_button = tk.Button(root, text="Spotify ID", command=lambda :handle_adding_playlist_by_id(user_name), width = 25)
    id_button.pack()
    url_button = tk.Button(root, text="Spotify URL", command=lambda :handle_adding_playlist_by_url(user_name), width = 25)
    url_button.pack()

def handle_adding_playlist_by_id(user_name):

    remove_widgets_from_root()
    temp_label = tk.Label(root, text = 'Adding by ID')
    temp_label.pack();
    id_entry_label = tk.Label(root, text = 'Enter your spotify ID')
    id_entry_label.pack()
    id_entry = tk.Entry(root, width = 20)
    id_entry.pack();
    id_submit_button = tk.Button(root, text="Submit", command=lambda :check_playlist_id_entry(user_name,id_entry.get()), width = 25)
    id_submit_button.pack()
    no_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def check_playlist_id_entry(user_name,playlist_id):
    remove_widgets_from_root();

    if is_valid_playlist_id(playlist_id):
        temp_label = tk.Label(root, text = 'Valid Spotify Playlist ID entered')
        temp_label.pack()
        temp_label = tk.Label(root, text = 'Would you like to add this playlist to your records?')
        id_button = tk.Button(root, text = "Yes", command=lambda: check_if_playlist_id_in_records(user_name,playlist_id),width = 25)
        id_button.pack();
        main_menu_button = tk.Button(root,text='No', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();
        pass
    else:
        temp_label = tk.Label(root, text = 'Not Valid ID')
        temp_label = tk.Label(root, text = 'Would you like to re-enter new ID or return to main menu?')

        id_button = tk.Button(root, text = "Try a different Spotify ID", command=lambda: handle_adding_playlist_by_id(user_name),width = 25)
        id_button.pack();
        main_menu_button = tk.Button(root,text='Return to main menu', command=lambda: handle_music_suggestion_menu(user_name), width = 25)
        main_menu_button.pack();

    pass   
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
def msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name):
    #inserts new playlist record into playlists table

    user_id = msGet_User_Id_Using_User_Name(user_name);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    c.execute('INSERT INTO playlists(user_id, playlist_id) VALUES (?,?)',(user_id, playlist_id));
    conn.commit();
    msClose_DB_Connection(c, conn);

def msHandle_User_Playlist_ID_Entry(user_name):
    #handles user input of spotify playlist id entry and decides if playlist needs to be added or is already added

    playlist_id = input("Please enter spotify playlist id: ");
    while(True):
        
        if is_valid_playlist_id(playlist_id):
            print(f'Spotify playlist id has been entered. Checking if playlist is added for user: {user_name}');
            playlist_record = msGet_Playlist_In_Playlists_Table(playlist_id, user_name);
            if(playlist_record is None):
                print('Adding playlist to your list of playlists. Returning to main menu.');
                msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name);
                break;
            else:
                print('Playlist is already in your list of playlists. Returning to main menu.');
                break;
        else:
            playlist_id = input("Please enter a valid spotify playlist id: ");

def handle_adding_playlist_by_url(user_name):
    
    remove_widgets_from_root()
    temp_label = tk.Label(root, text = 'Adding by URL')
    temp_label.pack();
    no_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

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

    removing_playlist_label = tk.Label(root, text=f'Removing playlist for {user_name}', justify="left")
    removing_playlist_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_3(user_name):
    #handles music suggestion menu option 3
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to display all playlists for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :handle_removing_playlist(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def display_all_playlists(user_name):
    #displays all playlists

    remove_widgets_from_root()

    display_playlists_label = tk.Label(root, text=f'Displaying all playlists for {user_name}', justify="left")
    display_playlists_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_4(user_name):
    
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to display all tracks of a specific playlist for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :display_all_tracks_of_playlist(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def display_all_tracks_of_playlist(user_name):
    # displays all tracks of a playlist 

    remove_widgets_from_root()

    display_playlists_label = tk.Label(root, text=f'Displaying all tracks of playlist for {user_name}', justify="left")
    display_playlists_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_5(user_name):
    
    remove_widgets_from_root()

    display_playlists_question_label = tk.Label(root, text=f'Would you like to get track suggestions for {user_name}?', justify="left")
    display_playlists_question_label.pack()

    yes_button = tk.Button(root, text="Yes", command=lambda :get_track_suggestions(user_name), width = 25)
    yes_button.pack()
    no_button = tk.Button(root, text="No", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    no_button.pack()

def get_track_suggestions(user_name):
    #gets track suggestions

    remove_widgets_from_root()

    display_playlists_label = tk.Label(root, text=f'Getting track suggestions for {user_name}', justify="left")
    display_playlists_label.pack()

    return_to_main_menu_button = tk.Button(root, text="Return to main menu", command=lambda :handle_music_suggestion_menu(user_name), width = 25)
    return_to_main_menu_button.pack()

def handle_music_suggestion_menu_option_6():
    #exits the program

    root.destroy()
 
def get_login_result_label():  
    text_var = tk.StringVar(value="")
    label = tk.Label(root, text=text_var)
    label.place(x = 50, y = 75)
    return label
    
user_id = ms_Get_Record_Of_User_In_Users_Table('Yuriy')[0];
playlists = msGet_Playlists_Using_User_ID(user_id);
playlist_dict = msGet_all_playlist_names(playlists);

def main():

    # Create labels and entry fields
    label1 = tk.Label(root, text="User Name:")
    label1.place(x=5, y=10)
    entry1 = tk.Entry(root, width = 20)
    entry1.place(x=70, y=10)

    label2 = tk.Label(root, text="Password:")
    label2.place(x=5, y=35)
    entry2 = tk.Entry(root, show = "*", width= 20)
    entry2.place(x=70, y=35)
    label3 = tk.Label(root, text="Login Result:")
    label3.place(x=5, y=100)
    button = tk.Button(root, text="Submit", command=lambda :on_login_button_pressed(entry1, entry2))
    button.place(x=75, y=60)
    root.mainloop()

main();