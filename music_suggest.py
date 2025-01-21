import hashlib
import os
import re
import spotify_api_keys as keys
import spotipy
import sqlite3
from spotipy.oauth2 import SpotifyOAuth

def clear_screen():
    #clears the screen

    # For Windows
    if os.name == 'nt':
        _ = os.system('cls') 

    # For macOS and Linux
    else:
        _ = os.system('clear')

def msGet_DB_Connection():
    
    conn = sqlite3.connect('C:/SQLite/files/music_suggestion.db');
    return conn;

def msGet_DB_Cursor(conn):
    
    c = conn.cursor();
    return c;

def msClose_DB_Connection(c, conn):

    c.close();
    conn.close();

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=keys.clientID,

                                               client_secret=keys.clientSecret,

                                               redirect_uri=keys.reDirURL,

                                               scope='user-library-read'));
def msHandle_Initial_Menu():

    print("Welcome to music suggestion. Please choose either new user to create or login existing user");
    print("Type 1 for New User or Type 2 for Existing User");
    myChoice = 0;
    while(True):
        try:
            myChoice = int(input('Enter your digit: '))
            if myChoice == 1 or myChoice == 2:
                break;
            else:
                print('Please re-enter a number that is 1 or 2!');
        except ValueError:
            print('Please re-enter a valid number!');
    return myChoice;
    
def msUser_Login():

    choice = msHandle_Initial_Menu();
    userName = '';
    if choice == 1:
        userName = msCreate_New_User();
    else:
        userName = msLogin_Existing_User();
    return userName;
    
def msCreate_New_User():
    # handles creation of new user to add to the users table
    
    print("New User");
    user_name = input('Enter new user name: ');
    while(True):
        user_record = ms_Get_Record_Of_User_In_Users_Table(user_name);
        if(user_record is None):
            #print('Success');
            break;
        else:
            user_name = input('Please enter a user name that is not taken: ');
    while(True):
        user_pass_input = input('Please enter your password: ');
        user_pass_hash = hashlib.sha224(user_pass_input.encode('utf-8')).hexdigest();
        ms_Insert_New_User_Into_Users(user_name,user_pass_hash);
        
        break;
    return user_name;

def ms_Get_Record_Of_User_In_Users_Table(user_name):
    # returns empty array or one item array of the user in users table

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT * FROM users WHERE user_name = ?;', (user_name,));
    user_record = queryExecute.fetchone();
    msClose_DB_Connection(c, conn);
    return user_record;

def ms_Insert_New_User_Into_Users(user_name,password):
    #inserts new user into users table

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    queryExecute = c.execute('SELECT MAX(user_id) FROM users');
    maxID = int(queryExecute.fetchone()[0]);
    c.execute('INSERT INTO users(user_id, user_name, password) VALUES (?,?,?)',(maxID + 1, user_name, password));
    conn.commit();
    msClose_DB_Connection(c, conn);

def msLogin_Existing_User():
    
    print("Existing User");
    print("Please Enter your user name and password");
    userNameInput = input('User Name: ');
    userPassInput = input('Password: ');
    userPassHash = hashlib.sha224(userPassInput.encode('utf-8')).hexdigest();
    while(True):
        conn = msGet_DB_Connection();
        c = msGet_DB_Cursor(conn);
        queryExecute = c.execute('SELECT * FROM users WHERE user_name = ? AND password = ?', (userNameInput, userPassHash));
        result = queryExecute.fetchone();
        conn.commit();
        msClose_DB_Connection(c, conn);
        if(result is None):
            print('Please type in a valid user name and password');
            userNameInput = input('User Name: ');
            userPassInput = input('Password: ');
            userPassHash = hashlib.sha224(userPassInput.encode('utf-8')).hexdigest();
        else:
            print('Successfully logged in');
            break;
    return userNameInput;

