# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 08:25:01 2018

@author: Bruno E. Chávez
"""
import sys
import os
import platform
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qrc_resources
import random
from Funciones_algoritmo_de_calculo import *
import xlwings as xw
sys.setrecursionlimit(5000)

__version__="1.0.0"
#Variables globales
PageSize=(23000,20000)
streams={}
spliters={}
variables=[]
restricciones={}
critic=[]


flag=False #Flag para indicar si un elemento es de nueva creación o quiere ser modificado
PointSize=10


'''-----------------Graphic object y graphic View-----------------------'''

class graphic_object(QGraphicsPixmapItem):
    def __init__(self,parent=None):
        super(graphic_object,self).__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsMovable)    
    
    def mouseDoubleClickEvent(self,event):
        MainWindow.modify_item(form)
    
class TextItem(QGraphicsTextItem):
    def __init__(self,text,position,scene,font=QFont("Arial Black",PointSize)):
        super(TextItem,self).__init__(text)
        self.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsMovable)
        self.setFont(font)
        self.setPos(position)
        scene.clearSelection()
        scene.addItem(self)
        self.setSelected(True)
    
    def parentWidget(self):
        return self.scene().views()[0]
    
    def mouseDoubleClickEvent(self,event):
        dialog=TextItemDlg(self,self.parentWidget())
        dialog.exec_()
        
class GraphicsView(QGraphicsView):
   def __init__(self,parent=None):
       super(GraphicsView,self).__init__(parent)
       self.setDragMode(QGraphicsView.RubberBandDrag)
   def wheelEvent(self,event):
       factor=1.41**(-event.angleDelta().y()/240)
       self.scale(factor,factor)

#####################################################################################
        

'''--------------------------------------------------------------------------------'''
'''------------------------Dialogs-------------------------------------------------'''
class TextItemDlg(QDialog):
    def __init__(self,item=None,position=None,scene=None,parent=None):
        super(QDialog,self).__init__(parent)
        self.item=item
        self.position=position
        self.scene=scene
        self.editor=QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabChangesFocus(True)
        editorLabel=QLabel("&Text: ")
        editorLabel.setBuddy(self.editor)
        self.fontComboBox=QFontComboBox()
        self.fontComboBox.setCurrentFont(QFont("Times",PointSize))
        fontLabel=QLabel("&Font:")
        fontLabel.setBuddy(self.fontComboBox)
        self.fontSpinBox=QSpinBox()
        self.fontSpinBox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.fontSpinBox.setRange(6,280)
        self.fontSpinBox.setValue(PointSize)
        fontSizeLabel=QLabel("&Size:")
        fontSizeLabel.setBuddy(self.fontSpinBox)
        self.buttonBox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        if self.item is not None:
            self.editor.setPlainText(self.item.toPlainText())
            self.fontComboBox.setCurrentFont(self.item.font())
            self.fontSpinBox.setValue(self.item.font().pointSize())
        
        layout=QGridLayout()
        layout.addWidget(editorLabel,0,0)
        layout.addWidget(self.editor,1,0,1,6)
        layout.addWidget(fontLabel,2,0)
        layout.addWidget(self.fontComboBox,2,1,1,2)
        layout.addWidget(fontSizeLabel,2,3)
        layout.addWidget(self.fontSpinBox,2,4,1,2)
        layout.addWidget(self.buttonBox,3,0,1,6)
        self.setLayout(layout)
        
        '''Slots'''
        self.fontComboBox.currentFontChanged.connect(self.updateUi)
        self.fontSpinBox.valueChanged.connect(self.updateUi)
        self.editor.textChanged.connect(self.updateUi)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.setWindowTitle("Cuadro de Texto - %s" %("Add" if self.item is None else "Edit"))
        self.updateUi()
        
        '''Funciones de Text Dialog'''
        
    def updateUi(self):
        font=self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.editor.document().setDefaultFont(font)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.editor.toPlainText()=="")
    
    def accept(self):
        if self.item is None:
            self.item=TextItem("",self.position,self.scene)
            
        font=self.fontComboBox.currentFont()
        font.setPointSize(self.fontSpinBox.value())
        self.item.setFont(font)
        self.item.setPlainText(self.editor.toPlainText())
        self.item.update()
        QDialog.accept(self)
        
class settingsWindow(QDialog):
    def __init__(self,parent=None):
        super(settingsWindow,self).__init__(parent)
        self.Tolerancia=QLineEdit("Asigne tolerancia")
        self.Iteraciones=QLineEdit("Asigne número máximo de iteraciones")
        tol_Label=QLabel("Tolerancia:")
        it_Label=QLabel("Máximo número de iteraciones:")
        okButton=QPushButton("OK")
        cancelButton=QPushButton("Cancel")
        buttonLayout=QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout=QGridLayout()
        layout.addWidget(it_Label,0,0)
        layout.addWidget(self.Iteraciones,0,1)
        layout.addWidget(tol_Label,1,0)
        layout.addWidget(self.Tolerancia,1,1)
        layout.addLayout(buttonLayout,2,0,1,3)
        self.setLayout(layout)
        self.setMinimumSize(500,50)
        self.setWindowTitle("Parámetros de cálculo")
        
        '''Slots'''
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
    
    def accept(self):
        try:
            int(self.Iteraciones.text())
            if int(self.Iteraciones.text())<0:
                QMessageBox.warning(self,"Error","Las número máximo de iteraciones no puede ser menor que cero")
                return
            if int(self.Iteraciones.text())==0:
                QMessageBox.warning(self,"Error","Las número máximo de iteraciones no puede ser cero")
                return
        except:
             QMessageBox.warning(self,"Error","Las número máximo de iteraciones tiene que ser un número")
             return
         
        try:
            a=float(self.Tolerancia.text())
            if float(self.Tolerancia.text())<0:
                QMessageBox.warning(self,"Error","La tolerancia no puede ser menor que cero")
                return
            if float(self.Tolerancia.text())==0:
                QMessageBox.warning(self,"Error","La tolerancia no puede ser cero")
                return       
        except:
            QMessageBox.warning(self,"Error","La tolerancia tiene que ser un número")
            return
        QDialog.accept(self)
         
class StreamWindow(QDialog):
    def __init__(self,parent=None):
        super(StreamWindow,self).__init__(parent)
        self.nombre=""
        self.flujo=""
        self.minimo=""
        self.maximo=""
        nombreLabel=QLabel("Nombre")
        flujoLabel=QLabel("Flujo")
        iny_label=QLabel("Inyección")
        self.iny_checkable=QCheckBox("")
        minLabel=QLabel("Mínimo")
        maxLabel=QLabel("Máximo")
        self.funcion_de_label=QLabel("En función de")
        self.funcion_de_combo=QComboBox()
        self.funcion_de_combo.addItems(variables)
        self.funcion_de_combo.setEditable(False)
        self.dependencia_label=QLabel("Dependencia")
        self.dependencia_combo=QComboBox()
        self.dependencia_combo.addItems(["Positiva","Negativa"])
        self.dependencia_combo.setEditable(False)
        self.dependencia_combo.setEnabled(False)
        self.funcion_de_combo.setEnabled(False)
        self.casilla=" "
        
        if flag==False:
            self.Nombre=QLineEdit("Asigne un nombre a la corriente")
            self.Nombre.selectAll()
            self.Flujo=QLineEdit("")
            self.setWindowTitle("Nueva corriente")
            self.critic_checkable=QCheckBox("Variable")
            self.restriccion_checkable=QCheckBox("Restriccion")
            self.fijar_checkable=QCheckBox("Fijar")
            self.minimo=QLineEdit("None")
            self.minimo.setReadOnly(True)
            self.maximo=QLineEdit("None")
            self.maximo.setReadOnly(True)
            self.minimo.setStyleSheet("color:rgb(128,128,128);")
            self.maximo.setStyleSheet("color:rgb(128,128,128);")
            

        else:
            item=form.scene.selectedItems()
            item=item[0]
            self.name=MainWindow.get_itemName(form,item)
            self.Nombre=QLineEdit(self.name)
            self.Nombre.selectAll()
            self.Flujo=QLineEdit(str(streams[self.name].Flujo))
            if streams[self.name].Tipo=="Inyeccion":
                self.iny_checkable.setCheckState(2)
            if streams[self.name].editable()==False and streams[self.name].is_fixed()==False:
                self.Flujo.setReadOnly(True)
                self.Flujo.setStyleSheet("color:rgb(128,128,128);")
            limits=streams[self.name].get_limits()
            self.minimo=QLineEdit(str(limits[0]))
            self.maximo=QLineEdit(str(limits[1]))
            self.critic_checkable=QCheckBox("Variable")
            self.restriccion_checkable=QCheckBox("Restriccion")
            self.fijar_checkable=QCheckBox("Fijar")
            state=streams[self.name].is_critic()
            self.setWindowTitle("Corriente")
            
            if state=="variable" or state=="restriccion":
                self.Flujo.setReadOnly(True)
                self.Flujo.setStyleSheet("color:rgb(128,128,128);")
                if state=="variable":
                    self.critic_checkable.setCheckState(2)
                    self.casilla="variable"
                if state=="restriccion":
                    self.dependencia_combo.setEnabled(True)
                    self.funcion_de_combo.setEnabled(True)
                    self.restriccion_checkable.setCheckState(2)
                    self.casilla="restriccion"
                    if len(restricciones)>0:
                        index=self.funcion_de_combo.findText(restricciones[self.name][0])
                    else:
                        index=0
                    if index>=0:
                        self.funcion_de_combo.setCurrentIndex(index)
                    index=self.dependencia_combo.findText(restricciones[self.name][1])
                    if index>=0:
                        self.dependencia_combo.setCurrentIndex(index)
            
            elif streams[self.name].is_fixed()==True:
                self.fijar_checkable.setCheckState(2)
                self.casilla="fijar"
                self.minimo.setReadOnly(True)
                self.maximo.setReadOnly(True)
                self.minimo.setStyleSheet("color:rgb(128,128,128);")
                self.maximo.setStyleSheet("color:rgb(128,128,128);")
            else:
                self.minimo.setReadOnly(True)
                self.maximo.setReadOnly(True)
                self.minimo.setStyleSheet("color:rgb(128,128,128);")
                self.maximo.setStyleSheet("color:rgb(128,128,128);")
            
               
            

        okButton=QPushButton("&OK")
        cancelButton=QPushButton("Cancel")
        buttonLayout=QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout=QGridLayout()
        layout.addWidget(nombreLabel,0,0)
        layout.addWidget(self.Nombre,0,1)
        layout.addWidget(iny_label,0,2)
        layout.addWidget(self.iny_checkable,0,3)
        layout.addWidget(flujoLabel,1,0)
        layout.addWidget(self.Flujo,1,1)
        layout.addWidget(self.critic_checkable,2,0)
        layout.addWidget(self.restriccion_checkable,2,1)
        layout.addWidget(self.fijar_checkable,2,3)
        layout.addWidget(minLabel,3,0)
        layout.addWidget(self.minimo,3,1)
        layout.addWidget(maxLabel,3,2)
        layout.addWidget(self.maximo,3,3)
        layout.addWidget(self.funcion_de_label,4,0)
        layout.addWidget(self.funcion_de_combo,4,1)
        layout.addWidget(self.dependencia_label,4,2)
        layout.addWidget(self.dependencia_combo,4,3)
        layout.addLayout(buttonLayout,5,0,1,3)
        self.setLayout(layout)
        self.setMinimumSize(300,50)
       

        '''Slots'''
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        self.critic_checkable.toggled.connect(self.critic_stream)
        self.restriccion_checkable.toggled.connect(self.critic_stream)
        self.fijar_checkable.toggled.connect(self.critic_stream)
        
    '''-------------------Funciones de StreamWindow--------------'''
    
    def critic_stream(self):
        if self.casilla=="variable":
            self.critic_checkable.setCheckState(0)
        if self.casilla=="restriccion":
            self.restriccion_checkable.setCheckState(0)
        if self.casilla=="fijar":
            self.fijar_checkable.setCheckState(0)
            
        if self.critic_checkable.checkState()!=0:
            self.Flujo.setReadOnly(True)
            self.Flujo.setText("x")
            self.Flujo.setStyleSheet("color:rgb(128,128,128);")
            self.minimo.setReadOnly(False)
            self.maximo.setReadOnly(False)
            self.minimo.setStyleSheet("color:rgb(0,0,0);")
            self.maximo.setStyleSheet("color:rgb(0,0,0);")
            self.funcion_de_combo.setEnabled(False)
            self.dependencia_combo.setEnabled(False)
            self.casilla="variable"
                
        elif self.restriccion_checkable.checkState()!=0:
            self.Flujo.setReadOnly(True)
            self.Flujo.setText("x")
            self.Flujo.setStyleSheet("color:rgb(128,128,128);")
            self.minimo.setReadOnly(False)
            self.maximo.setReadOnly(False)
            self.minimo.setStyleSheet("color:rgb(0,0,0);")
            self.maximo.setStyleSheet("color:rgb(0,0,0);")
            self.funcion_de_combo.setEnabled(True)
            self.dependencia_combo.setEnabled(True)
            self.casilla="restriccion"
        elif self.fijar_checkable.checkState()!=0:
            self.Flujo.setReadOnly(False)
            self.Flujo.setStyleSheet("color:rgb(0,0,0);")
            self.minimo.setText("None")
            self.maximo.setText("None")
            self.minimo.setReadOnly(True)
            self.maximo.setReadOnly(True)
            self.minimo.setStyleSheet("color:rgb(128,128,128);")
            self.maximo.setStyleSheet("color:rgb(128,128,128);")
            self.funcion_de_combo.setEnabled(False)
            self.dependencia_combo.setEnabled(False)
            self.casilla="fijar"
        else:
            self.Flujo.setReadOnly(False)
            self.Flujo.setStyleSheet("color:rgb(0,0,0);")
            self.minimo.setText("None")
            self.maximo.setText("None")
            self.minimo.setReadOnly(True)
            self.maximo.setReadOnly(True)
            self.minimo.setStyleSheet("color:rgb(128,128,128);")
            self.maximo.setStyleSheet("color:rgb(128,128,128);")
            self.funcion_de_combo.setEnabled(False)
            self.dependencia_combo.setEnabled(False)
            self.casilla=""
            
            
            
    def accept(self):
        try:
            if self.Nombre.text()=="Asigne un nombre a la corriente" or self.Nombre.text()=="":
                if len(streams)==0:
                    self.Nombre.setText("1")
                else:
                    n=len(streams)
                    n+=1
                    self.Nombre.setText(str(n))
            else:
                if flag==False:
                    name=""
                    name_lis=self.Nombre.text().split()
                    for i in name_lis:
                        name+=i
                        name+=" "
                    self.Nombre.setText(name)
                    while self.Nombre.text()[0]==" ":
                        self.Nombre.setText(self.Nombre.text()[1:])
                    while self.Nombre.text()[-1]==" ":
                        self.Nombre.setText(self.Nombre.text()[0:-1])
                    
                    if self.Nombre.text() in streams:
                        QMessageBox.warning(self, "Error de especificación","Ya existe una corriente con el nombre asignado, favor de asignar un nombre diferente")
                        return
                    if self.Nombre.text() in spliters:
                        self.Nombre.setText("Corriente "+self.Nombre.text())
                    if "Divisor" in self.Nombre.text():
                        QMessageBox.warning(self,"Error de nombre","El nombre de una corriente no puede llevar la palabra 'Divisor'")
                        return
                    if "Extracción" in self.Nombre.text():
                        QMessageBox.warning(self,"Error de nombre","El nombre de una corriente no puede llevar la palabra 'Extracción'")
                        return
                elif flag==True:
                    name=""
                    name_lis=self.Nombre.text().split()
                    for i in name_lis:
                        name+=i
                        name+=" "
                    self.Nombre.setText(name)
                    while self.Nombre.text()[0]==" ":
                        self.Nombre.setText(self.Nombre.text()[1:])
                    while self.Nombre.text()[-1]==" ":
                        self.Nombre.setText(self.Nombre.text()[0:-1])
                    if self.name!=self.Nombre.text():
                        if self.Nombre.text() in streams:
                            QMessageBox.warning(self, "Error de especificación","Ya existe una corriente con el nombre asignado, favor de asignar un nombre diferente")
                            return
                        if self.Nombre.text() in spliters:
                            self.Nombre.setText("Corriente "+self.Nombre.text())
                        if "Divisor" in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una corriente no puede llevar la palabra 'Divisor'")    
                            return
                        if "Extracción" in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una corriente no puede llevar la palabra 'Extracción'")    
                            return
            if self.critic_checkable.checkState()!=0 or self.restriccion_checkable.checkState()!=0:
                minimo=self.minimo.text()
                maximo=self.maximo.text()
                minimo=float(minimo)
                maximo=float(maximo)
                if maximo < minimo:
                    QMessageBox.warning(self,"Error en limites","Los limites tienen que ser de la forma mínimo < máximo")
                    return
                if self.restriccion_checkable.checkState()!=0:
                    if self.funcion_de_combo.currentText()=="":
                        QMessageBox.warning(self,"Error en la restricción","Si la corriente se quiere agregar como restricción, es necesario elegir dependencia de una variable")
                        return
            
            if flag==True:
                if self.critic_checkable.checkState()==0:
                    if len(restricciones)!=0:
                        for i in restricciones:
                            if restricciones[i][0]==self.name:
                                   QMessageBox.warning(self,"Error","La corriente "+str(name)+" esta asociada con la variable de restricción "+str(i)+"."+"Favor de primero modificar la variable de restricción a libre")
                                   return
            
            flujo=self.Flujo.text()
            if flujo=="" or flujo=="x":
                self.Flujo.setText("")
                QDialog.accept(self)
            else:
                flujo=float(flujo)
                QDialog.accept(self)
            
        except:
            QMessageBox.warning(self,"Error de flujo","Ningún flujo puede ser texto (Mínimo, máximo, flujo)")
            return

###----------------------------------------------------------------------------------###
'''----------------------------------------------------------------------------------'''
###----------------------------------------------------------------------------------###
class ExtractionWindow(QDialog):
    def __init__(self,parent=None):
        super(ExtractionWindow,self).__init__(parent)
        nombreLabel=QLabel("Nombre")
        flujoLabel=QLabel("Flujo")
        if flag==False:
            self.Nombre=QLineEdit("Asigne un nombre a la extracción")
            self.Nombre.selectAll()
            self.Flujo=QLineEdit("")
            self.setWindowTitle("Nueva extracción")
        elif flag==True:
            item=form.scene.selectedItems()
            item=item[0]
            self.name=MainWindow.get_itemName(form,item)
            self.Nombre=QLineEdit(self.name)
            self.Nombre.selectAll()
            self.Flujo=QLineEdit(str(streams[self.name].Flujo))
            if streams[self.name].editable()!=True:
                self.Flujo.setReadOnly(True)
            self.setWindowTitle("Extracción")
        okButton=QPushButton("&OK")
        cancelButton=QPushButton("Cancel")
        buttonLayout=QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout=QGridLayout()
        layout.addWidget(nombreLabel,0,0)
        layout.addWidget(self.Nombre,0,1)
        layout.addWidget(flujoLabel,1,0)
        layout.addWidget(self.Flujo,1,1)
        layout.addLayout(buttonLayout,2,0,1,3)
        self.setLayout(layout)
        self.setMinimumSize(300,50)
        
        '''Slots'''
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        
        
    '''----------------------------------------------'''
    '''------------Funciones de 'ExtraccionWIndow'----------'''
    def accept(self):
        try:
            flujo=self.Flujo.text()
            flujo=float(flujo)
            if self.Nombre.text()=="Asigne un nombre a la extracción" or self.Nombre.text()=="":
                global streams
                if len(streams)==0:
                    self.Nombre.setText("1")
                else:
                    n=len(streams)
                    n+=1
                    self.Nombre.setText(str(n))
            else:
                name=""
                name_lis=self.Nombre.text().split()
                for i in name_lis:
                    name+=i
                    name+=" "
                self.Nombre.setText(name)
                while self.Nombre.text()[-1]==" ":
                     self.Nombre.setText(self.Nombre.text()[0:-1])
                while self.Nombre.text()[0]==" ":
                    self.Nombre.setText(self.Nombre.text()[1:])
                
                if flag==False:
                    if self.Nombre.text() in streams:
                        QMessageBox.warning(self, "Error de especificación","Ya existe una extracción con el nombre asignado, favor de asignar un nombre diferente")
                        return
                    if self.Nombre.text() in spliters:
                        self.Nombre.setText("Extracción "+self.Nombre.text())
                    if "Divisor" in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una extracción no puede llevar la palabra 'Divisor'")
                            return
                    if "Corriente" in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una extracción no puede llevar la palabra 'Corriente'")
                            return
                if flag==True:
                    if self.name!=self.Nombre.text():
                        if self.Nombre.text() in streams:
                            QMessageBox.warning(self, "Error de especificación","Ya existe una extracción con el nombre asignado, favor de asignar un nombre diferente")
                            return
                        if self.Nombre.text() in spliters:
                            self.Nombre.setText("Extracción "+ self.Nombre.text())
                        if "Divisor"  in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una extracción no puede llevar la palabra 'Divisor'")
                            return
                        if "Corriente" in self.Nombre.text():
                            QMessageBox.warning(self,"Error de nombre","El nombre de una extracción no puede llevar la palabra 'Corriente'")
                            return
            QDialog.accept(self)
        except:
            if flujo=="" or flujo=="Favor de assignar un flujo":
                self.Flujo.setText("Favor de assignar un flujo")
                self.Flujo.selectAll()
                self.Flujo.setFocus()
                return
            else:
                self.Flujo.setText("El flujo debe de ser un numero")
                self.Flujo.selectAll()
                self.Flujo.setFocus()
                return
            
###---------------------------------------------------------------------------####
'''---------------------------------------------------------------------------'''
###---------------------------------------------------------------------------####

class DivisorWindow(QDialog):
    def __init__(self,parent=None):
        super(DivisorWindow,self).__init__(parent)
        self.NombreLabel=QLabel("Nombre")
        self.EntradasLabel=QLabel("Entradas")
        self.SalidasLabel=QLabel("Salidas")
        self.Entradas_seleccionadas_Label=QLabel("Entradas seleccionadas")
        self.Salidas_seleccionadas_Label=QLabel("Salidas seleccionadas")
        self.Nombre=QLineEdit("Asigne nombre al divisor")
        self.textbox=QLineEdit("Buscar corriente")
        self.Entradas=[]         #Lists to parse to spliter object
        self.Salidas=[]
        self.offset_inlets=0
        self.offset_outlets=0
        
        
        '''Seteo de checklist''' 
        #Declaración de elementos necesarios para el seteo de la lista
        
        self.entradas_list=QListView()
        self.salidas_list=QListView()
        self.inlet_list=QListView()
        self.outlet_list=QListView()
        self.model_inlets=QStandardItemModel()
        self.model_outlets=QStandardItemModel()
        self.inside_streams=[] #Lista de corrientes dentro del dialogo 
        
        #Obtención de lista de corrientes
        
        for i in streams:
            self.inside_streams.append(streams[i].name)
        self.inside_streams.sort()

        #seteo
        
        '''Creación o modificación'''
        if flag==True:
            item=form.scene.selectedItems()
            item=item[0]
            self.name=MainWindow.get_itemName(form,item)
            self.Nombre.setText(self.name)
            selected_inlets=spliters[self.name].entradas
            selected_outlets=spliters[self.name].salidas
            for i in self.inside_streams:
                item=QStandardItem(i)
                item.setCheckable(True)
                if i in selected_inlets:
                    item.setCheckState(1)
                    self.Entradas.append(i)
                self.model_inlets.appendRow(item)
                item=QStandardItem(i)
                item.setCheckable(True)
                if i in selected_outlets:
                    item.setCheckState(1)
                    self.Salidas.append(i)
                self.model_outlets.appendRow(item)
            self.model_entradas=QStandardItemModel()
            self.model_salidas=QStandardItemModel()
            for i in self.Entradas:
                item=QStandardItem(i)
                item.setEnabled(False)
                self.model_entradas.appendRow(item)
                self.model_salidas=QStandardItemModel()
            for i in self.Salidas:
                item=QStandardItem(i)
                item.setEnabled(False)
                self.model_salidas.appendRow(item)
            self.salidas_list.setModel(self.model_salidas)
            self.entradas_list.setModel(self.model_entradas)
            self.inlet_list.setModel(self.model_inlets)
            self.outlet_list.setModel(self.model_outlets)
            
        else:
            for i in self.inside_streams:
                item=QStandardItem(i)
                item.setCheckable(True)
                self.model_inlets.appendRow(item)
                item=QStandardItem(i)
                item.setCheckable(True)
                self.model_outlets.appendRow(item)
            self.inlet_list.setModel(self.model_inlets)
            self.outlet_list.setModel(self.model_outlets)
        
        
        
        ''' Botones "ok" y "cancel"'''
        okButton=QPushButton("&OK")
        cancelButton=QPushButton("Cancel")
        buttonLayout=QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

            
        
        '''Seteo de grid y layout'''
        layout=QGridLayout()
        layout.addWidget(self.NombreLabel,0,0)
        layout.addWidget(self.Nombre,0,1)
        layout.addWidget(self.EntradasLabel,1,0)
        layout.addWidget(self.SalidasLabel,1,1)
        layout.addWidget(self.inlet_list,2,0)
        layout.addWidget(self.outlet_list,2,1)
        layout.addWidget(self.textbox,3,0,1,3)
        layout.addWidget(self.Entradas_seleccionadas_Label,4,0)
        layout.addWidget(self.Salidas_seleccionadas_Label,4,1)
        layout.addWidget(self.entradas_list,5,0)
        layout.addWidget(self.salidas_list,5,1)
        layout.addLayout(buttonLayout,6,0,1,3)
        self.setLayout(layout)
        self.setWindowTitle("Nuevo divisor")
        self.setMinimumSize(300,50)
        
        
        '''Slots'''
        okButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)
        self.textbox.textChanged.connect(self.refresh_list)
        self.model_inlets.itemChanged.connect(self.item_changed_inlets)
        self.model_outlets.itemChanged.connect(self.item_changed_outlets)
            
        self.textbox.selectAll()
        self.textbox.setFocus()
        
        
    '''------------------------------------------'''
    '''-----Funciones de 'DivisorWindow'---------'''
    '''--------------------------------------------'''
    def refresh_list(self):
        self.model_outlets=QStandardItemModel()
        self.model_inlets=QStandardItemModel()
        self.model_inlets.itemChanged.connect(self.item_changed_inlets)
        self.model_outlets.itemChanged.connect(self.item_changed_outlets)
        if self.textbox.text()=="":
            for i in self.inside_streams:
                item=QStandardItem(i)
                item.setCheckable(True)
                if i in self.Entradas:
                    item.setCheckState(1)
                self.model_inlets.appendRow(item)
                item=QStandardItem(i)
                item.setCheckable(True)
                if i in self.Salidas:
                    item.setCheckState(1)
                self.model_outlets.appendRow(item)
            self.inlet_list.setModel(self.model_inlets)
            self.outlet_list.setModel(self.model_outlets)
    
        else:
            for stream in self.inside_streams:
                if self.textbox.text() in stream:
                    item=QStandardItem(stream)
                    item.setCheckable(True)
                    if stream in self.Entradas:
                        item.setCheckState(1)
                    self.model_inlets.appendRow(item)
                    item=QStandardItem(stream)
                    item.setCheckable(True)
                    if stream in self.Salidas:
                        item.setCheckState(1)
                    self.model_outlets.appendRow(item)
            self.inlet_list.setModel(self.model_inlets)
            self.outlet_list.setModel(self.model_outlets)
    
    def item_changed_inlets(self,item):
        if item.checkState()!=0 and item.text() not in self.Entradas:
            self.Entradas.append(item.text())
                
        elif item.checkState()==0 and item.text() in self.Entradas:
            self.Entradas.remove(item.text())
        
        self.model_entradas=QStandardItemModel()
        for i in self.Entradas:
            item=QStandardItem(i)
            item.setEnabled(False)
            self.model_entradas.appendRow(item)
        self.entradas_list.setModel(self.model_entradas)
    
    def item_changed_outlets(self,item):
        if item.checkState()!=0 and item.text() not in self.Salidas:
            self.Salidas.append(item.text())
        elif item.checkState()==0 and item.text() in self.Salidas:
            self.Salidas.remove(item.text())     
        
        self.model_salidas=QStandardItemModel()
        for i in self.Salidas:
            item=QStandardItem(i)
            item.setEnabled(False)
            self.model_salidas.appendRow(item)
        self.salidas_list.setModel(self.model_salidas)
            
    def accept(self):
        
        if len(self.Entradas)==0 or len(self.Salidas)==0:
            QMessageBox.warning(self, "Error de especificación","Es necesario especificar por lo menos una corriente de entrada y una corriente de salida")            
            return
        else:
            for i in self.Entradas:
                if i in self.Salidas:
                    QMessageBox.warning(self, "Error de especificación","Una misma corriente no puede ser entrada y salida a la vez")  
                    return
            if self.Nombre.text()=="Asigne nombre al divisor" or self.Nombre.text()=="":
                name_divisor=len(spliters)
                if name_divisor==0:
                    name_divisor+=1
                    self.Nombre.setText("Divisor "+str(name_divisor))
                else:
                    name_divisor+=1
                    while "Divisor "+str(name_divisor) in spliters:
                        name_divisor+=1
                    self.Nombre.setText("Divisor "+str(name_divisor))
            else:
                if len(spliters)==0:
                    QDialog.accept(self)
                else:
                    if flag==False:
                        name=""
                        name_lis=self.Nombre.text().split()
                        for i in name_lis:
                            name+=i
                            name+=" "
                        self.Nombre.setText(name)
                        while self.Nombre.text()[0]==" ":
                                self.Nombre.setText(self.Nombre.text()[1:])
                        while self.Nombre.text()[-1]==" ":
                                self.Nombre.setText(self.Nombre.text()[0:-1])
                                
                        if self.Nombre.text() in streams:
                            self.Nombre.setText("Divisor "+self.Nombre.text())
                            if self.Nombre.text() in spliters:
                                QMessageBox.warning(self, "Error de especificación","Ya existe un divisor con el nombre asignado. Favor de asignar un nombre diferente")
                                return
                        if self.Nombre.text() in spliters:
                            QMessageBox.warning(self, "Error de especificación","Ya existe un divisor con el nombre asignado. Favor de asignar un nombre diferente")
                            return
                        if "Corriente" in self.Nombre.text():
                                QMessageBox.warning(self,"Error de nombre","El nombre de un divisor no puede contener la palabra 'Corriente'")
                                return
                        if "Extracción" in self.Nombre.text():
                                QMessageBox.warning(self,"Error de nombre","El nombre de un divisor no puede contener la palabra 'Extracción'")
                                return
                    elif flag==True:
                        name=""
                        name_lis=self.Nombre.text().split()
                        for i in name_lis:
                            name+=i
                            name+=" "
                        self.Nombre.setText(name)
                        while self.Nombre.text()[0]==" ":
                                self.Nombre.setText(self.Nombre.text()[1:])
                        while self.Nombre.text()[-1]==" ":
                                self.Nombre.setText(self.Nombre.text()[0:-1])
                        
                        if self.name!=self.Nombre.text():
                            if self.Nombre.text() in streams:
                                self.Nombre.setText("Divisor "+self.Nombre.text())
                                
                            if self.Nombre.text() in spliters:
                                QMessageBox.warning(self, "Error de especificación","Ya existe un divisor con el nombre asignado. Favor de asignar un nombre diferente")
                                return
                            if "Corriente" in self.Nombre.text():
                                QMessageBox.warning(self,"Error de nombre","El nombre de un divisor no puede contener la palabra 'Corriente'")
                                return
                            if "Extracción" in self.Nombre.text():
                                QMessageBox.warning(self,"Error de nombre","El nombre de un divisor no puede contener la palabra 'Extracción'")
                                return
                        else:
                            QDialog.accept(self)
        
                      
        QDialog.accept(self)
        
#########################################################################################################################        
'''-------------------------------------------------------------------------------------------------------------------'''
#########################################################################################################################

class MainWindow(QMainWindow):    
    
    
    def __init__(self,parent=None):
        #Main Window
        super(MainWindow,self).__init__(parent)
        self.threadpool=QThreadPool()
        self.filename=""
        self.prevPoint=QPoint()
        self.setWindowTitle("Balanceador del Sistrangas----")
        self.addOffset=5
        self.setWindowIcon(QIcon(":/LogoCenagas.png"))
        self.prevPoint=QPoint()
        self.tol=0.001
        self.max_it=50
        

        '''---------------'''
        '''Actions & Icons'''
        
        #Icons para paleta de botones
        #Stream Icon
        self.AddStream=QPushButton("")
        self.AddStream.setIcon(QIcon(":/stream_button.png"))
        self.AddStream.setIconSize(QSize(80,20))
        helpText="Create a new stream"
        self.AddStream.setToolTip(helpText)
        self.AddStream.setStatusTip(helpText)
        self.AddStream.clicked.connect(self.addStreamFun)
        
        #Extraccion Icon
        self.AddExtraccion=QPushButton("")
        self.AddExtraccion.setIcon(QIcon(":/extraction_button.png"))
        self.AddExtraccion.setIconSize(QSize(80,20))
        helpText="Create a new extraccion"
        self.AddExtraccion.setToolTip(helpText)
        self.AddExtraccion.setStatusTip(helpText)
        self.AddExtraccion.clicked.connect(self.addExtractionFun)
        
        #Divisor Icon
        self.AddDivisor=QPushButton("")
        self.AddDivisor.setIcon(QIcon(":/Divisor.png"))
        self.AddDivisor.setIconSize(QSize(80,20))
        helpText="Create a new divisor"
        self.AddDivisor.setToolTip(helpText)
        self.AddDivisor.setStatusTip(helpText)
        self.AddDivisor.clicked.connect(self.addDivisorFun)
        
        #Rotate Icon
        self.RotateIcon=QPushButton("")
        self.RotateIcon.setIcon(QIcon(":/rotate_button.png"))
        self.RotateIcon.setIconSize(QSize(80,20))
        helpText="Rotate Icon"
        self.RotateIcon.setToolTip(helpText)
        self.RotateIcon.setStatusTip(helpText)
        self.RotateIcon.clicked.connect(self.rotate)
        
        #Cenagas Icon
        self.CenagasLogo=QLabel("")
        pixmap=QPixmap(":/Cenagas.png")
        pixmap_resized=pixmap.scaled(300,75.09)
        self.CenagasLogo.setPixmap(pixmap_resized)
        
        #Icons para tool bars
    
        #New Document Icon
        self.fileNewAction=QAction(QIcon(":/add-new-document.png"),"&New",self)
        self.fileNewAction.setShortcut(QKeySequence.New)
        helpText="Create a new document"
        self.fileNewAction.setToolTip(helpText)
        self.fileNewAction.setStatusTip(helpText)
        self.fileNewAction.triggered.connect(self.new_file)
        
        #Settings Icon
        self.settingsAction=QAction(QIcon(""),"Settings",self)
        self.settingsAction.setToolTip("Modificar parámetros de cálculo")
        self.settingsAction.triggered.connect(self.modify_settings)
        
        #Text Icon
        self.addTextAction=QAction(QIcon(""),"Agregar cuadro de texto",self)
        self.addTextAction.setToolTip("Agregar cuadro de texto a la escena")
        self.addTextAction.triggered.connect(self.addText)
        self.addTextAction.setShortcut("Ctrl+T")
        self.addTextAction.setToolTip("Agregar cuadro de texto(Ctrl+T)")
        
        #Run calculation Icon
        self.runCalculation=QAction(QIcon(":/run.png"),"&Run",self)
        self.runCalculation.setShortcut("F5")
        self.runCalculation.setToolTip("Run calculation. (F5)")
        self.runCalculation.setStatusTip("Run calculation")
        self.runCalculation.triggered.connect(self.run_all)
        
        #Save Icon
        self.save_action=QAction(QIcon(":/save.png"),"&Save",self)
        self.save_action.setShortcut(QKeySequence.Save)
        helpText="Save document"
        self.save_action.setToolTip(helpText)
        self.save_action.setStatusTip(helpText)
        self.save_action.triggered.connect(self.save)
        
        #Save as Icon
        self.save_as_action=QAction(QIcon(":/save.png"),"Save as",self)
        helpText="Save document as"
        self.save_as_action.setToolTip(helpText)
        self.save_as_action.setStatusTip(helpText)
        self.save_as_action.triggered.connect(self.save_as)
        
        #Open Icon
        self.open_action=QAction(QIcon(":/open.png"),"&Open",self)
        self.open_action.setShortcut(QKeySequence.Open)
        helpText="Open document"
        self.open_action.setToolTip(helpText)
        self.open_action.setToolTip(helpText)
        self.open_action.triggered.connect(self.Open)
                
        #Reset Streams
        self.reset_streams=QAction(QIcon(":/reset.png"),"Reset Streams",self)
        self.reset_streams.setShortcut("Ctrl+R")
        self.reset_streams.setToolTip("Reset Streams")
        self.reset_streams.triggered.connect(self.resetf)
        
        #Import data from Excel Icon
        self.import_from_excel=QAction(QIcon(":/excel.png"),"Import from excel",self)
        self.import_from_excel.setShortcut("Ctrl+I")
        self.import_from_excel.setToolTip("Importar datos de excel (Ctrl+I)")
        self.import_from_excel.triggered.connect(self.importf)

        #Import results
        self.export_results=QAction(QIcon(":/export.png"),"Import results",self)
        self.export_results.setShortcut("Ctrl+E")
        self.export_results.setToolTip("Exportar resultados a excel (Ctrl+E)")
        self.export_results.triggered.connect(self.export)
        

        

        
        '''--------------------------'''
        
        '''Docked widgets'''
        #Graphics window
        self.view=GraphicsView(self)
        self.scene=QGraphicsScene(self)
        self.scene.setSceneRect(0,0,PageSize[0],PageSize[1])
        self.view.setScene(self.scene)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.marco()
        
        # Paleta de botones
        self.Widget=QWidget(self) 
        self.Widget.setLayout(QVBoxLayout())
        self.GridWidgetProceso=QGridLayout()
        self.GridWidgetProceso.addWidget(self.CenagasLogo,0,0,0,4)
        self.GridWidgetProceso.addWidget(self.AddStream,1,0)
        self.GridWidgetProceso.addWidget(self.AddExtraccion,1,1)
        self.GridWidgetProceso.addWidget(self.AddDivisor,1,2)
        self.GridWidgetProceso.addWidget(self.RotateIcon,1,3)
        self.Widget.layout().addLayout(self.GridWidgetProceso)
        
        #Ventana de eventos
        self.logDockWidget=QDockWidget("Log",self)
        self.logDockWidget.setObjectName("LogDockWidget")
        self.listWidget=QTextBrowser()
        self.logDockWidget.setWidget(self.listWidget)
        
        #Status Bar
        self.sizeLabel=QLabel()
        self.sizeLabel.setFrameStyle(QFrame.Sunken)
        status=self.statusBar()
        status.setSizeGripEnabled(True)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready",10000)
        
        '''---------------'''
        
        '''Menus'''
        
        fileMenu=self.menuBar().addMenu("File")
        fileMenu.addAction(self.fileNewAction)
        fileToolbar=self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        fileToolbar.addAction(self.fileNewAction)
        
        #Tools menu
        toolsMenu=self.menuBar().addMenu("Herramientas")
        toolsMenu.addAction(self.settingsAction)
        toolsMenu.addAction(self.addTextAction)
        
        
        #Barra de proceso
        processToolbar=self.addToolBar("Process")
        processToolbar.setObjectName("ProcessToolBar")
        
        #Run icon bar
        processToolbar.addAction(self.runCalculation)
        
        #Reset Streams icon bar
        processToolbar.addAction(self.reset_streams)

        #Import from excel icon bar
        processToolbar.addAction(self.import_from_excel)
        
        #Export results
        processToolbar.addAction(self.export_results)
        
        #Save
        fileMenu.addAction(self.save_action)
        fileMenu.addAction(self.save_as_action)
        
        #Open
        fileMenu.addAction(self.open_action)
        #Open new file
        fileMenu.addAction(self.fileNewAction)
        
        '''----------------------------'''
        
        '''Spliters'''
        
        self.ProcesoSplitter=QSplitter(Qt.Vertical)
        self.ProcesoSplitter.addWidget(self.Widget)
        self.ProcesoSplitter.addWidget(self.logDockWidget)
        self.mainSplitter=QSplitter(Qt.Horizontal)
        self.mainSplitter.addWidget(self.ProcesoSplitter)
        self.mainSplitter.addWidget(self.view)
        self.setCentralWidget(self.mainSplitter)
        
        
    
    '''_______________---------__________________'''
    '''---------------Funciones------------------'''    
    '''_______________---------__________________'''
    

    
    def addText(self):
        dialog=TextItemDlg(position=self.position(),scene=self.scene,parent=self)
        dialog.exec_()
        
    def resetf(self):
        for stream in streams:
            if streams[stream].editable()!=True:
                if streams[stream].is_fixed()==False:
                    streams[stream].Flujo="x"
                streams[stream].edit=True
        for i in variables:
            streams[i].Flujo="x"
        for i in restricciones:
            streams[i].Flujo="x"
        for item in self.scene.items():
            name=self.get_itemName(item)
            if name in streams:
                item.setToolTip("Nombre: "+name+"\n Flujo: "+str(streams[name].Flujo))
        self.updateLog("Streams reset")   
        
    def marco(self):
            rect=QRectF(0,0,PageSize[0],PageSize[1])
            self.scene.addRect(rect,Qt.black)
            margin=0.01
            for i in range(0,100):
                self.scene.addRect(rect.adjusted(margin,margin,-margin,-margin))
                margin+=0.01
    
    def rotate(self):
        for item in self.scene.selectedItems():
            if item.rotation()==360:
                item.setRotation(0)
            angle=30+item.rotation()
            item.setRotation(angle)
            
    def position(self):
        point=self.mapFromGlobal(QCursor.pos())
        if not self.view.geometry().contains(point):
            coord=random.randint(0,144)
            point=QPoint(coord,coord)
        else:
            if point==self.prevPoint:
                point+=QPoint(self.addOffset,self.addOffset)
                self.addOffset+=50
            else:
                self.prevPoint=point
        return self.view.mapToScene(point)  
    
    def modify_settings(self):
        dialog=settingsWindow(self)
        if dialog.exec_():
            self.tol=float(dialog.Tolerancia.text())
            self.max_it=int(dialog.Iteraciones.text())
            self.updateLog("Parámetros de cálculo modificados")
            self.updateLog("Máximo número de iteraciones: "+str(self.max_it)+" Tolerancia: "+str(self.tol))
        
    def addStreamFun(self):
       
        
        dialog=StreamWindow(self)
        if dialog.exec_():
            item=graphic_object()
            pixmap=QPixmap(":/Stream.png")
            group_test=QGraphicsItemGroup()
            item.setPixmap(pixmap.scaled(200,100))
            item.setPos(self.position())
            a=self.addItemF(item,dialog,"Corriente")
            #Add to scene
            self.scene.clearSelection()
            test_name=self.get_itemName(item)    
            self.scene.addItem(item)
            item.setSelected(True)           
                 
                
    def addExtractionFun(self):
        
        ''' Validador del dialogo "extraccion" '''
        
        dialog=ExtractionWindow(self)
        if dialog.exec_():
            item=graphic_object()
            pixmap=QPixmap(":/Extraccion.png")
            item.setPixmap(pixmap.scaled(200,100))
            item.setPos(self.position())
            self.scene.clearSelection()
            self.addItemF(item,dialog,"Extraccion") #Para añadir info y corriente a lista global de corrientes. Funcion definida por mi
            test_name=self.get_itemName(item)
            if test_name==dialog.Nombre.text():
                self.scene.addItem(item)
                item.setSelected(True)           
            else:
                if test_name!="":
                    del streams[dialog.Nombre.text()]
                    dialog.Nombre.setText(test_name)
                    self.addItemF(item,dialog,"Extraccion")
                    try:
                        test_name=self.get_itemName(item)
                        streams[test_name]
                        self.scene.addItem(item)
                        item.setSelected(True)
                    except:
                        self.updateLog("<font color=red>Error al crear extracción, favor de crearla de nuevo</font>")
                        del streams[dialog.Nombre.text()]        
                else:
                        self.updateLog("<font color=red>Error al crear extracción, favor de crearla de nuevo</font>")
                        del streams[dialog.Nombre.text()]        
                
    def addDivisorFun(self):
        dialog=DivisorWindow(self)
        if dialog.exec_():
            item=graphic_object()
            pixmap=QPixmap(":/Divisor.png")
            item.setPixmap(pixmap.scaled(200,200))
            item.setPos(self.position())
            self.scene.clearSelection()
            a=self.addItemF(item,dialog,"Divisor")
            test_name=self.get_itemName(item)
            if test_name==dialog.Nombre.text():
                self.scene.addItem(item)
                item.setSelected(True)           
            else:
                if test_name!="":
                    del spliters[dialog.Nombre.text()]
                    dialog.Nombre.setText(test_name)
                    self.addItemF(item,dialog,"Divisor")
                    try:
                        test_name=self.get_itemName(item)
                        spliters[test_name]
                        self.scene.addItem(item)
                        item.setSelected(True)
                    except:
                        self.updateLog("<font color=red>Error al crear divisor, favor de crearla de nuevo</font>")
                        del spliters[dialog.Nombre.text()]        
                else:
                        self.updateLog("<font color=red>Error al crear divisor, favor de crearla de nuevo</font>")
                        del splters[dialog.Nombre.text()]        
            
    def updateLog(self,message):
        self.statusBar().showMessage(message,5000)
        self.listWidget.append(message)
    
    def addItemF(self,item,dialog,tipo):
        if tipo=="Extraccion" or tipo=="Corriente":
            stream=Stream(dialog.Nombre.text())
            flujo=dialog.Flujo.text()
            if flujo=="":
                flujo="x"
            else:
                flujo=float(flujo)
            
            stream.Flujo(flujo)
            if tipo=="Corriente":
                if dialog.critic_checkable.checkState()!=0 or dialog.restriccion_checkable.checkState()!=0:
                    minimo=float(dialog.minimo.text())
                    maximo=float(dialog.maximo.text())
                    limits=(minimo,maximo)
                    stream.limits=limits
                    if dialog.critic_checkable.checkState()!=0:
                        stream.critic="variable"
                        variables.append(stream.name)
                    else:
                        stream.critic="restriccion"
                        funcion_de=dialog.funcion_de_combo.currentText()
                        dependencia=dialog.dependencia_combo.currentText()
                        restricciones[stream.name]=[funcion_de,dependencia]
                        streams[stream].funcion_de=funcion_de
                        streams[stream].dependencia=dependencia
                elif dialog.fijar_checkable.checkState()!=0:
                    stream.fixed=True
                if dialog.iny_checkable.checkState()!=0:
                    stream.Tipo="Inyeccion"
                else:
                    stream.Tipo="Corriente"
            else:
                stream.Tipo="Extraccion"
            
            
            
            global streams
            streams[stream.name]=stream
            if stream.name in streams:
                item.setToolTip("Nombre: "+stream.name+"\n Flujo: "+str(stream.Flujo))
                self.updateLog(str(stream.Tipo)+" añadida con el nombre: "+str(stream.name))
                return "ok"
            else:
                return "error"
            
        elif tipo=="Divisor":
            spliter=Spliter(dialog.Nombre.text())
            spliter.entradas(dialog.Entradas)
            spliter.salidas(dialog.Salidas)
            global spliters
            spliters[spliter.name]=spliter
            spliters[spliter.name].status("Unsolved")
            if spliter.name in spliters:
                item.setToolTip("Nombre: "+''+str(dialog.Nombre.text()))
                self.updateLog(str(tipo)+" añadido con el nombre: "+str(spliter.name))
                return "ok"
            else:
                return "error"
            
    def get_itemName(self,item):
        tool_tip=item.toolTip()
        tool_tip_lis=tool_tip.split()
        i=1
        name=""
        if "Flujo:" in tool_tip_lis:
            while tool_tip_lis[i]!="Flujo:":
                name+=tool_tip_lis[i]
                if tool_tip_lis[i+1]!="Flujo:":
                    name+=" "
                i+=1
        elif "Nombre:" in tool_tip_lis and not "Flujo:" in tool_tip_lis:
            for i in range(0,len(tool_tip_lis)):
                if i!=0:
                    name+=tool_tip_lis[i]
                if i!=len(tool_tip_lis)-1 and i!=0:
                    name+=" "
        return name

    def solve_unique(self,spliter,tol):
        ans=node(streams,spliters[spliter],tol)
        if ans[0]==0 or ans[0]==1:
            corrientes=[]
            for i in spliters[spliter].entradas:
                    corrientes.append(i)
            for i in spliters[spliter].salidas:
                    corrientes.append(i)
#            for item in self.scene.items():
#                name=self.get_itemName(item)     #Obtiene el nombre de la corriente en item
#                for corriente in corrientes:
#                    name_2=name.replace(" ","")
#                    corriente_2=corriente.replace(" ","")
#                    if name_2==corriente_2:
#                        item.setToolTip("Nombre: "+corriente+"\n Flujo: "+str(streams[corriente].Flujo))
#                        
    
    def delete_item(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)
            name=self.get_itemName(item)
            if name in streams:
                del streams[name]
                self.updateLog("Stream: "+str(name)+" deleted")
                for spliter in spliters:
                    if name in spliters[spliter].entradas:
                        for entrada in spliters[spliter].entradas:
                            if name==entrada:
                                spliters[spliter].entradas.remove(name)
                    if name in spliters[spliter].salidas:
                        for salida in spliters[spliter].salidas:
                            if name==salida:
                                spliters[spliter].salidas.remove(name)
            if name in spliters:
                del spliters[name]
                self.updateLog("Spliter: "+str(name)+" deleted")
            
            
        
    def modify_item(self):
        global flag
        global streams
        item=self.scene.selectedItems()
        if len(item)>1:
            QMessageBox.warning(self, "Error","Seleccione solo un elemento por favor.")
        else:
            item=item[0]
            name=str(self.get_itemName(item))
            if name in streams:
                tipo=streams[name].Tipo
                flag=True
                if tipo=="Corriente":
                    dialog=StreamWindow(self)
                elif tipo=="Inyeccion":
                    dialog=StreamWindow(self)
                elif tipo=="Extraccion":
                    dialog=ExtractionWindow(self)
                if dialog.exec_():
                       name_before=streams[name].name
                       flujo_before=streams[name].Flujo
                       critic_before=streams[name].is_critic()
                       fixed_before=streams[name].is_fixed()  
                       limits_before=streams[name].get_limits()
                       tipo_before=streams[name].get_Tipo()
                       
                       if dialog.Nombre.text()==name:
                           #Si lo que cambio fue el flujo.....
                           
                           flujo=dialog.Flujo.text()
                           if flujo=="" or flujo=="x":
                               flujo="x"
                           else:
                               flujo=float(flujo)
                           streams[name].Flujo=flujo
                           stream=streams[name]
                           item.setToolTip("Nombre: "+stream.name+"\n Flujo: "+str(stream.Flujo))
                       else:
                           #Si lo que cambio fue el nombre.....
                           
                           item.setToolTip("Nombre: "+dialog.Nombre.text()+"\n Flujo: "+str(dialog.Flujo.text()))  
                           stream=Stream(dialog.Nombre.text())
                           flujo=dialog.Flujo.text()
                           if flujo=="" or flujo=="x":
                               flujo="x"
                           else:
                               flujo=float(flujo)
                           stream.Flujo(flujo)
                           stream.Tipo=tipo
                           editable=streams[name].editable()
                           del streams[name]
                           streams[stream.name]=stream
                           name=stream.name
                           streams[name].edit=editable
                           for spliter in spliters:
                               #Modificar nombre en los divisores asociados
                               if name_before in spliters[spliter].entradas:
                                   for entrada in spliters[spliter].entradas:
                                       if name_before==entrada:
                                           spliters[spliter].entradas.remove(name_before)
                                           spliters[spliter].entradas.append(name)
                               elif name_before in spliters[spliter].salidas:
                                   for salida in spliters[spliter].salidas:
                                       if name_before==salida:
                                           spliters[spliter].salidas.remove(name_before)
                                           spliters[spliter].salidas.append(name)
                           if tipo=="Corriente":
                                if len(restricciones)>0:
                                   for i in restricciones:
                                       if restricciones[i][0]==name_before:
                                           restricciones[i][0]=streams[name].name
                                if dialog.iny_checkable.checkState()!=0:
                                    streams[name].Tipo="Inyeccion"
                                else:
                                    streams[name].Tipo="Corriente"
                       if tipo=="Corriente":                
                               if name_before in variables:
                                       variables.remove(name_before)
                               if name_before in restricciones:
                                       del restricciones[name_before]
                               
                               if dialog.critic_checkable.checkState()!=0:
                                    ans="variable"
                               elif dialog.restriccion_checkable.checkState()!=0:
                                    ans="restriccion"
                               elif dialog.fijar_checkable.checkState()!=0:
                                   ans="fixed"
                               else:
                                   ans=None
                                
                               if ans=="fixed":
                                   '''Opcion cuando la casilla marcada es "fixed"'''    
                                   if dialog.fijar_checkable.checkState()!=0:
                                       state="fija"
                                       minimo="None"
                                       maximo="None"
                                       limits=(minimo,maximo)
                                       streams[name].limits=limits
                                       streams[name].critic=False
                                       streams[name].fixed=True
                                       streams[name].edit=True
                                       
                                       for i in range(0,len(variables)):
                                           if variables[i]==name:
                                               del variables[i]
                                               break  
                               elif ans=="variable" or ans=="restriccion":
                                       '''Opcion cuando variable o restriccion esta marcada'''
                                       minimo=float(dialog.minimo.text())
                                       maximo=float(dialog.maximo.text())
                                       limits=(minimo,maximo)
                                       streams[name].limits=limits
                                       if dialog.critic_checkable.checkState()!=0:
                                           streams[name].critic="variable"
                                           variables.append(streams[name].name)
                                           streams[name].funcion_de=""
                                           streams[name].dependencia=""
                                       elif dialog.restriccion_checkable.checkState()!=0:
                                           streams[name].critic="restriccion"
                                           funcion_de=dialog.funcion_de_combo.currentText()
                                           dependencia=dialog.dependencia_combo.currentText()
                                           restricciones[name]=[funcion_de,dependencia]
                                           streams[name].funcion_de=funcion_de
                                           streams[name].dependencia=dependencia
                                           
                               elif ans==None:
                                       state="no variable ni restricción"
                                       minimo="None"
                                       maximo="None"
                                       limits=(minimo,maximo)
                                       streams[name].limits=limits
                                       streams[name].critic=False
                                       streams[name].fixed=False
                                       streams[name].funcion_de=""
                                       streams[name].dependnecia=""
                       
                       if name_before!=streams[name].name or flujo_before!=streams[name].Flujo:
                           if tipo=="Corriente" or tipo=="Inyeccion":
                               if name_before!=streams[name].name:
                                   self.updateLog("Corriente "+name_before+", modificada a "+streams[name].name)
                               if flujo_before!=streams[name].Flujo:
                                   self.updateLog("Flujo de la corriente "+streams[name].name+", modificado a "+str(streams[name].Flujo))    
                               if critic_before!=streams[name].is_critic():
                                   if streams[name].is_critic()==False:
                                       self.updateLog("Corriente "+streams[name].name+", modificada a "+"fija")
                                   else:
                                       self.updateLog("Corriente "+streams[name].name+", modificada a "+str(streams[name].is_critic()))
                               if limits_before!=streams[name].get_limits():
                                   self.updateLog("Los limites de la corriente "+streams[name].name+" han sido modificados")
                               if tipo_before!=streams[name].get_Tipo():
                                   self.updateLog("La corriente "+str(streams[name].name+" ha sido cambiada a tipo "+str(streams[name].get_Tipo())))
                           elif tipo=="Extraccion":
                               if name_before!=streams[name].name:
                                   self.updateLog("Extracción "+name_before+", modificada a "+streams[name].name)
                               if flujo_before!=streams[name].Flujo:
                                   self.updateLog("Flujo de la extracción "+streams[name].name+", modificado a "+str(streams[name].Flujo))
                       else:
                           if tipo_before!=streams[name].get_Tipo():
                                   self.updateLog("La corriente "+str(streams[name].name+" ha sido cambiada a tipo "+str(streams[name].get_Tipo()))) 
                           if critic_before!=streams[name].is_critic():
                                if streams[name].is_critic()==False:
                                       self.updateLog("Corriente "+streams[name].name+", modificada a "+"fija")
                                else:
                                       self.updateLog("Corriente "+streams[name].name+", modificada a "+str(streams[name].is_critic()))
                                   
                           if limits_before!=streams[name].get_limits():
                                   self.updateLog("Los limites de la corriente "+streams[name].name+" han sido modificados")
                            
                flag=False

            elif name in spliters:
                flag=True
                dialog=DivisorWindow(self)
                global spliters
                if dialog.exec_():
                    if name==dialog.Nombre.text():
                        del spliters[name].entradas
                        del spliters[name].salidas
                        spliters[name].entradas=dialog.Entradas
                        spliters[name].salidas=dialog.Salidas
                        #self.solve_unique(name)
                    else:
                        #Si lo que cambio fue el nombre
                        
                        item.setToolTip("Nombre: "+''+str(dialog.Nombre.text()))
                        test_name=self.get_itemName(item)
                        if test_name!=dialog.Nombre.text():
                            if test_name!="":
                                dialog.Nombre.setText(test_name)
                            else:
                                self.updateLog("<b><Font=red>Error al modificar divisor</font></b>")
                        spliter=Spliter(dialog.Nombre.text())
                        spliter.entradas(dialog.Entradas)
                        spliter.salidas(dialog.Salidas)
                        del spliters[name]
                        spliters[dialog.Nombre.text()]=spliter
                        self.updateLog("Divisor: "+str(spliter.name)+" modificado")
                flag=False        
    
    def run_all(self):
        global streams

        self.updateLog("<b>Resolviendo.....</b>")
        go=True
        break_dic={"Error":2,"Unsolved":10,"Solved":0}
        c=0
        
        for i in variables:
             limites=streams[i].get_limits()
             flujo=limites[1]
             streams[i].Flujo=flujo
        ans=0
        iny=0
        ext=0
        ok=True
        try:
            for i in streams:
                if streams[i].Tipo=="Extraccion":
                    ext+=streams[i].Flujo
                if streams[i].Tipo=="Inyeccion":
                    iny+=streams[i].Flujo
                ans=iny-ext
            if ans>0.00000000001:
                self.updateLog("<font color=orange><b>WARNING</b></font>")
                self.updateLog("<font color=orange><b>El balance de oferta y demanda no es igual a cero</b></font>")
                self.updateLog("       Resultado de Oferta menos Demanda: "+str(ans))
                self.updateLog("       Demanda:"+str(ext))
                self.updateLog("       Oferfa:"+str(iny))
                self.updateLog("<b>Cálculo abortado, favor de corregir balance general</b>")
                ok=False
        except TypeError:
            ok=True
        if ok==True:
            while go==True:
                k=0
                j=0
                self.updateLog("<b>Iteración: "+str(c)+"</b>")
                for i in streams:
                    if streams[i].editable()==False:
                        if streams[i].critic!="variable":
                             streams[i].Flujo="x"
                for i in spliters:
                    spliters[i].status="Unsolved"
                QCoreApplication.processEvents()
                while(j<self.max_it):
                    QCoreApplication.processEvents()
                    status_lis=[]
                    if k==0:
                        QCoreApplication.processEvents()
                        self.updateLog("   Iteración número: "+str(j+1))
                    QCoreApplication.processEvents()    
                    for spliter in spliters:
                        if spliters[spliter].status!="Solved" and spliters[spliter].status!="Error":
                            self.solve_unique(spliter,self.tol)    
                    QCoreApplication.processEvents()            
                    for spliter in spliters:
                        status_lis.append(spliters[spliter].status)
                    QCoreApplication.processEvents()
                    if "Unsolved" in status_lis:
                        j+=1
                        if j==self.max_it-1:
                            QCoreApplication.processEvents()
                            self.updateLog("<font color=red><b>Se realizarón "+str(self.max_it)+" iteraciones. No fue posible resolver todos los nodos</b></font>")
                            self.updateLog("Estatus de los divisores:")
                            for spliter in spliters:
                                if spliters[spliter].status!="Solved":
                                    self.updateLog("Divisor: "+str(spliter)+" "+spliters[spliter].status)
                            j=self.max_it+break_dic["Unsolved"]
    
                    else:
    
                        QCoreApplication.processEvents()
                        
                        self.updateLog("<b>Se ha encontrado un posible resultado</b>")
                        self.updateLog("<b>Comprobando resultado...</b>")
                        error_lis=[]
                        for spliter in spliters:
                               inlets=[]
                               outlets=[]
                               for i in spliters[spliter].entradas:
                                   inlets.append(streams[i].Flujo)
                               for i in spliters[spliter].salidas:
                                   outlets.append(streams[i].Flujo)
                               ans_entradas=0
                               ans_salidas=0
                               
                               for i in inlets:
                                   ans_entradas+=i
                               for i in outlets:
                                   ans_salidas+=i
                               ans=ans_entradas-ans_salidas
                              
                               if abs(ans)>self.tol:
                                   spliters[spliter].status="Error"
                                   j=self.max_it+break_dic["Error"]
                                   error_lis.append(spliter)
                               QCoreApplication.processEvents()
                        if len(error_lis)!=0:
                            j=self.max_it+break_dic["Error"]
                            
                        if j!=self.max_it+break_dic["Error"]:
                            j=self.max_it+break_dic["Solved"]
                    QCoreApplication.processEvents()      
                
                
                result=j-self.max_it
                if len(variables)==0:     
                    if result==break_dic["Error"]:
                        if len(variables)==0:
                            self.updateLog("<b><font color=red>Error encontrado en:</b></font>")
                            for i in error_lis:
                                self.updateLog("    "+str(i))
                            if len(error_lis)>1:
                                self.updateLog("Realizando reset de corrientes debido a los errrores encontrados")
                            elif len(error_lis)==1:
                                self.updateLog("Realizando reset de corrientes debido al error encontrado")
                            self.resetf()
                if len(variables)>0:
                    if result==break_dic["Error"]:
                        self.updateLog("<b><font color=red>Se ha encontrado un error</b></font>")
                        error_lis=[]
                        for spliter in spliters:
                            a=spliters[spliter].status
                            if a=="Error":
                                error_lis.append(spliter)
                        self.updateLog("<b>Error econtrado en:</b>")
                        for i in error_lis:
                            self.updateLog("    "+str(i)) 
                        self.resetf()
                        go=False
                    elif result==break_dic["Unsolved"]:
                        self.updateLog("<b>No fue posible resolver el sistema de manera total. Favor de revisar grados de libertad</b>")
                        go=False
                    elif result==break_dic["Solved"]:
                        no_lis=[]    #Lista de corrientes que no cumplen con restriccion
                        for r in restricciones:
                            if abs(streams[r].Flujo)<streams[r].limits[0] or abs(streams[r].Flujo)>streams[r].limits[1]:
                                no_lis.append(r)
                        if len(no_lis)==0:
                            go=False
                            self.updateLog("<b><font color=green>Sistema resuelto en "+str(c+1)+" iteraciones</font></b>")
                        else:
                            QCoreApplication.processEvents()
                            if len(no_lis)>1:
                                self.updateLog("<b>Se han encontrado "+str(len(no_lis))+" corrientes que no cumplen con las restricciones")
                            else:
                                self.updateLog("<b>Se ha encontrado "+str(len(no_lis))+" corriente que no cumple con las restricciones")
                            def forward(var_a_modificar):
                                  global streams
                                  if streams[var_a_modificar].Flujo<0:
                                      flujo=(abs(streams[var_a_modificar].limits[1])-abs(streams[var_a_modificar].Flujo))/2-abs(streams[var_a_modificar].limits[1])
                                      flujo*=-1
                                  else:
                                      flujo=(streams[var_a_modificar].limits[1]-streams[var_a_modificar].Flujo)/2-streams[var_a_modificar].limits[1]
                                  if abs(flujo)>streams[var_a_modificar].limits[1]-0.5:
                                      QCoreApplication.processEvents()
                                      self.updateLog("<b><font color=red>No se encontro una solución que cumpla con las restricciones y los limites de las variables</font></b>")
                                      self.resetf()
                                      return True
                                  else:
                                      streams[var_a_modificar].Flujo=flujo
                                      
                                      
                            def backward(var_a_modificar):
                                   global streams
                                   if streams[var_a_modificar].Flujo<0:
                                       flujo=(abs(streams[var_a_modificar].Flujo)-abs(streams[var_a_modificar].limits[0]))/2+streams[var_a_modificar].limits[0]
                                       flujo*=-1
                                   else:
                                       flujo=(streams[var_a_modificar].Flujo-streams[var_a_modificar].limits[0])/2+streams[var_a_modificar].limits[0]
                                   if abs(flujo)<streams[var_a_modificar].limits[0]+0.5:
                                       QCoreApplication.processEvents()
                                       self.updateLog("<b><font color=red>No se encontro una solución que cumpla con las restricciones y los limites de las variables</font></b>")
                                       streams[var_a_modificar].Flujo="x"
                                       streams[r].Flujo="x"
                                       self.resetf()
                                       return True
                                   else:
                                       streams[var_a_modificar].Flujo=flujo
        
                            for i in no_lis:                           
                                var_a_modificar=restricciones[i][0]
                                dependencia=restricciones[i][1]
                                if type(streams[i].Flujo)!=str:
                                    if abs(streams[i].Flujo)>streams[i].limits[1]:
                                        if dependencia=="Positiva":         
                                            if backward(var_a_modificar):
                                                go=False
                                                break
                                        if dependencia=="Negativa": 
                                            if forward(var_a_modificar):
                                                go=False
                                                break
                                    if abs(streams[i].Flujo)<streams[i].limits[0]:                                
                                        if dependencia=="Positiva":                                    
                                            if forward(var_a_modificar):
                                                go=False
                                                break
                                        
                                        if dependencia=="Negativa":                                    
                                            if backward(var_a_modificar):
                                                go=False
                                                break
                                QCoreApplication.processEvents()    
                
                                        
                else:
                    QCoreApplication.processEvents()
                    if result==break_dic["Solved"]:
                        self.updateLog("<b><font color=green>Sistema resuelto en "+str(c+1)+" iteraciones</font></b>")
                    go=False
                c+=1
                if c>=10:
                    go=False
                    self.updateLog("No se ha podido resolver el sistema con las condiciones indicadas")
                       
        '''Update de tooltip'''
        for item in self.scene.items():
                name=self.get_itemName(item)     #Obtiene el nombre de la corriente en item
                for corriente in streams:
                    name_2=name.replace(" ","")
                    corriente_2=corriente.replace(" ","")
                    if name_2==corriente_2:
                        item.setToolTip("Nombre: "+corriente+"\n Flujo: "+str(streams[corriente].Flujo))
                                        
                        
    def importf(self):
        if self.filename=="":
            path="."
        else:
            path=self.filename.split("/")
            path=path[0:-1]
            path="/".join(path)
        fname=QFileDialog.getOpenFileName(self,"Balanceador - Open excel file",path,"Oferta y demanda(*.xlsx)")
        if fname[0]=="":
            return
        fname_log=fname[0].split("/")
        fname_log=fname_log[-1]
        fname_log_test="<Book ["+fname_log+"]>"
        self.updateLog("Importing data from: "+fname_log+".....")
        try:
            lis=[]
            for i in xw.books:
                lis.append(str(i))
            if fname_log_test in lis:
                wb=xw.books[fname_log]
            else:
                wb=xw.Book(fname[0])
        except:
            wb=xw.Book(fname[0])
        sheet=wb.sheets[0]
        #Ciclo para inyecciones
        try:
            filas=["A","E","I","M","Q"]
            for fila in filas:
                i=11
                b=sheet.range(fila+str(i)).value
                while(b!="TOTAL"):
                    excel_stream=sheet.range(fila+str(i)).value
                    if fila=="I":
                        excel_stream="Campo "+excel_stream
                    if fila=="M":
                        excel_stream="LNG "+excel_stream
                    if excel_stream in streams:
                        if streams[excel_stream].editable()==False:
                            streams[excel_stream].edit=True
                        if fila=="A":
                            valor=sheet.range("B"+str(i)).value
                        if fila=="E":
                            valor=sheet.range("F"+str(i)).value
                        if fila=="I":
                            valor=sheet.range("J"+str(i)).value
                        if fila=="M":
                            valor=sheet.range("N"+str(i)).value
                        if fila=="Q":
                            valor=sheet.range("R"+str(i)).value
                        try:
                            if valor!="":
                                streams[excel_stream].Flujo=float(valor)
                            else:
                                self.updateLog("<b> Corriente"+str(excel_stream)+" sin valor")
                        except:
                            self.updateLog("<b><font color=red>Error importando dato de "+str(excel_stream))
                        streams[excel_stream].Tipo="Inyeccion"
                    else:
                        self.updateLog("Corriente "+str(excel_stream)+" presente en excel pero no en la red")
                    i+=1
                    b=sheet.range(fila+str(i)).value
                    
            for fila in filas:
                
                i=1
                test=sheet.range("A"+str(i)).value
                while (test!="Nodo"):
                    test=sheet.range("A"+str(i)).value
                    i+=1
                
                b=sheet.range(fila+str(i)).value
                while(b!="TOTAL"):
                    excel_stream=sheet.range(fila+str(i)).value
                    if excel_stream in streams:
                        if streams[excel_stream].editable()==False:
                            streams[excel_stream].edit=True
                        if fila=="A":
                            valor=sheet.range("B"+str(i)).value
                        if fila=="E":
                            valor=sheet.range("F"+str(i)).value
                        if fila=="I":
                            valor=sheet.range("J"+str(i)).value
                        if fila=="M":
                            valor=sheet.range("N"+str(i)).value
                        if fila=="Q":
                            valor=sheet.range("R"+str(i)).value
                        try:
                            if valor!="":
                                streams[excel_stream].Flujo=float(valor)
                            else:
                                self.updateLog("<b> Corriente"+str(excel_stream)+" sin valor") 
                        except:
                            self.updateLog("<b><font color=red>Error importando dato de "+str(excel_stream))
                    else:
                        self.updateLog("Extracción "+str(excel_stream)+" encontrada en el excel pero no en la red")
                    i+=1
                    b=sheet.range(fila+str(i)).value
        except KeyError:
            pass
        for item in self.scene.items():
            if isinstance(item,QGraphicsPixmapItem):
               self.update_toolTip(item)             
        self.updateLog("Data imported")
        ans=0
        iny=0
        ext=0
        for i in streams:
            if streams[i].Tipo=="Extraccion":
                ext+=streams[i].Flujo
            if streams[i].Tipo=="Inyeccion":
                iny+=streams[i].Flujo
            ans=iny-ext
        if ans!=0:
            self.updateLog("<font color=orange><b>WARNING</b></font>")
            self.updateLog("<font color=orange><b>El balance de oferta y demanda no es igual a cero</b></font>")
            self.updateLog("       Resultado de Oferta menos Demanda: "+str(ans))
            self.updateLog("       Demanda:"+str(ext))
            self.updateLog("       Oferfa:"+str(iny))
            
    def update_toolTip(self,item):
        name=self.get_itemName(item)
        if name in streams:
            item.setToolTip("Nombre: "+name+"\n Flujo: "+str(streams[name].Flujo))
    
    
    def export(self):
        wb=xw.Book()
        sheet=wb.sheets[0]
        fila=2
        sheet.range(1,1).value="Corriente"
        sheet.range(1,2).value="Flujo(MMpcd)"
        self.updateLog("Exporting data to excel: "+".....")
        for i in streams:
            sheet.range((fila,1)).value=streams[i].name
            sheet.range((fila,2)).value=str(streams[i].Flujo)
            sheet.range((fila,3)).value=str(streams[i].Tipo)
            fila+=1
        self.updateLog("Data exported")
        
    '''---------------------------------------------------------------------------------------------------'''    
    '''-----------------Funciones de abrir y guardar-----------------------------------------------------'''
    
    def save(self):
        if self.filename=="":
            path="."
            fname=QFileDialog.getSaveFileName(self,"Balanceador - Save as",path,"Balanceador Files(*.pgd)")
            if fname[0]=="":
                return
            self.filename=fname[0]
        self.save_f()
        
    def save_f(self):
        fh=None
        try:
            fh=QFile(self.filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError #str(fh.errorString())
            name=self.filename
            name=name.split("/")
            name=name[-1]
            self.updateLog("Saving file.... "+str(name))
            self.setWindowTitle("Balanceador del Sistrangas----"+name)
            self.scene.clearSelection()
            qstream=QDataStream(fh)
            qstream.setVersion(QDataStream.Qt_4_2)
            qstream.writeInt(len(spliters))
            qstream.writeInt(len(streams))
            
            #Guardado de keys
            for i in sorted(spliters.keys()):
                key=str(i)
                qstream.writeQString(key)
            for i in sorted(streams.keys()):
                key=str(i)
                qstream.writeQString(key)  
                        
            #Guardado status de spliters
            for i in sorted(spliters.keys()):
                status=str(spliters[i].status)
                qstream.writeQString(status)
            
            #Guardado de entradas y salidas de spliters
            for i in sorted(spliters.keys()):
                qstream.writeInt(len(spliters[i].entradas))
                for j in spliters[i].entradas:
                    qstream.writeQString(str(j))
                qstream.writeInt(len(spliters[i].salidas))
                for j in spliters[i].salidas:
                    qstream.writeQString(str(j))
                for item in self.scene.items():
                    name=self.get_itemName(item)
                    if str(name)==str(spliters[i].name):
                        spliters[i].Pos=item.pos()
                        qstream << spliters[i].Pos            
            

            #Guardado de info de streams
            for i in sorted(streams.keys()):
                qstream.writeQString(str(streams[i].name))
                qstream.writeQString(str(streams[i].editable()))
                qstream.writeQString(str(streams[i].Flujo))
                qstream.writeQString(str(streams[i].Tipo))
                qstream.writeQString(str(streams[i].is_critic()))
                qstream.writeQString(str(streams[i].get_limits()[0]))
                qstream.writeQString(str(streams[i].get_limits()[1]))
                qstream.writeQString(str(streams[i].is_fixed()))
                qstream.writeQString(str(streams[i].dependencia))
                qstream.writeQString(str(streams[i].funcion_de))
                for item in self.scene.items():
                    name=self.get_itemName(item)
                    if str(name)==str(streams[i].name):
                        streams[i].Pos=item.pos()
                        qstream << streams[i].Pos  
            
            #QStream para items
            len_graphics=0
            for item in self.scene.items():
                if isinstance(item,QGraphicsPixmapItem):
                    len_graphics+=1      
            
            qstream.writeQString(str(len_graphics))
            for item in self.scene.items():
                self.writeItemToStream_graphics(qstream,item)
            
            for item in self.scene.items():
                self.writeItemToStream_Text(qstream,item)
                
            self.updateLog("Saved")
        except IOError:
            QMessageBox.warning(self,"Balanceador --- Save Error","Failed to save %s: %s"%(self.filename))
        finally:
            if fh is not None:
                fh.close()

    def writeItemToStream_Text(self,qstream,item):
        if isinstance(item,QGraphicsTextItem):
            qstream.writeQString(item.toPlainText())
            angle=item.rotation()
            qstream.writeInt(angle)
            qstream<<item.pos()<<item.font()
    
    def writeItemToStream_graphics(self,qstream,item):   
        if isinstance(item,QGraphicsPixmapItem):
            name=self.get_itemName(item)
            if name in spliters:
                tipo="Divisor"
            elif name in streams:
                tipo=streams[name].Tipo
            qstream.writeQString(tipo)
            angle=item.rotation()
            qstream.writeInt(angle)
            qstream << item.pos() <<item.pixmap()
        
            
            
    def Open(self):
        path=QFileInfo(self.filename).path() \
        if not self.filename=="" else "."
        fname=QFileDialog.getOpenFileName(self,"Balanceador - Open",path,"Balanceador Files(*.pgd)")
        if fname[0]=="":
            return
        self.filename=fname[0]
        name=self.filename
        name=name.split("/")
        name=name[-1]
        self.updateLog("Loading file....  "+str(name))
        self.setWindowTitle("Balanceador del Sistranags-----"+str(name))
        fh=None
        global spliters
        global streams
        global variables
        global restricciones
        spliters={}
        streams={}
        variables=[]
        restricciones={}
        try:
            fh=QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError
            items=self.scene.items()
            while items:
                item=items.pop()
                self.scene.removeItem(item)
                del item
            qstream=QDataStream(fh)
            qstream.setVersion(QDataStream.Qt_4_2)

            len_spliters=0
            len_streams=0
            key=""
            
            len_spliters=qstream.readInt()
            len_streams=qstream.readInt()
            keys_spliters=[]
            keys_streams=[]
            
            for i in range(0,len_spliters):
                key=qstream.readQString()
                keys_spliters.append(key)
            
            for i in range(0,len_streams):
                key=qstream.readQString()
                keys_streams.append(key)
                

            #Parentesis, creación de corrientes y spliters en global dictionaries
            for spliter in keys_spliters:
                spliter_i=Spliter(spliter)
                spliters[spliter]=spliter_i
            for stream in keys_streams:
                stream_i=Stream(stream)
                streams[stream]=stream_i
            
            #Continua carga de datos from qstream
            
            for i in keys_spliters:
                status=qstream.readQString()
                spliters[i].status=status
            
            for i in keys_spliters:
                len_entradas=qstream.readInt()
                spliters[i].entradas=[]
                spliters[i].salidas=[]
                for j in range(0,len_entradas):
                    entrada=qstream.readQString()
                    spliters[i].entradas.append(entrada)
                len_salidas=qstream.readInt()
                for j in range(0,len_salidas):
                    salida=qstream.readQString()
                    spliters[i].salidas.append(salida)
                position=QPointF()
                qstream >> position
                spliters[i].Pos=position
                

            for i in keys_streams:
                streams[i].name=qstream.readQString()
                streams[i].edit=qstream.readQString()
                streams[i].Flujo=qstream.readQString()
                try:
                    streams[i].Flujo=float(streams[i].Flujo)
                except:
                    streams[i].Flujo=str(streams[i].Flujo)
                streams[i].Tipo=qstream.readQString()
                state=qstream.readQString()
                if state=="False":
                    state=False
                elif state=="True":
                    state=True
                streams[i].critic=state
                minimo=qstream.readQString()
                maximo=qstream.readQString()
                fixed=qstream.readQString()
                dependencia=qstream.readQString()
                funcion_de=qstream.readQString()
                try:
                    minimo=float(minimo)
                    maximo=float(maximo)
                except:
                    pass
                streams[i].limits=(minimo,maximo)
                if fixed=="True":
                    fixed=True
                if fixed=="False":
                    fixed=False
                streams[i].fixed=fixed
                streams[i].dependencia=dependencia
                streams[i].funcion_de=funcion_de
                position=QPointF()
                qstream >> position
                streams[i].Pos=position

            len_items=qstream.readQString()
            len_items=int(len_items)
            for i in range(0,len_items):
                self.readItemFromStream(qstream)
            
            while not fh.atEnd():
                self.readTextFromStream(qstream)
            
            #Seting tooltips
            
            for item in self.scene.items():
                scene_pos=item.pos()
                for stream in streams:
                    if scene_pos==streams[stream].Pos:
                        item.setToolTip("Nombre: "+streams[stream].name+"\n Flujo: "+str(streams[stream].Flujo))
                for spliter in spliters:
                    if scene_pos==spliters[spliter].Pos:
                        item.setToolTip("Nombre: "+''+str(spliters[spliter].name))
            
            for stream in streams:
                if streams[stream].editable()=="True":
                    streams[stream].edit=True
                if streams[stream].editable()=="False":
                    streams[stream].edit=False
                    
            #Añadiendo corrientes a variables y restricciones
            for stream in streams:
                if streams[stream].is_critic()=="variable":
                    variables.append(stream)
                elif streams[stream].is_critic()=="restriccion":
                    restricciones[stream]=[streams[stream].funcion_de,streams[stream].dependencia]
            
            
            self.marco()
        except IOError:
            QMessageBox.warning(self,"Balanceador -- Open Error","Failed to open "+str(self.filename)) 
        finally:
            if fh is not None:
                fh.close()
        self.updateLog("Loaded!")
        
    def readTextFromStream(self,qstream):
        text=""
        font=QFont()
        position=QPointF()
        text=qstream.readQString()
        angle=qstream.readInt()
        qstream>>position>>font
        item=TextItem(text,position,self.scene,font)
        item.setRotation(angle)
        
    def readItemFromStream(self,qstream):
        tipo=qstream.readQString()
        if tipo!="Pass" and tipo!="":
            position=QPointF()
            pixmap=QPixmap()
            angle=qstream.readInt()
            qstream >> position >> pixmap
            self.drawItemFromStream(pixmap,position,tipo,angle)
        
    def drawItemFromStream(self,pixmap,position,tipo,angle):      
        item=graphic_object()
        pixmap_in=QPixmap(pixmap)
        if tipo!="Divisor":
            item.setPixmap(pixmap_in.scaled(200,100))
        else:
            item.setPixmap(pixmap_in.scaled(200,200))
        item.setPos(position)
        item.setRotation(angle)
        self.scene.clearSelection()
        self.scene.addItem(item)
        item.setSelected(True)
        
    def new_file(self):
        self.filename=""
        self.setWindowTitle("Balanceador del Sistrangas-----")
        self.updateLog("New file created")
        global streams
        global spliters
        streams={}
        spliters={}
        items=self.scene.items()
        while items:
                item=items.pop()
                self.scene.removeItem(item)
                del item
        self.marco()
        
    def save_as(self):
        path="."
        fname=QFileDialog.getSaveFileName(self,"Balanceador - Save as",path,"Balanceador Files(*.pgd)")
        if fname[0]=="":
            return
        self.filename=fname[0]
        self.save_f()
    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Delete:
            print("Exterminate!")
            self.delete_item()


'''---------Invocación de main frame-----'''   
if not QApplication.instance():
     app=QApplication(sys.argv)
else:
    app=QApplication.instance()
app.setOrganizationName("Cenagas")
#app.setApplicationName("Balance de materia SISTRANGAS")
form=MainWindow()
rect=QApplication.desktop().availableGeometry()
form.resize(float(rect.width()),float(rect.height()*0.9))
form.show()
app.exec_()
