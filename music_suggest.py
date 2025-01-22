import hashlib
import os
import random
import re
import spotify_api_keys as keys
import spotipy
import sqlite3
import logging
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

def clear_screen():
    #clears the screen

    # For Windows
    if os.name == 'nt':
        _ = os.system('cls') 

    # For macOS and Linux
    else:
        _ = os.system('clear')

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

def msHandle_Initial_Menu():
    #outputs the options for login screen and returns the choice picked

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
    #handles initial choise between creating new users or logging in as existing user

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
    #handles login of existing users
    
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
    #outputs list of options available to the user to choose

    menu = """
Welcome to music suggestions
What option would you like to pick?
Option 1: Add playlist to your playlists
Option 2: Delete playlist from your playlists
Option 3: Display all tracks in a specific playlist
Option 4: Display all of your playists
Option 5: Suggest songs for your playlist
Option 6: Exit""";
    print(menu);

def is_valid_playlist_id(playlist_id):
    # returns boolean if playlist id is a valid spotify playlist id

    try:
        sp.playlist(playlist_id) ;
        return True;
    except spotipy.exceptions.SpotifyException as e:
        return False;        
def msHandle_User_Playlist_ID_Entry(user_name):
    #handles user input of spotify playlist id entry and decides if playlist needs to be added or is already added

    playlist_id = input("Please enter spotify playlist id: ");
    while(True):
        
        if is_valid_playlist_id(playlist_id):
            print('Spotify playlist id has been entered. Checking if playlist is added for user: ' + user_name);
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

def msDelete_Playlist_Record_Into_Playlists(playlist_id, user_name):
    #deletes specified playlist record from playlists table

    user_id = msGet_User_Id_Using_User_Name(user_name);
    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    c.execute('DELETE FROM playlists WHERE user_id = ? AND playlist_id = ?',(user_id, playlist_id));
    conn.commit();
    msClose_DB_Connection(c, conn);

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

def msGet_User_Playlist_Choice(playlists, action):
    #returns the playlist id based on which playlist user chooses from their playlist and the action they are looking to do

    playlist_id = '';
    if len(playlists) == 1:
        print('Since there is only one playlist listed for you, program will ' + action + ' for this playlist.');
        if action == 'remove':
            print('Do you wish to delete the only playlist record saved?');
            removal_input = input('Please write yes or no if you want to delete.');
            while(True):
                if removal_input == 'yes':
                    print('Thank you for confirming. Program will delete playlist ' + sp.playlist([playlists[0][0]])['name'] + ' from your playlists records');
                    playlist_id = playlists[0][0];
                    break;
                elif removal_input == 'no':
                    playlist_id = 'None';
                    break;
                else:
                    removal_input = input('Please try again. Type in yes or no if you want to delete: ');
    else:
        print('Which playlist would like you like to '+ action);
        msPrint_all_playlist_names(playlists);
        playlist_choice = int(input('Please choose the playlist you want to ' + action + ': '));
        while(True):
            try:
                #print(playlists[playlist_choice-1][0]);
                playlist_id = playlists[playlist_choice-1][0];
                if action == 'remove':
                    print('Do you wish to delete playlist ' + sp.playlist(playlist_id)['name'] + ' from your records?');
                    removal_input = input('Please write yes or no if you want to delete: ');
                    while(True):
                        if removal_input == 'yes':
                            print('Thank you for confirming. Program will delete playlist ' + sp.playlist(playlist_id)['name'] + ' from your playlists records');
                            break;
                        elif removal_input == 'no':
                            playlist_id = 'None';
                            break;
                        else:
                            removal_input = input('Please try again. Type in yes or no if you want to delete.');
                break;
            except:
                
                print('Invalid option selected. Please try again with the below options.');
                msPrint_all_playlist_names(playlists);
                playlist_choice = int(input('Please choose the playlist you want to ' + action + ' from above: '));

    return playlist_id;

def msHandle_User_Playlist_Option(user_name, action):
    #returns playlist_id based on provided user_name and the action they choose to perform
    user_id = msGet_User_Id_Using_User_Name(user_name);
    
    playlists = msGet_Playlists_Using_User_ID(user_id);

    playlist_id ='';
    if(playlists == []):
        print('You need to have at least one playlist saved to pick one.');
        playlist_id = 'None';
    else:
        #msPrint_all_playlist_names(playlists);
        playlist_id = msGet_User_Playlist_Choice(playlists, action);
        #msPrint_playlist_track_names(playlist_id);

    return playlist_id;

