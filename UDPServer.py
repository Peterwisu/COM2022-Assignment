'''
This is COM2020 Computer Networking coursework assignment in years two second semster at University of Surrey 2022 

Author: Wish Suharitdamrong 

This is a Server UDP file  

'''

#######################################################################################################################

"""
    IMPORT ALL IMPORTANT LIBRARIES
"""
import numpy as np
import imutils
import socket
import time
import base64
import threading
import cv2
import os.path

"""
    IMPORTANT  for mac user type command 'sudo sysctl -w net.inet.udp.maxdgram=65535' to max buffer size for UDP
"""
# buff size
BUFF_SIZE = 65536

# Set Empty list for list client connected
client_list = []



# Dictionary of authourize client and password 
authorize_client = {
    "wish" : '1234',
    "peter" : '1234',
    'mouaz' : '1234',

}

'''
    Class Client
'''


class Client:
    """
        Constructor of class Client
    """

    def __init__(self, name, address):
        self.name = name
        self.address = address
      

    # get ip of client
    def get_IP(self):
        return self.address[0]

    # get port of client
    def get_Port(self):
        return self.address[1]
    
    def reset_time(self):
        self.time = 1
        
    def increment_time(self):
        self.time+=1
        
    def get_time(self):
        return self.time

    # display details of client
    def Tostring(self):
        return f' Username :- {self.name}  at  IP {self.get_IP()} and Port  {self.get_Port()}'


###########################################################################################################

'''  
   Function to create UDP Socket
'''


def create_udp_socket():
    global server_socket
    global host_ip
    global host_name
    global port

    try:
        # create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        # get name of a machine
        host_name = socket.gethostname()
        print('Host Name : - ', host_name)
        # get IP of machine by using host name
        host_ip = socket.gethostbyname(host_name)
        print('Host IP : - ', host_ip)
        # port number
        port =   int(input('Port number\n')) # 9998
    except socket.error as msg:
        # Print Error
        print(f'Create socket error : {msg}')
        print('Server closing')
        exit()
    except ValueError as msg:
        print(f'Port must be the number : {msg} ')
        print('Server closing')
        exit()

'''
    Function to bind UDP Socket
'''


def binding_socket():
    try:
        # Set address of a socket
        socket_address = ('0.0.0.0', port)
        # bind a socket
        server_socket.bind(socket_address)

        print('listening at :-', socket_address)
    except socket.error as msg:
        print(f'Binding socket error : {msg}')
        print('Server closing')
        exit()


'''
    Function to broadcast video to client
'''


def broadcast(conn_client):
    print(f'Trying to broadcasing video to client : {conn_client.Tostring()}')

    # Check if address exist in list exist in client connection list
    exist = conn_client.address in (i.address for i in client_list)
    # if exist is false the program will exit and end that thread that use for broadcasting

    while exist:

        try:
            # using 0 for web cam
            if source ==1 :
                vid = cv2.VideoCapture(0)
            else:
                vid = cv2.VideoCapture(file_path)
            print(f'Broadcasting video to user :{conn_client.Tostring()}')
            #set a size of video
            Width = 400
            # if webcam is open
            while vid.isOpened():

                _, image = vid.read()
        
                # resize frame
                frame = imutils.resize(image, width=Width)
                # encode image format into streaming data 
                endcoded, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Assigning data in a packet
                packet = 'VIDEO::'
                for i in buffer:
                    packet+=f'{i} '
                     
    
                # encode a image data from an array of number into byte ascii and encode it using base63 encoding again
                message = base64.b64encode(packet.encode('ascii'))
                # send to client
              
                server_socket.sendto(message, conn_client.address)
                # check whether client still connect to server if not change exist to false to exit both inner loop
                # and outter loop
                exist = conn_client.address in (i.address for i in client_list)
                
                if exist:
                    client_list[client_list.index(conn_client)].increment_time()
                   # print(client_list[client_list.index(conn_client)].get_time())
                    
                    if client_list[client_list.index(conn_client)].get_time() >= 100:
                        print('\n')
                        print('\n<---------------------------Client Timeout--------------------------->\n')
                        print(f'Connection Timeout from {conn_client.Tostring()} ')
                        print('\n<-------------------------------------------------------------------->')
                        disconnect_user(client_list[client_list.index(conn_client)].address)
                
                
                
                # if client disconnect exit the loop
                if exist == False  :
                    print(f"Client {conn_client.Tostring()} disconnected ")
                    # exit broadcasting loop
                    break


        except socket.error as err:
            print(f" error :  {err}")
            server_socket.close()
            break
        except AttributeError as err:
            print(f" Video have finished {err}")
            packet = 'FINISH::'
            server_socket.sendto(base64.b64encode(packet.encode('ascii')),conn_client.address)
            break

    print(f'Stop Broadcasting to client {conn_client.Tostring()}')


'''
    Show preview video of broadcast
'''


