import os
import io

# Recebe o arquivo .pro do destool e retorna o alfabeto em um dicionário.
# Exemplo de retorno: {'S1_on': {'controllable': False, 'observable': True, 'forcible': False}, 'S1_off': {'controllable': False, 'observable': True, 'forcible': False}}
def get_Alphabet(destool_file):
    with open(destool_file,'r') as reader: #Abre o arquivo para leitura apenas
        start_read = False #Variável auxiliar
        result = dict() #Inicia vetor para incluir os resultados obtidos
        for line in reader: #reader é o arquivo e line são as linhas de reader
            if '</Alphabet>' in line: # '</Alphabet>' é o indicador do final de escrita do automato dentro do arquivo .pro do destool
                break #Finaliza o for

            if start_read: #Linhas internas à '<Alphabet>' e '</Alphabet>'
                if ('<Controllable/>' in line) or ('<Observable value="false"/>' in line) or ('<Forcible/>' in line):
                    if '<Controllable/>' in line:
                        result[key]['controllable'] = True #Coloca em "controllable" True
                    if '<Observable value="false"/>' in line:
                        result[key]['observable'] = False #Coloca em "observable" False
                    if '<Forcible/>' in line:
                        result[key]['forcible'] = True #Coloca em "forcible" True

                elif not ('</State>' in line):
                    try:
                        start=line.index('"')+1 #Retorna para start o lugar do prieiro " encontrado na linha
                        end = line.index('"',start) #Retorna para start o lugar do primeiro " encontrado na linha começando a contagem em start até o final da linha 
                        key=line[start:end]
                        result[key]={'controllable':False,'observable':True,'forcible':False} #Coloca em result a string que está entre start e end e os valores padrões de "controllable", "observable" e "forcible"
                    except ValueError: #Caso não haja mais " em line.index para ser encontrada nessa linha
                        continue

            if '<Alphabet>' in line: #'<Alphabet>' marca o início do automato dentro do arquivo .pro do destool
                start_read = True #Inicia a leitura
    return result

# Recebe o arquivo .pro do destool e retorna as configurações de cada estado em um dicionário.
# Exemplo de retorno: {'1': {'1': {'initial': True, 'marked': True}}, '2': {'2': {'initial': False, 'marked': False}}, '3': {'3': {'initial': False, 'marked': False}}}
def get_StateSet(destool_file):
    with open(destool_file,'r') as reader: #Abre o arquivo para leitura apenas
        start_read = False #Variável auxiliar
        result = dict() #Inicia vetor para incluir os resultados obtidos
        for line in reader: #reader é o arquivo e line são as linhas de reader
            if '</StateSet>' in line: # '</StateSet>' é o indicador do final de escrita do automato dentro do arquivo .pro do destool
                break #Finaliza o for

            if start_read: #Linhas internas à '<StateSet>' e '</StateSet>'
                if ('<Initial/>' in line) or ('<Marked/>' in line):
                    if '<Initial/>' in line:
                        result[key1][key2]['initial'] = True #Coloca em "initial" True
                    if '<Marked/>' in line:
                        result[key1][key2]['marked'] = True #Coloca em "marked" True

                elif not ('</State>' in line):
                    i=0 #Variável auxiliar
                    key1=False
                    key2=False
                    while True: #Roda até break
                        try:
                            start=line.index('"',i)+1 #Retorna para start o lugar do prieiro " encontrado na linha começando a contagem em i até o final da linha +1
                            end = line.index('"',start) #Retorna para start o lugar do primeiro " encontrado na linha começando a contagem em start até o final da linha 
                            i = end+1 #Não há " que não foi utilizado antes de end, por isso, i não é sequencial nesse while
                        except ValueError: #Caso não haja mais " em line.index para ser encontrada nessa linha
                            break #Finaliza o while
                        if not key1:
                            key1=line[start:end]
                        else:
                            key2=line[start:end]
                            result[key1]={key2:{'initial':False,'marked':False}}#Coloca em result os valores padrões de "initial" e "marked"

            if '<StateSet>' in line: #'<StateSet>' marca o início do automato dentro do arquivo .pro do destool
                start_read = True #Inicia a leitura
    return result

