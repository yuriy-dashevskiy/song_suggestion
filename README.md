# Spotify Song Suggestion

## Overview 
 - Project was created to help determine spotify song suggestions using spotify playlists
---
## Dataset <br/>
- Spotify Data is gathered utilizing [Spotipy](https://github.com/spotipy-dev/spotipy) for spotify api calls <br/>
- Playlist IDs are stored locally in SQLite DB through the user adding the playlist url/id in the program

SQLite DB Setup <br/>
![image](https://github.com/user-attachments/assets/64571979-1b92-4f8b-805f-fe6a8a22002f)

Playlists Records Example <br/>
![image](https://github.com/user-attachments/assets/b297ccc0-bee1-4337-8da5-9e39d5555299)
- Spotify playlist is stored and tied to the user id from the users table

Users Table Records Example <br/>
![image](https://github.com/user-attachments/assets/4de404ae-20af-42ca-92bd-244bcf71aed0)
- Passwords stored in hash format for an extra level of security
- Note that passwords were removed from screenshot for security purpose
---
## Tools
* Python - Scripting language utilized for handling music suggestions and used TKinter for creating gui front end
* SQL - Stored custom user login and user playlists for spotify music suggestion in a SQLite DB
---
## Screenshots
Initial Screen <br/>
![image](https://github.com/user-attachments/assets/bb929672-0973-40c5-841e-d77a5a223724)

Main Menu Screen <br/>
![image](https://github.com/user-attachments/assets/af0cc9bf-4a4e-42ca-a14b-df87e1e8e508)

Playlist Choice Screen <br/>
![image](https://github.com/user-attachments/assets/baa2890e-eb38-44fb-84d3-bc8c7fa19803)

Random or Specific Artist Option Screen <br/>
![image](https://github.com/user-attachments/assets/b1160bd9-ac6f-479b-8af8-dc7af00d4a79)

All Tracks or Top Tracks Option Screen <br/>
![image](https://github.com/user-attachments/assets/b019fb56-9442-45c2-b523-7a4f8218d303)

Track Suggestion Screen <br/>
![image](https://github.com/user-attachments/assets/53d4bff1-3350-43d9-b386-024311eea149)

## Future Improvements
* Reduce load time when user has too many playlists saved
* Offer additional options when suggestion music (ex: giving user ability to enter artist name without needing playlist id)
