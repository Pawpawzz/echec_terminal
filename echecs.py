class Plateau:
    posit={i for i in range(11,89)}^{19,20,29,30,39,40,49,50,59,60,69,70,79,80}
    def __init__(self,defaut=None):
        self.coups = 0
        self.table=[[None]*8 for _ in range(8)]
        if defaut==None or type(defaut[0][0])==int:
            self.listeblancs=[11+10*i for i in range(8)]+[12+10*i for i in range(8)]
            self.listenoirs=[18+10*i for i in range(8)]+[17+10*i for i in range(8)]
            self.table[0][0],self.table[0][7],self.table[7][0],self.table[7][7]=Tour('b'),Tour('b'),Tour('n'),Tour('n')
            self.table[0][1],self.table[0][6],self.table[7][1],self.table[7][6]=Cav('b'),Cav('b'),Cav('n'),Cav('n')
            self.table[0][2],self.table[0][5],self.table[7][2],self.table[7][5]=Fou('b'),Fou('b'),Fou('n'),Fou('n')
            self.table[0][3],self.table[7][3]=Dame('b'),Dame('n')
            self.table[0][4],self.table[7][4]=Roi('b'),Roi('n')
            for j in range(8):
                self.table[1][j],self.table[6][j]=Pion('b'),Pion('n')
            if defaut!=None:
                couleur1 = 'b'
                couleur2 = 'n'
                for positions in defaut:
                    self.deplacement(positions, couleur1)
                    couleur1, couleur2 = couleur2, couleur1
        elif type(defaut[0][0])==str:
            dicpieces={'p':Pion,'t':Tour,'c':Cav,'f':Fou,'d':Dame,'r':Roi}
            self.listeblancs=[]
            self.listenoirs=[]
            for positions in defaut:
                if positions[0][0] not in dicpieces:
                    raise NameError('Cette pièce n''existe pas.')
                if positions[0][1] not in {'b','n'}:
                     raise NameError('Cette couleur n''existe pas.')
                if positions[1] in self.listeblancs or positions[1] in self.listenoirs:
                    raise NameError('Il y a 2 pièces à la même position.')
                self.table[positions[1]%10-1][positions[1]//10-1]=dicpieces[positions[0][0]](positions[0][1])
                if positions[0][1]=='b':
                    self.listeblancs.append(positions[1])
                else:
                    self.listenoirs.append(positions[1])

    def trajectoire(self,depl):
        sens=(depl[1]-depl[0])//abs(depl[1]-depl[0])
        if abs(depl[1]-depl[0]) in {8,12,19,21}: #cavalier:pas de pb de trajectoire
            return set()
        if (depl[1]-depl[0])%11==0:
            increment=11
        if (depl[1]-depl[0])%9==0:
            increment=9
        if (depl[1]-depl[0])%10==0:
            increment=10
        if -8<=depl[1]-depl[0]<=8:
            increment=1
        traj=set()
        pos=depl[0]+increment*sens
        while pos!=depl[1]:
            traj=traj|{pos}
            pos+=increment*sens
        return traj

    def __getitem__(self,pos):
        return self.table[pos%10-1][pos//10-1]

    def mouv(self, depl, coul_joueur):
        if self[depl[0]].nom[0] == 'R' and self[depl[0]].bouge == False:
            try:
                self.roque(depl, coul_joueur)
                return
            except NameError:
                pass
        if self[depl[0]].nom[0] == 'i':
            if self.enpassant(depl, coul_joueur):
                return
        self.deplacement(depl, coul_joueur)
        if self[depl[1]].nom[0] == 'i':
            self.promo(depl[1], coul_joueur)
        self.coups += 1

    def deplacement(self,depl,coul_joueur):
        if depl[0] == depl[1]:
            raise NameError('déplacement sur place')
        if depl[0] not in set(self.listeblancs)|set(self.listenoirs):
            raise NameError('pas de piece à cet endroit')
        prise=False
        couleur=self[depl[0]].couleur
        if couleur!=coul_joueur:
            raise NameError('Ce n''est pas votre pièce')
        if couleur=='b':
            listejoueur=self.listeblancs
            listeadv=self.listenoirs
        else:
            listejoueur=self.listenoirs
            listeadv=self.listeblancs
        if self.trajectoire(depl)&(set(self.listenoirs)|set(self.listeblancs))!=set():
            raise NameError('ya du monde')
        if depl[1] in listejoueur:
            raise NameError('déjà sur place')
        if depl[1] in listeadv:
            prise=True
                    
        if depl[1] not in self[depl[0]].deplvalide(depl[0],prise):
            raise NameError('déplacement interdit')
        pprise = self[depl[1]]
        self.table[depl[1]%10-1][depl[1]//10-1]=self.table[depl[0]%10-1][depl[0]//10-1]
        self.table[depl[0]%10-1][depl[0]//10-1]=None
        listejoueur.remove(depl[0])
        listejoueur.append(depl[1])
        if prise==True:
            listeadv.remove(depl[1])
        if self.echec(coul_joueur) == True:
                self.retourenarriere(depl,coul_joueur,prise,pprise)
                raise NameError('déplacement interdit (echec)')
            
        self[depl[1]].bouge = True

    def enpassant(self, depl, couleur):
        if abs(depl[1] - depl[0]) == 2:
            self[depl[0]].deuxcases = self.coups
            return False
        if depl[1] not in self[depl[0]].deplvalide(depl[0], True):
            return False
        if couleur=='b':
            listejoueur=self.listeblancs
            listeadv=self.listenoirs
            if self[depl[1]-1].nom == 'i' + 'n':
                if self[depl[1]-1].deuxcases == self.coups - 1:
                    self.table[depl[1]%10-1][depl[1]//10-1]=self.table[depl[0]%10-1][depl[0]//10-1]
                    self.table[depl[0]%10-1][depl[0]//10-1]=None
                    self.table[(depl[1]-1)%10-1][(depl[1]-1)//10-1] = None
                    listejoueur.remove(depl[0])
                    listejoueur.append(depl[1])
                    listeadv.remove(depl[1]-1)
                    return True
        return False
        if couleur == 'n':
            listejoueur=self.listenoirs
            listeadv=self.listeblancs
            if self[depl[1]+1].nom == 'i' + 'b':
                if self[depl[1]+1].deuxcases == self.coups - 1:
                    self.table[depl[1]%10-1][depl[1]//10-1]=self.table[depl[0]%10-1][depl[0]//10-1]
                    self.table[depl[0]%10-1][depl[0]//10-1]=None
                    self.table[(depl[1]+1)%10-1][(depl[1]+1)//10-1] = None
                    listejoueur.remove(depl[0])
                    listejoueur.append(depl[1])
                    listeadv.remove(depl[1]+1)
                    return True
        return False
        

    def retourenarriere(self,depl,coul_joueur,prise=False, pprise=None):
        if depl[0] == depl[1]:
            return None
        if coul_joueur=='b':
            listejoueur=self.listeblancs
            listeadv=self.listenoirs
        else:
            listejoueur=self.listenoirs
            listeadv=self.listeblancs
        self.table[depl[0]%10-1][depl[0]//10-1]=self.table[depl[1]%10-1][depl[1]//10-1]
        self.table[depl[1]%10-1][depl[1]//10-1]=pprise
        listejoueur.append(depl[0])
        listejoueur.remove(depl[1])
        if prise==True:
            listeadv.append(depl[1])

    def echec(self, couleur):
        pos = 0
        if couleur == 'n':
            while self[self.listenoirs[pos]].nom != 'Rn':
                pos += 1
            roi_pos = self.listenoirs[pos]
            roi = self[roi_pos]
            for element in self.listeblancs:
                try:
                    self.deplacement((element, roi_pos),'b')
                except NameError:
                    pass
                else:
                    self.retourenarriere((element, roi_pos),'b',True,roi)
                    return True
        else:
            while self[self.listeblancs[pos]].nom != 'Rb':
                pos += 1
            roi_pos = self.listeblancs[pos]
            roi = self[roi_pos]
            for element in self.listenoirs:
                try:
                    self.deplacement((element, roi_pos),'n')
                except NameError:
                    pass
                else:
                    self.retourenarriere((element, roi_pos),'n',True,roi)
                    return True
        return False

    def mat(self, couleur):
        if couleur == 'b':
            if self.echec('n'):
                temp = self.listenoirs[:]
                for pos_piece in temp:
                    for depl_pssble in (self[pos_piece].deplvalide(pos_piece))|(self[pos_piece].deplvalide(pos_piece, True)):
                        arrivee = self.table[depl_pssble%10-1][depl_pssble//10-1]
                        if depl_pssble in self.listeblancs:
                            prise = True
                        else:
                            prise = False
                        try:
                            self.deplacement((pos_piece,depl_pssble), 'n')
                        except NameError:
                            pass
                        else:
                            self.retourenarriere((pos_piece,depl_pssble), 'n', prise, arrivee)
                            return False
                return True
        if couleur == 'n':
            if self.echec('b'):
                temp = self.listeblancs[:]
                for pos_piece in temp:
                    for depl_pssble in (self[pos_piece].deplvalide(pos_piece))|(self[pos_piece].deplvalide(pos_piece, True)):
                        arrivee = self.table[depl_pssble%10-1][depl_pssble//10-1]
                        if depl_pssble in self.listenoirs:
                            prise = True
                        else:
                            prise = False
                        try:
                            self.deplacement((pos_piece,depl_pssble), 'b')
                        except NameError:
                            pass
                        else:
                            self.retourenarriere((pos_piece,depl_pssble), 'b', prise, arrivee)
                            return False
                return True
        return False

    def pat(self, couleur):
        if couleur == 'b':
            if not self.echec('n'):
                temp = self.listenoirs[:]
                for pos_piece in temp:
                    for depl_pssble in (self[pos_piece].deplvalide(pos_piece))|(self[pos_piece].deplvalide(pos_piece, True)):
                        arrivee = self.table[depl_pssble%10-1][depl_pssble//10-1]
                        if depl_pssble in self.listeblancs:
                            prise = True
                        else:
                            prise = False
                        try:
                            self.deplacement((pos_piece,depl_pssble), 'n')
                        except NameError:
                            pass
                        else:
                            self.retourenarriere((pos_piece,depl_pssble), 'n', prise, arrivee)
                            return False
                return True
        if couleur == 'n':
            if not self.echec('b'):
                temp = self.listeblancs[:]
                for pos_piece in temp:
                    for depl_pssble in (self[pos_piece].deplvalide(pos_piece))|(self[pos_piece].deplvalide(pos_piece, True)):
                        arrivee = self.table[depl_pssble%10-1][depl_pssble//10-1]
                        if depl_pssble in self.listenoirs:
                            prise = True
                        else:
                            prise = False
                        try:
                            self.deplacement((pos_piece,depl_pssble), 'b')
                        except NameError:
                            pass
                        else:
                            self.retourenarriere((pos_piece,depl_pssble), 'b', prise, arrivee)
                            return False
                return True
    def roque(self, depl, couleur):
        if self.echec(couleur):
            raise NameError('roi en echec')
        if couleur=='b':
            listejoueur=self.listeblancs
        else:
            listejoueur=self.listenoirs
        if depl[1] in self[depl[0]].roque(depl[0]):

            if depl[0]<depl[1]: #petit roque
                #roi en echec? + déplacement du roi
                pos_roi = depl[0]
                for i in range(2):
                    try:
                        self.deplacement((pos_roi, pos_roi+10), couleur)
                    except NameError:
                        self.retourenarriere((depl[0],pos_roi), couleur)
                        raise NameError('roi en echec sur le trajet')
                    else:
                        pos_roi += 10

                #déplacement de la tour
                depl0 = depl[1] + 10
                depl1 = depl[1] - 10
                if self[depl[0]] != None and self[depl[0]].bouge == False:
                    self.table[depl1%10-1][depl1//10-1]=self.table[depl0%10-1][depl0//10-1]
                    self.table[depl0%10-1][depl0//10-1]=None
                    listejoueur.remove(depl0)
                    listejoueur.append(depl1)
                else:
                    raise NameError('La tour a bougé')

            if depl[1]<depl[0]: #grand roque

                #les cases sont vides?
                pos = depl[0]
                while pos > depl[1]-10:
                    pos -= 10
                    if self[pos] != None:
                        raise NameError('ya du monde')

                #roi en echec? + déplacement du roi
                pos_roi = depl[0]
                for i in range(2):
                    try:
                        self.deplacement((pos_roi, pos_roi-10), couleur)
                    except NameError:
                        self.retourenarriere((depl[0],pos_roi), couleur)
                        raise NameError('roi en echec sur le trajet')
                    else:
                        pos_roi -= 10

                #déplacement de la tour
                depl0 = depl[1] - 20
                depl1 = depl[1] + 10
                if self[depl[0]] != None and self[depl[0]].bouge == False:
                    self.table[depl1%10-1][depl1//10-1]=self.table[depl0%10-1][depl0//10-1]
                    self.table[depl0%10-1][depl0//10-1]=None
                    listejoueur.remove(depl0)
                    listejoueur.append(depl1)
                else:
                    raise NameError('La tour a bougé')


    def promo(self, pos, couleur):
        fin = {0,7}
        if pos%10-1 in fin:
            piece = input('Rentrez la pièce par laquelle vous voulez remplacer le pion, en rentrant l''initiale de la piece, sans la couleur, en minuscule.')
            if piece == 'd':
                self.table[pos%10-1][pos//10-1] = Dame(couleur, True)
                return
            if piece == 't':
                self.table[pos%10-1][pos//10-1] = Tour(couleur, True)
                return
            if piece == 'c':
                self.table[pos%10-1][pos//10-1] = Cav(couleur, True)
                return
            if piece == 'f':
                self.table[pos%10-1][pos//10-1] = Fou(couleur, True)
                return
            if piece == 'r' or piece =='p':
                raise NameError('peut pas se transformer en roi ou en pion')

    def __repr__(self):
        res='      1    2    3    4    5    6    7    8   \n'
        res+='    ---- ---- ---- ---- ---- ---- ---- ---- \n'
        for i in range(8,0,-1):
            ligne=str(i)+'  '+'|'
            for j in range(8):
                if self.table[i-1][j] is None:
                    ligne+='    |'
                else:
                    ligne+=' '+self.table[i-1][j].nom+' |'
            ligne+='  '+str(i)+'\n'
            res+=ligne+'    ---- ---- ---- ---- ---- ---- ---- ---- \n'
        res+='      1    2    3    4    5    6    7    8   '


        return res


class Pion:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='i'+couleur
        self.bouge=bouge
        self.deuxcases = None

    def deplvalide(self,pos,prise=False):
        col=1
        if self.couleur=='n':
            col=-1
        if prise==False:
            if pos%10==2 or pos%10==7:
                return {pos+2*col,pos+1*col} & Plateau.posit
            return {pos+1*col}
        if prise==True:
            return {pos-9*col,pos+11*col} & Plateau.posit


    def __repr__(self):
        return 'i'+self.couleur


class Tour:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='T'+couleur
        self.bouge=bouge

    def deplvalide(self,pos,prise=False):
        return ({(pos//10)*10+i for i in range(1,9)}|{(pos%10)+10*i for i in range(1,9)}) & Plateau.posit

    def __repr__(self):
        return 'T'+self.couleur

    def roque(self, pos):
        if self.bouge == False:
            return {pos-20, pos+30} & Plateau.posit
        return {}

class Cav:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='C'+couleur
        self.bouge=bouge

    def deplvalide(self,pos,prise=False):
        return {pos-21,pos-19,pos-12,pos-8,pos+8,pos+12,pos+19,pos+21} & Plateau.posit

    def __repr__(self):
        return 'C'+self.couleur

class Fou:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='F'+couleur
        self.bouge=bouge

    def deplvalide(self,pos,prise=False):
        i=1
        res=set()
        while pos+11*i in Plateau.posit:
            res=res|{pos+11*i}
            i+=1
        i=1
        while pos-11*i in Plateau.posit:
            res=res|{pos-11*i}
            i+=1
        i=1
        while pos-9*i in Plateau.posit:
            res=res|{pos-9*i}
            i+=1
        i=1
        while pos+9*i in Plateau.posit:
            res=res|{pos+9*i}
            i+=1
        return res & Plateau.posit

    def __repr__(self):
        return 'F'+self.couleur


class Dame:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='D'+couleur
        self.bouge=bouge

    def deplvalide(self,pos,prise=False):
        res=set()
        i=1
        while pos+11*i in Plateau.posit:
            res=res|{pos+11*i}
            i+=1
        i=1
        while pos-11*i in Plateau.posit:
            res=res|{pos-11*i}
            i+=1
        i=1
        while pos-9*i in Plateau.posit:
            res=res|{pos-9*i}
            i+=1
        i=1
        while pos+9*i in Plateau.posit:
            res=res|{pos+9*i}
            i+=1
        return ({(pos//10)*10+i for i in range(1,9)}|{(pos%10)+10*i for i in range(1,9)}|res)&Plateau.posit

    def __repr__(self):
        return 'D'+self.couleur

class Roi:
    def __init__(self,couleur,bouge=False):
        self.couleur=couleur
        self.nom='R'+couleur
        self.bouge=bouge

    def deplvalide(self,pos,prise=False):
        return {pos-1,pos+1,pos-10,pos+10,pos-9,pos+9,pos-11,pos+11} & Plateau.posit

    def roque(self, pos):
        if self.bouge == False:
            return {pos-20,pos+20}
        return {}
    def __repr__(self):
        return 'R'+self.couleur

def partie():
    test=Plateau()
    while True:
        while True:
            try:
                print(test)
                coup=input('les blancs jouent, déplacement:')
                depl=(int(coup[1:3]),int(coup[4:6]))
                test.mouv(depl,'b')
                if test.mat('b') == True:
                    print(test)
                    return 'echec et mat, les blancs gagnent'
                if test.pat('b') == True:
                    print(test)
                    return 'pat, fin de partie'
                if test.echec('n') == True:
                    print('echec')
            except NameError:
                print('une erreur est survenue, recommencez')
            else:
                break
        while True:
            try:
                print(test)
                coup=input('les noirs jouent, déplacement:')
                depl=(int(coup[1:3]),int(coup[4:6]))
                test.mouv(depl,'n')
                if test.mat('n') == True:
                    print(test)
                    return 'echec et mat, les noirs gagnent'
                if test.pat('n') == True:
                    print(test)
                    return 'pat, fin de partie'
                if test.echec('b') == True:
                    print('echec')
            except:
                print('une erreur est survenue, recommencez')
            else:
                break

test = Plateau()
t = Plateau((("rb",51), ("tb",81), ("tb",11),("rn",58),("fn",16),('pb',77)))
t = Plateau((("rn",58),("rb",51),("pb",55),("pn",47)))
