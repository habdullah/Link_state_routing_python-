from socket import *
from priodict import priorityDictionary
import sys
import thread
import json
import time
import threading
import collections


counter =0;
Table = []
deadarr = {}
#first time counters. 
c = 0
d = 0
#Dijkstra algo taken from https://www.ics.uci.edu/~eppstein/161/python/dijkstra.py


def shortestPath(G,start,end):
    
    D,P = djsktra(G,start,end)
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        end = P[end]
    Path.reverse()
    return Path,D


def djsktra(G,start,end=None):
    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors
    Q = priorityDictionary()
    Q[start] = 0
    
    for v in Q:
        D[v] = Q[v]
        if v == end: break
        
        for w in G[v]:
            vwLength = D[v] + G[v][w]
            if w in D:
                if vwLength < D[w]:
                    raise ValueError, \
  "Dijkstra: found better path to already-final vertex"
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v
    return (D,P)

graph =  {}


def main():
    IP = "localhost"
    ID = sys.argv[1]
    port_no = sys.argv[2]
    file = sys.argv[3]

    print "-I'm router",sys.argv[1]
    print "-I'm listening on port",sys.argv[2]
    print "-Config file entered:",sys.argv[3]

    
    f = open(file,'r')
    n = f.readline()
    global Table
    for line in f:
        Table.append(line.split())
    f.close()

    #initially add my own neighbours to the graph list
    temp = {}
    for i in range(len(Table)):
            temp[Table[i][0]]=float(Table[i][1])
            Table[i][1]=float(Table[i][1])
    graph[ID]=temp
    t=threading.Thread(target=send_packet,kwargs={'table':Table,'ID':ID,'flag':0})
    t1=threading.Thread(target=rcv_packet,kwargs={'portno':port_no})
    t2=threading.Thread(target=dijkstra,kwargs={'graphh':graph})
    
    t.start()
    t1.start()
    t2.start()
    
    while 1:
        pass

def send_packet(table,ID,flag):

    seq = 0
    
    while True:
        explored = []
        port = []
        IP = "localhost"
        Id = ID 
        global counter
        routerSocket = socket(AF_INET,SOCK_DGRAM)
        tmp = []

    #["A", "A", 1, [["B", "6.5", "5001"]]]
       
        
        explored.append(sys.argv[1])
        


        if flag:
            table1 = table[3]

            localcounter = 0
            
            #adding nodes to graph 
            temp = {}
            for x in table1:
                temp[str(x[0])]=x[1]


            graph[str(table[0])]=temp 
            forwardexplored = table[1]
            for i in range(len(Table)):
                port.append(Table[i][2])

            for i in range(len(Table)):
                if Table[i][0] not in forwardexplored:
                    forwardexplored.append(Table[i][0])
                    tmp.append(i)
        else:
            for i in range(len(table)):
                explored.append(table[i][0])
                port.append(table[i][2])

        k = len(port)
        for i in range(0,k):

            if flag:
                if i in tmp:
                    message = [Id,forwardexplored,seq,table1]
                    message = json.dumps(message)
                    message = message.encode('utf-8')
                    routerSocket.sendto(message,(IP,int(port[i])))
                else:
                    continue
            else:
                message = [Id,explored,seq,Table]
                message = json.dumps(message)
                message = message.encode('utf-8')
                routerSocket.sendto(message,(IP,int(port[i])))

        seq = seq + 1
        if flag:
            return
        time.sleep(1)


def rcv_packet(portno):
    global deadarr
    IP = "localhost"
    port = portno
    global recvtable
    seq1 = 0

    rcvSock = socket(AF_INET,SOCK_DGRAM)
    
    rcvSock.bind((IP,int(port)))

    while True:
        data, addr = rcvSock.recvfrom(4096) # buffer size is 4096 bytes
        data = data.decode('utf-8')
        first_data = json.loads(data)
        if first_data[0] in deadarr:#if no data has been received from this node
            if deadarr[first_data[0]] == 0:
                    deadarr[first_data[0]] = 1
        forwardthrd=threading.Thread(target=send_packet,kwargs={'table':first_data,'ID':first_data[0],'flag':1})
        forwardthrd.start()



def dijkstra(graphh):
    global c
    global deadarr
    global graph
    tmp = {}
    tmp2=[]
    while 1:
        
        if c==0:
            c=1
            time.sleep(20)
        
        for key in graph:
            deadarr[key]=0
        del deadarr[sys.argv[1]]
        #print "dead",deadarr
        time.sleep(3)

        #print "dead after sleep",deadarr
        for key in deadarr:
            if deadarr[key] == 0:
                tmp2.append(str(key))
                print "node "+str(key)+"is dead.removing "
                del graph[key]
                
        # at any instance the global graph will only contain neighbors that also exist as keys.
        #print "jugaar"
        #print graph
        for key in graph:
            tmp3 = graph[key]#for checking
            #tmp4 = graph[key]#for deleting.this tmp is saved back to the graph
            z = tmp3.keys()
            for y in z:
                if y not in graph.keys():
                    #print "deleting key",y
                    del tmp3[y]
                for e in range(len(Table)):
                    if key in Table[e][0]:#if key in graph is in list of neighbors
                        #print "found in list of neighbors",key
                        #and it also doesn't exist in my node

                        if key not in graph[sys.argv[1]].keys():
                            #add it to my dict in graph
                            #find distance
                            q=key
                            for x in range(len(Table)):
                                if q == Table[0]:
                                    break
                            tmp10=graph[sys.argv[1]]
                            tmp10[key]=Table[x][1]
                            #print "adding node",tmp10
                            graph[sys.argv[1]]=tmp10
            graph[key]=tmp3

        #vini,vedi,vini
        for x in tmp2:
            if x in deadarr:
                del deadarr[x]
            for k in graph:
                        tmp = graph[k]
                        if x in tmp:
                            del tmp[x]
                        graph[k]=tmp
        #print graph
        for key in graph:#mere naam k ilawa saray nodes
            if sys.argv[1] != key:
                pth,Dist = shortestPath(graph,sys.argv[1],key)
                print "shortest path from "+sys.argv[1]+" to "+key+""
                print pth
                print "Distance:",Dist[key]
                print "     -     "
        print "DIJKSTRA *********"
        time.sleep(30)
        
    # convert the graph you made to graph object and send it to dijkstra func as a parameter

   

main()

    