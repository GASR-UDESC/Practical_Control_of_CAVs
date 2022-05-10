#!/usr/bin/env python3

# Import the necessary libraries

import time
import paho.mqtt.client as mqtt
from pythonds.graphs import PriorityQueue, Graph
from ev3dev2.motor import MoveSteering, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import ColorSensor 

from random import choice

# Create the sensors, motors and buttons objects
steering_drive = MoveSteering(OUTPUT_A, OUTPUT_B)

color_sensor_in1 = ColorSensor(INPUT_1)

# Classe do robô
class commands():

    def __init__(self,initWay,initState,aut,eventEast,eventWest,eventNorth,eventSouth,allStates):
        self.currentWay = initWay
        self.currentState = initState
        self.aut = aut
        self.allStates = allStates
        self.disabledEvents = set()
        self.disabledStates = set()
        self.off=False

        self.east=eventEast#['a|b','b|c','d|e','e|f']
        self.west=eventWest#['b|a','c|b','e|d','f|e']
        self.north=eventNorth#['d|a','e|b','f|c']
        self.south=eventSouth#['a|d','b|e','c|f']

    #Faz o robô parar.
    def steering_driveOff(self):
        if not self.off:
            self.off=True
            steering_drive.off()

    #Faz o robô seguir reto.
    def straight(self):
        global memTime2,stablishTime
        steering_drive.on_for_seconds(steering=60,speed=15,seconds=waitTime)
        memTime2=time.time()
        stablishTime=4.5
    
    #Faz o robô retorna.
    def behind(self):
        global memTime2,stablishTime
        steering_drive.on_for_degrees(steering=100,speed=15,degrees=390)
        memTime2=time.time()
        stablishTime=5.5
    
    #Faz o robô seguir para a direita.
    def right(self):
        global memTime2,stablishTime
        steering_drive.on_for_degrees(steering=80,speed=15,degrees=270)#steering=80,speed=15,degrees=270
        memTime2=time.time()
        stablishTime=4.5
    
    #Faz o robô seguir para a esquerda.
    def left(self):
        global memTime2,stablishTime
        steering_drive.on_for_degrees(steering=-80,speed=15,degrees=220)#steering=-70,speed=15,degrees=270
        memTime2=time.time()
        stablishTime=4.5

    #Verifica qual estado deve ser desabilitado de acordo com o evento inserido e desabilita os eventos relacionados estado inserido
    def disableAndEnableEvents(self,pastState,futureState):
        #Habilita os eventos que levam para 'state'
        for i in self.aut.values():
            for j,k in i.items():
                if k == pastState:
                    self.disabledEvents.discard(j)
        #Retorna para 'self.disabledEvents' todos os eventos que levam para 'futureState'
        for i in self.aut.values():
            for j,k in i.items():
                if k == futureState:
                    self.disabledEvents.add(j)
        self.disabledStates.discard(pastState)
        self.disabledStates.add(futureState)

    #Atualiza self.currentState para o próximo estado, dependendo do evento selecionado
    def updateState(self,event):
        self.currentState=self.aut[self.currentState][event]
    
    #Define e chama para qual lado o robo deve seguir straight(), behind(), right() ou left().
    def goWay(self,way):
        if way == 'east':
            if self.currentWay == 'east':
                self.straight()
            elif self.currentWay == 'west':
                self.behind()
            elif self.currentWay == 'south':
                self.left()
            elif self.currentWay == 'north':
                self.right()

        elif way == 'west':
            if self.currentWay == 'east':
                self.behind()
            elif self.currentWay == 'west':
                self.straight()
            elif self.currentWay == 'south':
                self.right()
            elif self.currentWay == 'north':
                self.left()

        elif way == 'south':
            if self.currentWay == 'east':
                self.right()
            elif self.currentWay == 'west':
                self.left()
            elif self.currentWay == 'south':
                self.straight()
            elif self.currentWay == 'north':
                self.behind()

        elif way == 'north':
            if self.currentWay == 'east':
                self.left()
            elif self.currentWay == 'west':
                self.right()
            elif self.currentWay == 'south':
                self.behind()
            elif self.currentWay == 'north':
                self.straight()

        self.currentWay=way
    
    #Chama a função goWay() para que esta defina qual lado o robo deve seguir. Também chama a função updateState() para atualizar o currentState.
    def callBack(self,event):
        global auxVal,memTime3
        if event in self.east:
            self.goWay('east')
        elif event in self.west:
            self.goWay('west')
        elif event in self.south:
            self.goWay('south')
        elif event in self.north:
            self.goWay('north')
        self.updateState(event)
        self.off=False
        auxVal+=1
        memTime3=time.time()