def msHandle_User_Playlist_URL_Entry(user_name):
    #handles user input of spotify playlist url and decides if playlist needs to be added or is already added

    playlist_id = '';
    url = input('Please enter the spotify playlist url: ');
    while(True):
        if url.find('open.spotify.com/playlist/') != -1:
            print('Spotify playlist url has been entered. Checking if playlist is added for user: ' + user_name);
            url_parts = url.split('playlist/')[-1];
            match = re.search(r'[^a-zA-Z0-9]', url_parts);
            if match:
                playlist_id = url_parts[:match.start()];
            else:
                playlist_id = (url_parts);
            playlist_record = msGet_Playlist_In_Playlists_Table(playlist_id, user_name);
            if(playlist_record is None):
                if is_valid_playlist_id(playlist_id):
                    print('Adding playlist to your list of playlists. Returning to main menu.');
                    msInsert_Playlist_Record_Into_Playlists(playlist_id, user_name);
                    break;     
                else:
                    url = input('Invalid spotify playlist url. Please enter a valid spotify playlist url: ');
                
            else:
                print('Playlist is already in your list of playlists. Returning to main menu.');
                break;
        else:
            url = input('Please enter a valid spotify playlist url: ');

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
            choice = int(input('Please try again. Enter 1 or 2 for your choice: '));

def msPost_login_menu_choice_2(user_name):
    # allows user to remove a playlist from their list of playlists

    user_id = msGet_User_Id_Using_User_Name(user_name);
    
    playlists = msGet_Playlists_Using_User_ID(user_id);

    playlist_id ='';
    if playlists == []:
        print('You need to have at least one playlist saved to delete.');
    else:
        #msPrint_all_playlist_names(playlists);
        playlist_id = msGet_User_Playlist_Choice(playlists, 'remove');
        if playlist_id == 'None':
            print('No playlist will be deleted. Returning to main menu');
        else:
            msDelete_Playlist_Record_Into_Playlists(playlist_id, user_name);
            print('Record has been deleted.');

def msPost_login_menu_choice_3(user_name):
    # displays all tracks in specified playlist

    playlist_id = msHandle_User_Playlist_Option(user_name, 'view');

    if playlist_id == 'None':
        print('Returning to main menu');
    else:
        msPrint_playlist_track_names(playlist_id);

def msPost_login_menu_choice_4(user_name):
    # displays all playlists for specific user

    user_id = msGet_User_Id_Using_User_Name(user_name);

    playlists = msGet_Playlists_Using_User_ID(user_id);

    if playlists == []:
        print('You need to have at least one playlist saved to display all of your playlists.');
    else:
        msPrint_all_playlist_names(playlists);

def msPost_login_menu_choice_5(user_name):
    #handles music suggestion feature

    user_id = msGet_User_Id_Using_User_Name(user_name);

    playlists = msGet_Playlists_Using_User_ID(user_id);

    if playlists == []:
        print('You need to have at least one playlist to get music suggestions for');
    else:
        playlist_id = msGet_User_Playlist_Choice(playlists, 'get music suggestions');
        print('Would you like to top track suggestions or all song suggestions');
        track_suggestion_input = int(input('Please enter 1 for Top Tracks or 2 for All Tracks: '));
        while(True):
            if track_suggestion_input == 1:
                msHandle_Music_Suggestion(playlist_id, 'top');
                break;
            elif track_suggestion_input == 2:
                msHandle_Music_Suggestion(playlist_id, 'all');
                break;
            else:
                track_suggestion_input = int('Invalid entry. Please enter 1 for Top Tracks or 2 for All Tracks: ');

