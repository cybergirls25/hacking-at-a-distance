from flask import Flask, render_template_string, request
import RPi.GPIO as gpio

app = Flask(__name__)

# GPIO setup
gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.OUT)
gpio.setup(22, gpio.OUT)
gpio.setup(23, gpio.OUT)
gpio.setup(24, gpio.OUT)

# Motor control functions
def stop():
    gpio.output(17, False)
    gpio.output(22, False)
    gpio.output(23, False)
    gpio.output(24, False)

def forward():
    stop()
    gpio.output(22, True)
    gpio.output(23, True)

def reverse():
    stop()
    gpio.output(17, True)
    gpio.output(24, True)

def left_turn():
    stop()
    gpio.output(17, True)
    gpio.output(23, True)

def right_turn():
    stop()
    gpio.output(22, True)
    gpio.output(24, True)

# HTML template (black and white style)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Control Panel</title>
    <style>
        :root {
            --primary: #ffffff;
            --background: #000000;
            --text: #ffffff;
            --button-bg: #ffffff;
            --button-text: #000000;
        }

        body {
            background-color: var(--background);
            font-family: 'Poppins', sans-serif;
            color: var(--text);
            margin: 0;
            padding: 40px;
            text-align: center;
        }

        h1 {
            font-size: 3em;
            margin-bottom: 40px;
            text-shadow: 0 0 10px red;
        }

        .controls {
            background-color: #111;
            border-radius: 15px;
            padding: 30px;
            display: inline-block;
            border: 2px solid var(--primary);
        }

        .button-row {
            margin: 15px 0;
        }

        button {
            background-color: var(--button-bg);
            color: var(--button-text);
            border: none;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 1.2em;
            margin: 0 10px;
            cursor: pointer;
            transition: 0.3s;
            min-width: 120px;
        }

        button:hover {
            background-color: #ccc;
            color: #000;
        }

        #videoFeed {
            margin-top: 30px;
            max-width: 640px;
            width: 100%;
            border: 3px solid var(--primary);
            border-radius: 10px;
        }

        .refresh-btn {
            margin-top: 20px;
            background-color: var(--primary);
            color: var(--background);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
        }

        .refresh-btn:hover {
            background-color: #ccc;
            color: #000;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap" rel="stylesheet">
</head>
<body>
    <h1>Robot Control Panel</h1>

    <div class="controls">
        <div class="button-row">
            <button onclick="sendCommand('forward')">Forward</button>
        </div>
        <div class="button-row">
            <button onclick="sendCommand('left')">Left</button>
            <button onclick="sendCommand('stop')" style="background:#999;color:#fff;">Stop</button>
            <button onclick="sendCommand('right')">Right</button>
        </div>
        <div class="button-row">
            <button onclick="sendCommand('reverse')">Reverse</button>
        </div>
    </div>

    <div>
<img id="videoFeed" src="http://192.168.1.116/stream" alt="Live Feed">

    <script>
        function sendCommand(cmd) {
            fetch('/' + cmd).catch(err => console.error('Command error:', err));
        }
    </script>

</body>
</html>
"""

# Flask routes
@app.route('/')
def control_panel():
    return render_template_string(HTML_TEMPLATE)

@app.route('/forward')
def move_forward():
    forward()
    return "OK"

@app.route('/reverse')
def move_reverse():
    reverse()
    return "OK"

@app.route('/left')
def turn_left():
    left_turn()
    return "OK"

@app.route('/right')
def turn_right():
    right_turn()
    return "OK"

@app.route('/stop')
def stop_motors():
    stop()
    return "OK"

if __name__ == '__main__':
    try:
        print("Robot server running at http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        gpio.cleanup()