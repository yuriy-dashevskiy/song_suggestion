import spotipy
import hashlib
import sqlite3
from spotipy.oauth2 import SpotifyOAuth
import spotify_api_keys as keys

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
    
    print("New User");
    userNameInput = input('Enter new user name: ');
    while(True):
        conn = msGet_DB_Connection();
        c = msGet_DB_Cursor(conn);
        queryExecute = c.execute('SELECT * FROM users WHERE user_name = ?;', (userNameInput,));
        userRecord = queryExecute.fetchone();
        msClose_DB_Connection(c, conn);
        if(userRecord is None):
            #print('Success');
            break;
        else:
            userNameInput = input('Please enter a user name that is not taken: ');
    while(True):
        userPassInput = input('Please enter your password: ');
        hashInput = hashlib.sha224(userPassInput.encode('utf-8')).hexdigest();
        #print(userNameInput);
        #print(hashInput);
        conn = msGet_DB_Connection();
        c = msGet_DB_Cursor(conn);
        queryExecute = c.execute('SELECT MAX(user_id) FROM users');
        maxID = int(queryExecute.fetchone()[0]);
        c.execute('INSERT INTO users(user_id, user_name, password) VALUES (?,?,?)',(maxID + 1, userNameInput, hashInput));
        conn.commit();
        msClose_DB_Connection(c, conn);
        break;
    return userNameInput;

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
            print("Please type in a valid user name and password");
            userNameInput = input('User Name: ');
            userPassInput = input('Password: ');
            userPassHash = hashlib.sha224(userPassInput.encode('utf-8')).hexdigest();
        else:
            print("Successfully logged in");
            break;
    return userNameInput;
def msPost_login_menu_headline():
    
    print("Welcome to music suggestions");
    print("What option would you like to pick");
    print("Option 1: Add playlist to your playlists");
    print("Option 2: Display all tracks in a specific playlist");
    print("Option 3: Display all of your playists");
    print("Option 4: Exit");
                  
def msPost_login_menu_choice_1(userName):
    
    return 0;

def msPost_login_menu_choice_2(userName):
    
    return 0;

def msPost_login_menu_choice_3(userName):

    print(userName);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    userIdQueryExec = c.execute('SELECT user_id FROM users WHERE user_name = ?', (str(userName),));
    print('query1');
    userID = userIdQueryExec.fetchone()[0];
    msClose_DB_Connection(c, conn);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    playlistsQueryExec = c.execute('SELECT playlist_id FROM playlists WHERE user_id = ?', (userID,));
    print('query2');
    playlists = playlistsQueryExec.fetchall();
    msClose_DB_Connection(c, conn);
    for playlist in playlists:
        print(playlist[0]);

def msPost_login_Menu(userName):
    msPost_login_menu_headline();
    choice = int(input("Please choose a option: "));
    while(True):
        if choice == 1:
            break;
        if choice == 2:
            break;
        if choice == 3:
            msPost_login_menu_choice_3(userName);
            break;
        if choice == 4:
            print('Thank you for using music suggest. Logging out');
            break;
        else:
            choice = int(input("Please choose a valid option: "));

def msPrint_playlist_track_names(playlist_id):
    playlist= sp.playlist(playlistId);
    playlistTracks = playlist['tracks']['items'];
    for track in playlistTracks:
        try:
            print(track['track']['name']);
        except:
            pass
def main():
    userName = msUser_Login();
    msPost_login_Menu(userName);
    
main();