def msPost_login_menu_headline():

    menu = """
Welcome to music suggestions
What option would you like to pick?
Option 1: Add playlist to your playlists
Option 2: Display all tracks in a specific playlist
Option 3: Display all of your playists
Option 4: Exit""";
    print(menu);

def is_valid_playlist_id(playlist_id):
    # returns boolean if playlist id is a valid spotify playlist id

    try:
        sp.playlist(playlist_id);
        return True;
    except spotipy.exceptions.SpotifyException:
        return False;     
             
def msPost_login_menu_choice_1(user_name):
    # allows user to add a playlist to their list of playlists using spotify id or spotify url

    menu = """
Please choose an option for adding a playlist
Option 1: Enter unique spotify id (found after /playlists/ in url and before # or ?si= if present
Option 2: Enter the spotify playlist url.""";
    print(menu);
    choice = int(input('Enter 1 or 2 for your choice: '));
    while(True):
        if choice == 1:
            msHandle_User_Playlist_ID_Entry(user_name);
            break;
        elif choice == 2:
            msHandle_User_Playlist_URL_Entry(user_name)
            break;
        else:
            choice = int(input('Please try again. Enter 1 or 2 for your choice.'));

def msHandle_User_Playlist_URL_Entry(user_name):
    #handles user input of spotify playlist url and decides if playlist needs to be added or is already added

    playlist_id = '';
    url = input('Please enter the spotify playlist url: ');
    while(True):
        if url.find('open.spotify.com/playlist/') != -1:
            print('Valid spotify playlist url has been entered. Checking if playlist is added for user: ' + user_name);
            url_parts = url.split('playlist/')[-1];
            match = re.search(r'[^a-zA-Z0-9]', url_parts);
            if match:
                playlist_id = url_parts[:match.start()];
            else:
                playlist_id = (url_parts);
            playlist_record = msGet_Playlist_In_Playlists_Table(playlist_id, user_name);
            if(playlist_record is None):
                print('Adding playlist to your list of playlists. Returning to main menu.');
                msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name);
                msPost_login_menu_headline();
                break;
            else:
                print('Playlist is already in your list of playlists. Returning to main menu.');
                msPost_login_menu_headline();
                break;
            break;
        else:
            url = input('Please enter a valid spotify playlist url');

def msHandle_User_Playlist_ID_Entry(user_name):
    #handles user input of spotify playlist id entry and decides if playlist needs to be added or is already added

    playlist_id = input("Please enter spotify playlist id: ");
    while(True):
        
        if is_valid_playlist_id(playlist_id):
            print('Valid spotify playlist id entered. Checking if playlist is added for user: ' + user_name);
            playlist_record = msGet_Playlist_In_Playlists_Table(playlist_id, user_name);
            if(playlist_record is None):
                print('Adding playlist to your list of playlists. Returning to main menu.');
                msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name);
                msPost_login_menu_headline();
                break;
            else:
                print('Playlist is already in your list of playlists. Returning to main menu.');
                msPost_login_menu_headline();
                break;
            
        else:
            playlist_id = input("Please enter a valid spotify playlist id: ");

def msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name):
    #inserts new playlist record into playlists table

    user_id = msGet_User_Id_Using_User_Name(user_name);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    c.execute('INSERT INTO playlists(user_id, playlist_id) VALUES (?,?)',(user_id, playlist_id));
    conn.commit();
    msClose_DB_Connection(c, conn);

def msGet_Playlist_In_Playlists_Table(playlist_id, user_name):
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    user_id = msGet_User_Id_Using_User_Name(user_name);
    playlistIdQueryCheckExecute = c.execute('SELECT * FROM playlists WHERE user_id = ? AND playlist_id = ?', (user_id,playlist_id));
    playlist_record = playlistIdQueryCheckExecute.fetchone();
    conn.commit();
    msClose_DB_Connection(c, conn);
    return playlist_record;