# Recebe o arquivo .pro do destool e retorna a relação de transição em um dicionário.
# Se idx = False (padrão), a função retorna os estados com os nomes colocados no destool.
# Se idx = True, a função retorna os estados com os IDs utilizados pelo software destool.
# Exemplo de retorno (idx=False): {'A': {'a|b': 'B', 'a|d': 'D'}, 'B': {'b|a': 'A', 'b|c': 'C', 'b|e': 'E'}}
# Exemplo de retorno (idx=True): {'1': {'a|b': '2', 'a|d': '3'}, '2': {'b|a': '1', 'b|c': '4', 'b|e': '5'}}
def get_TransitionRelation(destool_file,idx=False):
    with open(destool_file,'r') as reader: #Abre o arquivo para leitura apenas
        start_read = False #Variável auxiliar
        result = dict() #Inicia para incluir os resultados obtidos
        for line in reader: #reader é o arquivo e line são as linhas de reader
            if '</TransitionRelation>' in line: # '</TransitionRelation>' é o indicador do final de escrita do automato dentro do arquivo .pro do destool
                break #Finaliza o for
            if start_read: #Linhas internas à '<TransitionRelation>' e '</TransitionRelation>'
                #s=dict() #Inicia para incluir os valores obtidos internos as aspas
                i=0 #Variável auxiliar
                key1=False
                key2=False
                while True: #Roda até break
                    try:
                        start=line.index('"',i)+1 #Retorna para start o lugar do prieiro " encontrado na linha começando a contagem em i até o final da linha +1
                        end = line.index('"',start) #Retorna para start o lugar do primeiro " encontrado na linha começando a contagem em start até o final da linha 
                        i = end+1 #Não há " que não foi utilizado antes de end, por isso, i não é sequencial nesse while
                    except ValueError: #Caso não haja mais " em line.index para ser encontrada nessa linha
                        break #Finaliza o while
                    if not key1:
                        key1=line[start:end]
                    elif not key2:
                        key2=line[start:end]
                    else:
                        if key1 in result.keys():#Se essa key ja existe
                            result[key1].update({key2:line[start:end]})
                        else:#Se a key ainda não existe
                            result[key1]={key2:line[start:end]}
            if '<TransitionRelation>' in line: #'<TransitionRelation>' marca o início do automato dentro do arquivo .pro do destool
                start_read = True #Inicia a leitura
    if not idx:
        stateSet=get_StateSet(destool_file)
        for i in result.keys():
            for j in result[i].keys():
                result[i][j]=next(iter(stateSet[result[i][j]].keys()))#Atualiza result[i][j] com o valor escrito no destool, não mais pelo ID.
        for i in stateSet.keys():
            try:
                result[next(iter(stateSet[i].keys()))]=result.pop(i)#Atualiza result.keys() com os valores escritos no destool, não mais pelo ID.
            except KeyError:
                continue
    return result

myName=input('\nDigite o nome ao qual este robô será reconhecido\n:')

inp=input('\nA pista está entre as pistas conhecidas? [S/N]\n:')
east={'e','E','east','East','l','L','leste','Leste'}
west={'w','W','west','West','o','O','oeste','Oeste'}
north={'n','N','north','North','norte','Norte'}
south={'s','S','south','South','sul','Sul'}
if inp in {'s','S','sim','Sim'}:
    print('\nA partir das opções a seguir digite o numero correspondente à pista:')
    print('[1] Pista 2x3\n[2] Pista 3x4\n[3] Pista 5x6')
    inp=input(':')
    if inp=='1': #Pista 2x3
        trackName='2x3.pro'
        eventEast={'a|b','b|c','d|e','e|f'}
        eventWest={'b|a','c|b','e|d','f|e'}
        eventNorth={'d|a','e|b','f|c'}
        eventSouth={'a|d','b|e','c|f'}
    elif inp=='2': #Pista 3x4
        trackName='3x4.pro'
        eventEast={'a|b','b|c','c|d','e|f','f|g','g|h','i|j','j|k','k|l'}
        eventWest={'b|a','c|b','d|c','f|e','g|f','h|g','j|i','k|j','l|k'}
        eventNorth={'e|a','i|e','f|b','j|f','g|c','k|g','h|d','l|h'}
        eventSouth={'a|e','e|i','b|f','f|j','c|g','g|k','d|h','h|l'}
    elif inp=='3': #Pista 5x6
        trackName='5x6.pro'
        eventEast= {'a1|b1','b1|c1','c1|d1','d1|e1','e1|f1',
                    'g1|h1','h1|i1','i1|j1','j1|k1','k1|l1',
                    'm1|n1','n1|o1','o1|p1','p1|q1','q1|r1',
                    's1|t1','t1|u1','u1|v1','v1|w1','w1|x1',
                    'y1|z1','z1|a2','a2|b2','b2|c2','c2|d2'}
        eventWest= {'b1|a1','c1|b1','d1|c1','e1|d1','f1|e1',
                    'h1|g1','i1|h1','j1|i1','k1|j1','l1|k1',
                    'n1|m1','o1|n1','p1|o1','q1|p1','r1|q1',
                    't1|s1','u1|t1','v1|u1','w1|v1','x1|w1',
                    'z1|y1','a2|z1','b2|a2','c2|b2','d2|c2'}
        eventNorth={'g1|a1','h1|b1','i1|c1','j1|d1','k1|e1','l1|f1',
                    'm1|g1','n1|h1','o1|i1','p1|j1','q1|k1','r1|l1',
                    's1|m1','t1|n1','u1|o1','v1|p1','w1|q1','x1|r1',
                    'y1|s1','z1|t1','a2|u1','b2|v1','c2|w1','d2|x1'}
        eventSouth={'a1|g1','b1|h1','c1|i1','d1|j1','e1|k1','f1|l1',
                    'g1|m1','h1|n1','i1|o1','j1|p1','k1|q1','l1|r1',
                    'm1|s1','n1|t1','o1|u1','p1|v1','q1|w1','r1|x1',
                    's1|y1','t1|z1','u1|a2','v1|b2','w1|c2','x1|d2'}
