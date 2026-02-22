# LaskerChampClient
a site for playing chess againts engines or real people

the site is located at [laskerchamp](http://laskerchamp.herokuapp.com).

the site has full proof sql injection protection on the login and registration page.

the site uses cookies in order to identify the client upon entering the game page, the cookie is unique for each client and lasts practecly forever on the browser unless you log out.

the site is codded on the back end with python and postgresql to save the data using the following:
* aiohttp
* psycopg3
* socketio
* chess
* stockfish

on the front end its codded with css html and js using:
* chessboard.js
* chess.js
* socketio

Run the application using the following command

```
chmod +x run.sh
./run.sh
```