def msGet_All_Playlists_Using_User_ID(user_name):
    # returns an array using user_name

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    user_id = msGet_User_Id_Using_User_Name(user_name);
    playlistIdQueryCheckExecute = c.execute('SELECT * FROM playlists WHERE user_id = ?', (user_id,));
    playlists = playlistIdQueryCheckExecute.fetchone();
    conn.commit();
    msClose_DB_Connection(c, conn);
    return playlists;

def msGet_User_Playlist_Choice(playlists):
    playlist_id = '';
    if len(playlists) == 1:
        print('Since there is only one playlist saved, program will display that playlists tracks');
        playlist_id = playlists[0][0];
    else:
        playlist_choice = int(input('Please choose the playlist you want to view: '));
        while(True):
            try:
                #print(playlists[playlist_choice-1][0]);
                playlist_id = playlists[playlist_choice-1][0];
                break;
            except:
                
                print('Invalid option selected. Please try again with the below options.');
                msPrint_all_playlist_names(playlists);
                playlist_choice = int(input('Please choose the playlist you want to view from above: '));
    return playlist_id;

def msHandle_User_Playlist_Option(user_name):

    user_id = msGet_User_Id_Using_User_Name(user_name);
    
    playlists = msGet_Playlists_Using_User_ID(user_id);

    playlist_id ='';
    if(playlists == []):
        print('You need to have at least one playlist saved to pick one.');
        playlist_id = 'None';
    else:
        print('Which playlist would like you like to view');
        msPrint_all_playlist_names(playlists);
        playlist_id = msGet_User_Playlist_Choice(playlists);
        #msPrint_playlist_track_names(playlist_id);

    return playlist_id;

def msPost_login_menu_choice_2(userName):
    # displays all tracks in specified playlist

    playlist_id = msHandle_User_Playlist_Option(userName);

    if playlist_id == 'None':
        print('Returning to main menu');
    else:
        msPrint_playlist_track_names(playlist_id);

def msPost_login_menu_choice_3(user_name):
    # displays all playlists for specific user

    user_id = msGet_User_Id_Using_User_Name(user_name);

    playlists = msGet_Playlists_Using_User_ID(user_id);

    if(playlists == []):
        print('You need to have at least one playlist saved to display all of your playlists.');
    else:
        msPrint_all_playlist_names(playlists);

def msGet_User_Id_Using_User_Name(user_name):

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    userIDGetQueryExecute = c.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,));
    user_id = userIDGetQueryExecute.fetchone()[0];
    conn.commit();
    msClose_DB_Connection(c, conn);
    return user_id;        

def msGet_Playlists_Using_User_ID(user_id):
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    playlistsQueryExec = c.execute('SELECT playlist_id FROM playlists WHERE user_id = ?', (user_id,));
    playlists = playlistsQueryExec.fetchall();
    msClose_DB_Connection(c, conn);
    return playlists

def msPost_login_Menu(userName):
    msPost_login_menu_headline();
    choice = int(input('Please choose a option: '));
    while(True):
        if choice == 1:
            
            clear_screen();
            msPost_login_menu_choice_1(userName);
            
        if choice == 2:
            
            clear_screen();
            msPost_login_menu_choice_2(userName);
            
        if choice == 3:
            
            clear_screen();
            msPost_login_menu_choice_3(userName);
            
        if choice == 4:
            
            clear_screen();
            print('Thank you for using music suggest. Logging out');
            break;

        else:

            msPost_login_menu_headline();
            choice = int(input('Please choose another main menu option: '));

def msPrint_playlist_track_names(playlist_id):
    #display every track name in a playlist using playlist id provided

    playlist= sp.playlist(playlist_id);
    playlistTracks = playlist['tracks']['items'];
    for track in playlistTracks:
        try:
            print(track['track']['name']);
        except:
            pass
def msPrint_all_playlist_names(playlists):
    i = 1;
    for playlist in playlists:
        print(str(i) + ') ' +sp.playlist(playlist[0])['name']);
        i = i + 1;
def main():
    userName = msUser_Login();
    msPost_login_Menu(userName);
  
main();