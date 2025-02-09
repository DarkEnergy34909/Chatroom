from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

def initialise_database():
    con = sqlite3.connect("chatroom.db")
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS Message(MessageID INTEGER PRIMARY KEY AUTOINCREMENT, Message TEXT, Username TEXT, Timestamp TEXT)")
    con.commit()
    con.close()

# Returns the most recent 30 messages from the database
def fetch_messages():
    con = sqlite3.connect("chatroom.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM Message ORDER BY Timestamp")
    messages = res.fetchall()
    con.commit()
    con.close()

    # Only return the most recent 100 messages
    if (len(messages) > 100):
        messages = messages[-100:]

    return messages

def insert_test_messages():
    con = sqlite3.connect("chatroom.db")
    cur = con.cursor()

    cur.execute("INSERT INTO Message(Message, Username, Timestamp) VALUES(?, ?, ?)", ("HELLO", "User1", "2021-09-01 12:00:00"))
    con.commit()    
    cur.execute("INSERT INTO Message(Message, Username, Timestamp) VALUES(?, ?, ?)", ("BYE", "User2", "2021-09-01 12:01:00"))
    con.commit()
    con.close()

def insert_message(message, username):
    con = sqlite3.connect("chatroom.db")
    cur = con.cursor()

    cur.execute("INSERT INTO Message(Message, Username, Timestamp) VALUES(?, ?, datetime('now'))", (message, username))
    con.commit()
    con.close()

@app.route("/", methods=["GET", "POST"])
def main_menu():
    return render_template("index.html")

@app.route("/chatroom", methods=["GET", "POST"])
def chatroom():
    if (request.method == "GET"):
        # Get username from GET parameters
        requestData = request.args
        print(requestData)
        username = requestData["username"]

        # Get all messages from the database
        messages = fetch_messages()

        if ("username" not in requestData):
            return "Please enter a valid username in the main menu to enter the chatroom."
        else:
            return render_template("chatroom.html", username=username, messages=messages)
    else:
        # Get the username from the form
        requestData = request.form
        username = requestData["username"]

        if (username == ""):
            return "Please enter a valid username to enter the chatroom."
        else:
            # Check if the user has entered a message, if so, insert it into the database
            if ("message" in requestData):
                message = requestData["message"]
                insert_message(message, username)
                # print(requestData)
            messages = fetch_messages()
            print(messages)

            return render_template("chatroom.html", username=username, messages=messages)
        
@app.route("/messages", methods=["GET"])
def get_messages():
    messages = fetch_messages()
    return {'messages': messages}

# SocketIO event handler
@socketio.on("send_message")
def handle_send_message_event(data):
    print(data)
    username = data["username"]
    message = data["message"]

    insert_message(message, username)
    messages = fetch_messages()
    
    # Send the message to all clients
    emit("receive_message", {"messages": messages}, broadcast=True)



if (__name__ == "__main__"):
    initialise_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
