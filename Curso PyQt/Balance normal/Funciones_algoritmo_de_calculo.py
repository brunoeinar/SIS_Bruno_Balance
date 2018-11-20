# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 08:43:24 2018

@author: Bruno E. Chávez
"""
from sympy import *
class Stream(object):
    def __init__(self,name):
        self.name=name
        self.edit=True
        self.critic=False
        self.limits=("None","None")
        self.delta=""
        self.fixed=False
        
    def Flujo(self,Flujo):
        self.Flujo=Flujo
    def Ducto(self,Ducto):
        self.Ducto=Ducto
    def Zona(self,Zona):
        self.Zona=Zona
    def Tipo(self,Tipo):
        self.Tipo=Tipo
    def Pos(self,Pos):
        self.Pos=Pos
    def editable(self):
        return self.edit
    def is_critic(self):
        return self.critic
    def get_limits(self):
        return self.limits
    def get_delta(self):
        return self.delta
    def is_fixed(self):
        return self.fixed
class Spliter(object):
    def __init__(self,name):
        self.name=name
    def entradas(self,entradas):
        self.entradas=entradas
    def salidas(self,salidas):
        self.salidas=salidas
    def status(self,status):
        self.status=status
    def Pos(self,Pos):
        self.Pos=Pos
def node(streams_dic,spliter,tol):
   ''' 
       streams_dic -> diccionario de todas las corrientes declaradas
       spliter-> divisor a resolver. Divisor type-->>object. El objeto contiene le siguiente información:
                                                             Nombre, entradas y salidas.
       inlets -> lista de entradas en forma "["x","100","x",...,"n"]"
       outlets -> Lista de salidas en fomra "["x","200","x",...,"n"]"
       valores de return ->'-100->Inconsitence error,'-1'->G!=0,'0'-> Resuelto primera iteración,'1'->Resuelto,
                           '3'-> Error en el cálculo de iteración
       '''
   inlets=[]
   outlets=[]
       
   for i in spliter.entradas:
       try:
           inlets.append(streams_dic[i].Flujo)
       except:
           return
   for i in spliter.salidas:
       try:
           outlets.append(streams_dic[i].Flujo)
       except:
           return
   I=0
   for i in inlets:   #Cuenta las incógnitas
       if i=="x":
           I+=1
   for i in outlets:
       if i=="x":
           I+=1
   G=1-I
   if G==0:
       x=Symbol("x")
       ec=""
       for i in range(0,len(inlets)):
           if i==len(inlets)-1:
                   ec+=str(inlets[i])
           else:
                   ec+=str(inlets[i])+"+"
       for i in outlets:
               ec+="-"+str(i)
       sol=solve(ec,x)
       ans=""
       for i in spliter.entradas:
            if streams_dic[i].Flujo=="x":
#                    if sol[0]<0:
#                        ans="Entradas"
#                    else:
                    streams_dic[i].Flujo=sol[0]
                    streams_dic[i].edit=False
       for i in spliter.salidas:
            if streams_dic[i].Flujo=="x":
#                    if sol[0]<0:
#                        ans="Salidas"
#                    else:
                    streams_dic[i].Flujo=sol[0]
                    streams_dic[i].edit=False
                    
       try:
           if ans=="":
               spliter.status("Solved")
               return[0,"Solved",""]
           if ans=="Salidas" or ans=="Entradas":
               spliter.status("Unsolved")
               return [spliter.name,"Confluence point",ans]
       except:
           if ans=="":
               spliter.status="Solved"    
               return[0,"Solved",""]
           if ans=="Salidas" or ans=="Entradas":
               spliter.status="Unsolved"
               return [spliter.name,"Confluence point",ans]
   if G==1:
       entradas=0
       salidas=0
       for i in inlets:
           entradas+=i
       for i in outlets:
           salidas+=i
       if entradas<0:
           entradas*=-1
       if salidas<0:
           salidas*=-1
       if abs(entradas-salidas)>tol:
           spliter.status="Error"
           return[-100,"Error",""]
       try:
           spliter.status("Solved")
           return [1,"Solved",""]
       except:
           spliter.status="Solved"
           return [1,"Solved",""]
   if G<0:
       try:
           spliter.status("Unsolved")
           return [-1,"Unsolved",G]
       except:
           spliter.status="Unsolved"
           return [-1,"Unsolved",G]
       