
# aChat is for Anonymous Chat 😉
First of all this is not a hacking project. This is a simple chat server. You can connect many clients as you want to the server, after that you can connect to another partner and start chatting. The server will recive your message and formard it to the other client.
## Download the Project
Downloading proccess is simple. Just clone the repository or click [here](https://codeload.github.com/0301yasiru/ServerClient/zip/main) to download.

    git clone https://github.com/0301yasiru/aChat.git

## Installation of server
This server script does not require any special liblaries. **And both scripts are programmed to work on both Linux and Wondows** (*better on linux*). So you can run the server scripts directly. Here are the steps,

 1. Firsly, locate the main script of the server.<br>
  `cd cd ServerClient\server\`
  
 2. Then, the most importantly you have to edit the config.conf file. It contans the port, host, blacklist, whitelist etc.<br>
  `nano config.conf`

 4. Then, run the main script using python 3.<br>
  `python3 main.py`

## Installation of Client
This proccess also very simple because it doest not require any special liblaries. **The only thing you have to do is setup the config.conf file** but you have two ways to deal with it. 

> (The Format of the Config File)<br>
	client_id: 0302yasiru [this is your username]<br>
	host: 192.168.1.4 [this is the servers IP]<br>
	port: 5050 [this is the connection port]<br>

 1. Firsly locate the client directory.<br>
  `cd cd ServerClient\client\`
  
 2. If you have a propper text editor use it to edit config.conf file<br>
  `nano client.conf`
  
 3. If you don't (for android phones) use setup.py script.<br>
  `python3 setup.py`
  
 4. Finally, run the client script<br>
 `python3 main.py`

## How to start the server
Before you start the server you must have configured the config file. You can do ith with the **main.py** or editing the config file.

 1. Firsly run the main script (After locating the server directory).<br>
 `python3 main.py`
 
 2. Configure the server using commands.<br>
	 a. Use **show** command to view configuration of server blacklist ... etc.<br>
	 `#SERVER/> show server`<br>
	 `#SERVER/> show blacklist`<br>
	 `#SERVER/> show whitelist`<br>
	 b. Use **set** command to set port and host in the server configuration.<br>
	 `set server port 5151`<br>
	 `set server host 192.168.1.56`<br>
	 c. Use **add/remove** command to add or remove clients to blacklist or whitelist.<br>
	 `blacklist add 0301yasiru`<br>
	 `blacklist remove someuser`<br>
	 `whitelist add 0301yasiru`<br>
	 `whitelist remove 0301yasiru__`<br>
	 d. Finally, use **start/run** command to start the server.<br>
	 `run`<br>

 3. After you start the server you can use following utility commands.<br>
	 a. Use **clients** commands to view the connected clients.<br>
	 `clients`<br>
	 b. Use **clear** command to clear the screen.<br>
	 `clear`<br>
	 c. Use **poweroff** command to shut down the server.<br>
	 `poweroff`<br>

## How to Use Client
This is the easiest in this article. After you configured **client.conf** file you can run the client script.

 1. Firtly locate the client directory.<br>
 `cd ServerClient\client\`<br>
 
 2. Then run the main script using python3.<br>
 `python3 main.py`<br>
 
 3. After client program started, you can connect to another client or you can wait until some other client connects you. If you want to communicate to another client you must know his/her **user name**. You can connect your partner using **connect** command.<br> 
 `connect <partners username>`<br>
 `connect 0301yasiru`<br>