# Atualiza o grafo adicionando ou removendo vertices e arcos
def setGraphFromAut():
    graph=Graph()
    for i in aut.keys():
        for j in aut[i].values():
            if i not in EV3.disabledStates and j not in EV3.disabledStates:
                graph.addEdge(i,j,1)
    return graph

#Realiza o calculo da trajetória ótima do vértice "start" até o vértice "end"
def dijkstra(aGraph,start,end):
    pq = PriorityQueue()
    start.setDistance(0)
    pq.buildHeap([(v.getDistance(),v) for v in aGraph])
    while not pq.isEmpty():
        currentVert = pq.delMin()
        for nextVert in currentVert.getConnections():
            newDist = currentVert.getDistance() \
                    + currentVert.getWeight(nextVert)
            if newDist < nextVert.getDistance():
                nextVert.setDistance( newDist )
                nextVert.setPred(currentVert)
                pq.decreaseKey(nextVert,newDist)
        if currentVert.getId() == end.getId():
            return currentVert

#Retorna uma lista com a sequência de eventos que deve ocorrer a partir do objeto bestWay
def getEvents(bestWay):
    currentVert=bestWay
    states=[currentVert.getId()]
    for i in range(bestWay.getDistance()):
        currentVert=currentVert.getPred()
        try:
            states.insert(0,currentVert.getId())
        except AttributeError:
            states=False
            break
    events=list()
    if states:
        for i in range(len(states)-1):
            j=states[i]
            for k in aut[j].keys():
                if aut[j][k] == states[i+1]:
                    events.append(k)
    return events

#Chama as funções necessárias para realizar o cálculo de trajetória até "destination", a partir de EV3.currentState. 
#E retorna a lista de eventos que deve ocorrer para tal objetivo.
def goTo(destination):
    global auxVal,events
    events=list()
    auxVal=0
    graph=setGraphFromAut()
    if destination in graph.getVertices():
        bestWay=dijkstra(graph,graph.getVertex(EV3.currentState),graph.getVertex(destination))
        return getEvents(bestWay)
    return list()    