def msHandle_Music_Suggestion(playlist_id, action):
    #handles user choosing computer to decide the artist or they can pick the artist for music suggestion

    options = """"
Would you like music suggestion of a random artist or a specific artist in your playlist?
Option 1: Pick a random artist from your playlist to get song suggestions.
Option 2: Pick a specific artist from your playlist to get song suggestions.
""";

    playlist_artist_dict = msGet_Playlist_Artist_Sorted_Dictionary(playlist_id);
    i = 1;
    for id in playlist_artist_dict:
        print(str(i) + ')' + playlist_artist_dict[id]);
        i = i + 1;
    print(options);
    music_suggestion_input = int(input('Pick one of the options above: '));

    while(True):

        if music_suggestion_input == 1:
            if action == 'top':
                msHandle_Artist_Song_Suggestion(playlist_artist_dict, playlist_id, 'random', 'their top');
            else:
                msHandle_Artist_Song_Suggestion(playlist_artist_dict, playlist_id, 'random', 'all their');
            break;
            
        elif music_suggestion_input == 2:
            if action == 'top':
                msHandle_Artist_Song_Suggestion(playlist_artist_dict, playlist_id, 'specific', 'their top');
            else:
                msHandle_Artist_Song_Suggestion(playlist_artist_dict, playlist_id, 'specific', 'all their');
            break;

        else:
            music_suggestion_input = int(input('Please try again. Enter 1 or 2 for the options listed above: '));

def msPrint_Artist_Sorted_Dictionary(playlist_artist_dictionary):
    #prints the values in the playlist_artist_dictionary

    i = 1;
    pad = playlist_artist_dictionary;
    for key in pad:
        print(str(i) + ') ' + pad[key]);
        i = i + 1;

def msGet_All_Tracks_Of_Artist(artist_id):

    songs = [];

    # Get artist's albums
    albums = sp.artist_albums(artist_id, album_type='album,single,appears_on')
    for album in albums['items']:
        # Get tracks for each album
        tracks = sp.album_tracks(album['id'])
        #for track in tracks['items']:
         #   songs.append({
        #        'name': track['name'],
        #        #'album': album['name'],
                #'artist': track['artists'][0]['name'],
                #'id':track['id']
        #    })
        songs.append(tracks);

    return songs;

def msHandle_Artist_Song_Suggestion(playlist_artist_dict, playlist_id, action, total):
    #handles the song suggestion based on action, playlist_id and playlist_artist_dict provided

    pad = playlist_artist_dict;
    artist_list = [];
    artist_id = '';
    if action == 'specific':
        msPrint_Artist_Sorted_Dictionary(pad);
        print('Pick an artist using the number next to them to start song suggestion');

        i = 1;
        for artist in pad:
            print(str(i) + ') ' + pad[artist]);
            artist_list.append([artist]);
            i = i + 1;
        artist_choice = int(input('Enter a number option next to the artist name: '));

        while(True):
            if 1 <= artist_choice <= i :
                artist_id = artist_list[artist_choice-1][0];
                print('Artist ' + pad[artist_id] + ' has been picked');
                print('Suggested songs to add/listen to from ' + total + ' tracks');
                songs_list = msGet_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id)
                if total == 'their top':
                    tracks = sp.artist_top_tracks(artist_id)['tracks'];
                    msPrint_List_of_Top_Tracks_Not_In_Playlist(tracks, songs_list);
                else:
                    tracks = msGet_All_Artist_Songs(artist_id);
                    msPrint_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list);
                break;
            else:
                artist_choice = int(input('Please enter a valid number next to the artists listed above: '));
    else:
        print('Picking an artist at random from your playlist');
        i = 1;
        for artist in pad:
            print(str(i) + ') ' + pad[artist]);
            artist_list.append([artist]);
            i = i + 1;
        artist_choice = random.randint(1,i);
        artist_id = artist_list[artist_choice-1][0];        
        print('Artist ' + pad[artist_id] + ' has been picked at random');
        print('Suggested songs to add/listen to from ' + total +' tracks');
        songs_list = msGet_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id)
        if total == 'their top':
            tracks = sp.artist_top_tracks(artist_id)['tracks'];
            msPrint_List_of_Top_Tracks_Not_In_Playlist(tracks, songs_list);
        else:
            tracks = msGet_All_Artist_Songs(artist_id);
            msPrint_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list);  

def msPrint_List_of_Top_Tracks_Not_In_Playlist(tracks, songs_list):
    #prints tracks not in songs list

    for track in tracks:
            if track['name'] not in songs_list:
                print(track['name']);

def msPrint_List_of_All_Tracks_Not_In_Playlist(tracks, songs_list):
    #prints tracks not in songs list

    for track in tracks:
            if track not in songs_list:
                print(track);