def preview():
    while True:
        Width = 400
        if source ==1 :
            vid = cv2.VideoCapture(0)
        else:
            vid = cv2.VideoCapture(file_path)
        fps, st, frames_to_count, cnt = (0, 0, 20, 0)
        while vid.isOpened():
            _, frame = vid.read()

            frame = imutils.resize(frame, width=Width)
            frame = cv2.putText(frame, 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow(f'Preview broadcast(q:quit)', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                server_socket.close()
                break
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count / (time.time() - st))
                    st = time.time()
                    cnt = 0
                except:
                    pass
            cnt += 1


'''
    Add address and name of client connected to a list and display list
'''


def connected_user(conn_client):
    # add client to a list
    client_list.append(conn_client)
    display_connection()


'''
    Remove address and name of client from list when it is disconnect
'''


def disconnect_user(client_addr):
    rm_client = None
    # Run loop through all client that connect
    for client in client_list:
        #  if address equal to client_addr
        if client.address == client_addr:
            # assign client to rm_client
            rm_client = client

    # Remove Client from List
    client_list.remove(rm_client)

    print('\n<--------------Disconnected------------------->')
    print(f'Client :{rm_client.Tostring()} have disconnected')
    print('<--------------------------------------------->\n')

    # display present connection
    display_connection()


'''
    Display list of all connection to a server
'''

def display_connection():
    # check if there is 0 connection
    if (len(client_list) == 0):
        print('\n<------------------------>')
        print(' 0 connection to a server ')
        print('<------------------------>\n')
    else:
        # Display all connections
        print('\n<-----------------------All Connecting Client----------------------->')
        for client in client_list:
            print(f'Client : {client.Tostring()}')

        print('<-------------------------------------------------------------------->\n')


def fake_id(client_name):
    
    con = False
    for c in client_list:
        
        if c.name == client_name:
            
            return True
        else :
            pass
   
    return con
    



'''
    Authentication login and password of user
'''

def client_auth(client_name,client_password):
        
    # check that username does exist in authorize list dictionary and check that the password match with password in dictionary according to user name
    if client_name in authorize_client.keys() and client_password == authorize_client[client_name] :
                
        return True
    else:
        return False

'''
    Handle multiple connection from client
'''

def handle_receive_connection():
    print('Waiting for client to connect ')
    while True:
        # Receive connection from client
        msg, client_addr = server_socket.recvfrom(BUFF_SIZE)
        # unpack packet
        msg = base64.b64decode(msg,b' /').decode('ascii')

        # split a message into multiple string seperate  by :
        msg_split = msg.split('::')

        # first index of array contain status of request
        status = msg_split[0]
        # second index of array is name of user 
        msg = msg_split[1]
       
       

        
        # if Status is quit then remove client
        if (status == 'QUIT'):
            disconnect_user(client_addr)
        # if status is RTT then pass this is for calculate RTT time in client and check whether is client is still connect if connect reset a time
        elif (status == 'RTT'):
        
           for i,client  in enumerate (client_list):
               if client.name == msg:
                   client_list[i].reset_time()
                  
        
        # if Status = LOGIN
        elif(status == 'LOGIN'):

            # if status is LOGIN the format should be LOGIN:username:password
            # get the pass word of user
            password = msg_split[2]


            # limit number of client  to 6
            if len(client_list) <=4:
                # add client connection to server
                print('\n<---------------------------Received Connection------------------------>')
                print(f'GOT connection from  IP and Port {client_addr} , with username {msg}')
                print('<---------------------------------------------------------------------->\n')

                existed = fake_id(msg)
                # pass username and password to authentication
                check = client_auth(msg, password )

                
                
                if(check and not existed):
                    
                    # send message to client to,let user know login has been authorize
                    server_socket.sendto(base64.b64encode(b'AUTHORIZE::'),client_addr)
                    # create new client object
                    conn_client = Client(msg, client_addr)
                    
                    conn_client.reset_time()
                    # add client to client list
                    connected_user(conn_client)
                    # start thread to handle broadcasting video to client
                    t2 = threading.Thread(target=broadcast, args=(conn_client,))
                    # start thread
                    t2.start()
                
                elif( check == False):
                      
                    print('Unauthorize user try to connect from address:',client_addr)
                    # send message to client to,let user know login has been rejected
                    server_socket.sendto(base64.b64encode(b'UNAUTHORIZE::'),client_addr)
                
                elif existed == True:
                    print(f' User  {msg} try to connect from address :{client_addr} but already login from other address')
                    # send message to client to,let user know login has been rejected
                    server_socket.sendto(base64.b64encode(b'EXISTED::'),client_addr)

            else:
                print('Unauthorize user try to connect from address:',client_addr)
                # send message to client to,let user know login has been rejected
                server_socket.sendto(base64.b64encode(b'FULL::'),client_addr)
        else:
            print('Unauthorize machine try to connect from address:',client_addr)
            pass


'''
    Start the server
'''
def start_server():
    
    global source
    global file_path 
    con =True
    while con:
        
        try:
            source = int(input('Enter 1 to use your webcam or 2 to use video file for broadcasting\n'))
            
            if source == 1 or source == 2 :
                con = False
                if(source == 2 ):
                    
                    file_path = str(input('please enter file path or file name\n'))
                    
                    if not os.path.isfile(file_path):
                        con = True
                        print ("File not exist")
                        raise Exception("File does not exist please try again")     
            else :
                
                raise Exception("Please try again Enter 1 to use your webcam or 2 to use video file for broadcasting")     
            
        except ValueError as err:
            print('Please try again Enter 1 to use your webcam or 2 to use video file for broadcasting')
        except Exception as err:
            print(err)
        
    create_udp_socket()
    binding_socket()
    handle_receive_connection()


start_server()