#startInputs
myName='3'
initWay='east'
initState='M1'
aut={'A1': {'a1|b1': 'B1', 'a1|g1': 'G1'}, 'B1': {'b1|a1': 'A1', 'b1|c1': 'C1', 'b1|h1': 'H1'}, 'C1': {'c1|b1': 'B1', 'c1|d1': 'D1', 'c1|i1': 'I1'}, 'D1': {'d1|e1': 'E1', 'd1|c1': 'C1', 'd1|j1': 'J1'}, 'E1': {'e1|f1': 'F1', 'e1|d1': 'D1', 'e1|k1': 'K1'}, 'F1': {'f1|e1': 'E1', 'f1|l1': 'L1'}, 'G1': {'g1|h1': 'H1', 'g1|a1': 'A1', 'g1|m1': 'M1'}, 'H1': {'h1|i1': 'I1', 'h1|g1': 'G1', 'h1|b1': 'B1', 'h1|n1': 'N1'}, 'I1': {'i1|j1': 'J1', 'i1|h1': 'H1', 'i1|c1': 'C1', 'i1|o1': 'O1'}, 'J1': {'j1|k1': 'K1', 'j1|i1': 'I1', 'j1|d1': 'D1', 'j1|p1': 'P1'}, 'K1': {'k1|l1': 'L1', 'k1|j1': 'J1', 'k1|e1': 'E1', 'k1|q1': 'Q1'}, 'L1': {'l1|k1': 'K1', 'l1|f1': 'F1', 'l1|r1': 'R1'}, 'M1': {'m1|n1': 'N1', 'm1|g1': 'G1', 'm1|s1': 'S1'}, 'N1': {'n1|o1': 'O1', 'n1|m1': 'M1', 'n1|h1': 'H1', 'n1|t1': 'T1'}, 'O1': {'o1|p1': 'P1', 'o1|n1': 'N1', 'o1|i1': 'I1', 'o1|u1': 'U1'}, 'P1': {'p1|q1': 'Q1', 'p1|o1': 'O1', 'p1|j1': 'J1', 'p1|v1': 'V1'}, 'Q1': {'q1|r1': 'R1', 'q1|p1': 'P1', 'q1|k1': 'K1', 'q1|w1': 'W1'}, 'R1': {'r1|q1': 'Q1', 'r1|l1': 'L1', 'r1|x1': 'X1'}, 'S1': {'s1|t1': 'T1', 's1|m1': 'M1', 's1|y1': 'Y1'}, 'T1': {'t1|u1': 'U1', 't1|s1': 'S1', 't1|n1': 'N1', 't1|z1': 'Z1'}, 'U1': {'u1|v1': 'V1', 'u1|t1': 'T1', 'u1|o1': 'O1', 'u1|a2': 'A2'}, 'V1': {'v1|w1': 'W1', 'v1|u1': 'U1', 'v1|p1': 'P1', 'v1|b2': 'B2'}, 'W1': {'w1|x1': 'X1', 'w1|v1': 'V1', 'w1|q1': 'Q1', 'w1|c2': 'C2'}, 'X1': {'x1|w1': 'W1', 'x1|r1': 'R1', 'x1|d2': 'D2'}, 'Y1': {'y1|z1': 'Z1', 'y1|s1': 'S1'}, 'Z1': {'z1|a2': 'A2', 'z1|y1': 'Y1', 'z1|t1': 'T1'}, 'A2': {'a2|b2': 'B2', 'a2|z1': 'Z1', 'a2|u1': 'U1'}, 'B2': {'b2|a2': 'A2', 'b2|c2': 'C2', 'b2|v1': 'V1'}, 'C2': {'c2|b2': 'B2', 'c2|d2': 'D2', 'c2|w1': 'W1'}, 'D2': {'d2|c2': 'C2', 'd2|x1': 'X1'}}
eventEast={'c1|d1', 'q1|r1', 'e1|f1', 't1|u1', 'a2|b2', 'w1|x1', 'a1|b1', 'm1|n1', 'v1|w1', 'j1|k1', 'u1|v1', 'o1|p1', 'b1|c1', 'p1|q1', 's1|t1', 'b2|c2', 'y1|z1', 'z1|a2', 'g1|h1', 'c2|d2', 'd1|e1', 'n1|o1', 'h1|i1', 'i1|j1', 'k1|l1'}
eventWest={'c1|b1', 'h1|g1', 'd1|c1', 'w1|v1', 'a2|z1', 'p1|o1', 'j1|i1', 'e1|d1', 'b1|a1', 't1|s1', 'v1|u1', 'l1|k1', 'r1|q1', 'i1|h1', 'f1|e1', 'x1|w1', 'n1|m1', 'b2|a2', 'd2|c2', 'u1|t1', 'c2|b2', 'o1|n1', 'k1|j1', 'q1|p1', 'z1|y1'}
eventNorth={'z1|t1', 'r1|l1', 'j1|d1', 'a2|u1', 'd2|x1', 'v1|p1', 'b2|v1', 'k1|e1', 'p1|j1', 'x1|r1', 'o1|i1', 'h1|b1', 's1|m1', 'u1|o1', 'i1|c1', 'l1|f1', 'w1|q1', 'n1|h1', 'c2|w1', 'q1|k1', 't1|n1', 'y1|s1', 'g1|a1', 'm1|g1'}
eventSouth={'q1|w1', 'j1|p1', 'u1|a2', 'n1|t1', 'a1|g1', 'x1|d2', 'd1|j1', 's1|y1', 'e1|k1', 'g1|m1', 'i1|o1', 'k1|q1', 'c1|i1', 'h1|n1', 'o1|u1', 'w1|c2', 'l1|r1', 'r1|x1', 'v1|b2', 'p1|v1', 'b1|h1', 'f1|l1', 'm1|s1', 't1|z1'}
allStates={'Q1', 'E1', 'T1', 'N1', 'A2', 'M1', 'H1', 'F1', 'P1', 'W1', 'C2', 'R1', 'C1', 'K1', 'D2', 'A1', 'I1', 'Z1', 'U1', 'B1', 'D1', 'G1', 'V1', 'J1', 'X1', 'Y1', 'O1', 'B2', 'S1', 'L1'}
brokerIP='192.168.0.100'

