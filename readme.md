# ChatterBot

This library allows developers to create language independent chat bots that
return responses to based on collections of known conversations.

[![Package Version](https://badge.fury.io/py/ChatterBot.png)](http://badge.fury.io/py/ChatterBot)
[![Build Status](https://travis-ci.org/gunthercox/ChatterBot.svg?branch=master)](https://travis-ci.org/gunthercox/ChatterBot)
[![PyPi](https://pypip.in/download/ChatterBot/badge.svg)](https://pypi.python.org/pypi/ChatterBot)
[![Coverage Status](https://img.shields.io/coveralls/gunthercox/ChatterBot.svg)](https://coveralls.io/r/gunthercox/ChatterBot)

An example of typical input would be something like this:
> user: Good morning! How are you doing?  
> bot:  I am doing very well, thank you for asking.  
> user: Your welcome.  
> bot: Do you like hats?  

## Installation

This package can be installed using
```
pip install chatterbot
```

## Useage

Create a new chat bot  
**Note:** This object takes an optional parameter for the bot's name.
```
from chatterbot import ChatBot
chatbot = ChatBot("Ron Obvious")
```

Getting a response to input text
```
response = chatbot.get_response("Good morning!")
print(response)
```

Specify a defult location for conversation log files  
**Note:** The default log directory is `conversation_engrams/`.
```
chatbot.log_directory = "path/to/directory/"
```

Terminal mode (User and chat bot)
```
from chatterbot import Terminal
terminal = Terminal()
terminal.begin()
```

Have the chat bot talk with CleverBot
```
from chatterbot import TalkWithCleverbot
talk = TalkWithCleverbot()
talk.begin()
```

## Notes

Sample conversations for training the chatbot can be downloaded
from https://gist.github.com/gunthercox/6bde8279615b9b638f71

This program is not designed to be an open source version of CleverBot.
Although this **Chat Bot** returns responces, the code here handels communication
much differently then [CleverBot](http://www.cleverbot.com) does.