else:
    trackName=input('Digite o nome do arquivo .pro, incluindo o ".pro" ao final, referente à pista\n:')
    alphabet_trackName=get_Alphabet(trackName)
    print("Digite a direção do respectivo evento:")
    print("e = Leste (East)\nw = Oeste (West)\nn = Norte (North)\ns = Sul (South)")
    eventEast=set()
    eventWest=set()
    eventNorth=set()
    eventSouth=set()
    for i in alphabet_trackName.keys():
        while True:
            inp=input(i+' = ')
            if inp in east:
                eventEast.add(i)
                break
            elif inp in west:
                eventWest.add(i)
                break
            elif inp in north:
                eventNorth.add(i)
                break
            elif inp in south:
                eventSouth.add(i)
                break
            else:
                print('Este não é um comando valido, tente novamente...')

aut=get_TransitionRelation(trackName)
stateSet_trackName=get_StateSet(trackName)

#Retorna "allStates"
allStates=set()
for i in stateSet_trackName.values():
    allStates.add(next(iter(i.keys())))

#Pega o estado inicial
while True:
    inp=input('\nQual o estado inicial deste robô?\n:')
    if inp in allStates:
        initState=inp
        break
    else:
        print('Este não é um comando valido, tente novamente...')

#Pega a direção inicial
while True:
    print("\nDigite a direção inicial:")
    initWay=input("e = Leste (East)\nw = Oeste (West)\nn = Norte (North)\ns = Sul (South)\n:")
    if initWay in east:
        initWay='east'
        break
    elif initWay in west:
        initWay='west'
        break
    elif initWay in north:
        initWay='north'
        break
    elif initWay in south:
        initWay='south'
        break
    else:
        print('Este não é um comando valido, tente novamente...')

#Pega o IP do broker
brokerIP=input('\nDigite o endereço IP do broker\n:')

inputs=[
    "myName='",myName,"'\n",
    "initWay='",initWay,"'\n",
    "initState='",initState,"'\n",
    "aut=",str(aut),"\n",
    "eventEast=",str(eventEast),"\n",
    "eventWest=",str(eventWest),"\n",
    "eventNorth=",str(eventNorth),"\n",
    "eventSouth=",str(eventSouth),"\n",
    "allStates=",str(allStates),"\n",
    "brokerIP='",brokerIP,"'\n"]

def pythonToEV3(EV3PythonFile):
    try:
        os.mkdir('PtoEV3')
    except FileExistsError:
        None
    pathName=os.getcwd()+r'\PtoEV3'
    fileName=EV3PythonFile
    destiny_directory=os.path.join(pathName,fileName)

    with io.open(destiny_directory,'w',newline='\n') as writer: #Abre ou cria o arquivo para escrita apenas
        with open('goTo.py','r') as reader: #Abre o arquivo para leitura apenas
            for line in reader:
                writer.write(line)
                if '#startInputs' in line:
                    writer.writelines(inputs)

pythonToEV3('goTo_'+myName+'.py')