#MQTT
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Separa "newMsg" em "beforeUnderscore" e "afterUnderscore" se beforeUnderscore é igual à myName ou se beforeUnderscore é um etado válido e afterUnderscore também é.
def separateMsg(newMsg,myName):
    try:
        beforeUnderscore=newMsg[:newMsg.index('_')]
        afterUnderscore=newMsg[newMsg.index('_')+1:]
        if (beforeUnderscore in EV3.allStates or beforeUnderscore == '') and (afterUnderscore in EV3.allStates or afterUnderscore == '') or beforeUnderscore == myName:
            return beforeUnderscore,afterUnderscore
        return False,False
    except ValueError:
        return False,False

def on_connect(client, userdata, flags, rc):
    client.subscribe('topic/EV3')
    client.publish('topic/EV3',(myName+' connected'))

def on_message(client, userdata, msg):
    global sendMsg,run,stop,events,myName,destination,rand,memTime3
    newMsg=msg.payload.decode()
    #print(newMsg)
    beforeUnderscore,afterUnderscore=separateMsg(newMsg,myName)
    if newMsg == 'run':
        memTime3=time.time()
        run=True
    elif newMsg == 'Random':
        memTime3=time.time()
        rand=0
        run=True
        destination=choice(tuple(EV3.allStates-EV3.disabledStates))
        sendMsg=myName+' going to '+destination
        client.publish('topic/EV3',(myName+' going to '+destination))
        events=goTo(destination) # Calcula a trajetoria a partir da mensagem recebida
    elif newMsg == 'stop':
        stop=True
    elif beforeUnderscore == myName:
        memTime3=time.time()
        destination=afterUnderscore
        events=goTo(destination) # Calcula a trajetoria a partir da mensagem recebida
    elif newMsg != sendMsg and beforeUnderscore != False and afterUnderscore != EV3.currentState:
        EV3.disableAndEnableEvents(pastState=beforeUnderscore,futureState=afterUnderscore)#Desabilita e habilita eventos

client = mqtt.Client()
client.connect(brokerIP,1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_start()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

memTime1=time.time()
memTime2=time.time()
memTime3=time.time()
waitTime=0.2
stablishTime=0
run=False
stop=False
events=list()
auxVal=0
sendMsg=''
destination=''
rand=0

EV3=commands(initWay=initWay,initState=initState,aut=aut,eventEast=eventEast,eventWest=eventWest,eventNorth=eventNorth,eventSouth=eventSouth,allStates=allStates)

while not stop: # forever
    if run:
        color=color_sensor_in1.color
        currenTime=time.time()
        
        if color != 6: #Black
            steering_drive.on(steering=30,speed=15) #Vira para direita
            memTime1=time.time()
            EV3.off=False

        else: #White
            if (currenTime-waitTime)<memTime1 or (currenTime-memTime2)<stablishTime:
                steering_drive.on(steering=-50,speed=15) #Vira para esquerda
            elif auxVal<len(events) and events[auxVal] not in EV3.disabledEvents:
                    sendMsg=EV3.currentState+'_'+aut[EV3.currentState][events[auxVal]]
                    client.publish('topic/EV3', sendMsg)
                    EV3.callBack(events[auxVal])
            elif EV3.currentState != destination and (currenTime-15)<memTime3: #Se não está mais que 15 segs sem ir a um novo estado
                EV3.steering_driveOff()
                events=goTo(destination)
            elif rand>2:
                rand+=1
                destination=choice(tuple(EV3.allStates-EV3.disabledStates))
                sendMsg=myName+' going to '+destination
                client.publish('topic/EV3',(myName+' going to '+destination))
                events=goTo(destination) # Calcula a trajetoria a partir da mensagem recebida
            else:
                EV3.steering_driveOff()
    time.sleep(0.02)

EV3.steering_driveOff()
client.disconnect()