def msPrint_List_of_Ten_Random_All_Tracks_Not_In_Playlist(tracks, songs_list):
    #prints ten random tracks of a specific artists tracks not in songs list

    songs_not_in_list = [];
    for track in tracks:
        if track not in songs_list:
                songs_not_in_list.append(track);
    size = len(songs_not_in_list);
    if size < 11:
        for track in songs_not_in_list:
            print(track);
    else:
        i = 1;
        index_list = [];
        while i < 11:
            random_index =  random.randint(0, len(songs_not_in_list)-1);
            if random_index not in index_list:
                print(songs_not_in_list[random_index]);
                index_list.append(random_index);
                i = i + 1; 

def msGet_Playlist_Artist_Sorted_Dictionary(playlist_id):
    #returns a sorted dictionary of artists in a playlist using playlist_id

    artist_id_list = {};
    playlist =  sp.playlist(playlist_id);
    print('Artists in Playlist: ' + playlist['name']);
    playlistTracks = playlist['tracks']['items'];

    for track in playlistTracks:
        try:
            temp = track['track']['artists'][0]['id'];
            tempName = track['track']['artists'][0]['name'];
            artist_id_list[temp] = tempName;
        except:
            pass

    new_artist_id_list = dict(sorted(artist_id_list.items(), key = lambda item: item[1]));

    return artist_id_list;

def msGet_User_Id_Using_User_Name(user_name):
    #queries the users table to get user_id using user_name value

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    userIDGetQueryExecute = c.execute('SELECT user_id FROM users WHERE user_name = ?', (user_name,));
    user_id = userIDGetQueryExecute.fetchone()[0];
    conn.commit();
    msClose_DB_Connection(c, conn);
    return user_id;        

def msGet_Playlists_Using_User_ID(user_id):
    #queries the playlist table to get list of playlists using user_id value

    conn = msGet_DB_Connection();
    c = msGet_DB_Cursor(conn);
    playlistsQueryExec = c.execute('SELECT playlist_id FROM playlists WHERE user_id = ?', (user_id,));
    playlists = playlistsQueryExec.fetchall();
    msClose_DB_Connection(c, conn);
    return playlists

def msPost_login_Menu(user_name):
    #handles menu after logging in

    msPost_login_menu_headline();
    choice = int(input('Please choose a option: '));
    while(True):
        if choice == 1: clear_screen(); msPost_login_menu_choice_1(user_name);
            
        if choice == 2: clear_screen(); msPost_login_menu_choice_2(user_name);
            
        if choice == 3: clear_screen(); msPost_login_menu_choice_3(user_name);

        if choice == 4: clear_screen(); msPost_login_menu_choice_4(user_name);

        if choice == 5: clear_screen(); msPost_login_menu_choice_5(user_name);
            
        if choice == 6:
            
            clear_screen();
            print('Thank you for using music suggest. Logging out');
            break;

        else:

            msPost_login_menu_headline();
            choice = int(input('Please choose another main menu option: '));

def msGet_Songs_From_Playlist_From_Specific_Artist(artist_id,playlist_id):
    #returns list of specific artist songs in specific playlist

    songs_list = [];
    playlist= sp.playlist(playlist_id);
    playlistTracks = playlist['tracks']['items'];

    i = 1;
    for track in playlistTracks:
        try:
            specific_track = track['track']['artists'][0];
            #print(specific_track);
            if specific_track['id'] == artist_id:
                songs_list.append(track['track']['name']);

            i = i + 1;
        except:
            pass
    
    return songs_list;

def msGet_All_Artist_Songs(artist_id):
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

def msPrint_playlist_track_names(playlist_id):
    #display every track name in a playlist using playlist id provided

    playlist= sp.playlist(playlist_id);
    print('Playlist: ' + playlist['name']);
    playlistTracks = playlist['tracks']['items'];
    i = 1;
    for track in playlistTracks:
        try:
            print(str(i) + ') ' + track['track']['name']);
            i = i + 1;
        except:
            pass

def msPrint_all_playlist_names(playlists):
    #prints every playlist name in playlists provided

    i = 1;
    for playlist in playlists:
        try:
            print(str(i) + ') ' +sp.playlist(playlist[0])['name']);
            i = i + 1;
        except:
            print('404 for record');

def main():
    #handles main execution of the program

    userName = msUser_Login();
    msPost_login_Menu(userName);

main();