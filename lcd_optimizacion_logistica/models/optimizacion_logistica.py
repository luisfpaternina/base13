# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.website.models import ir_http

_logger = logging.getLogger(__name__)


class OptimizacionLogistica(models.Model):
    _name = 'optimizacion.logistica'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Optimización Logística'

    name=fields.Char('Número')
    fechas_fabricacion=fields.Char('Fechas de Fabricación',required=True)
    fechas_entrega=fields.Char('Fechas de Entrega',required=True)
    estado=fields.Selection([('borrador','Borrador'),('optimizado','Optimizado'),('cancelado','Cancelado')],'Estado',default='borrador',tracking=True)
    items=fields.One2many('optimizacion.logistica.detalle','optimizacion_id','Items')
    totales_categ=fields.One2many('optimizacion.logistica.detalle_categ','optimizacion_id','Totales X Categoría')
    totales_prod=fields.One2many('optimizacion.logistica.detalle_prod','optimizacion_id','Totales X Producto')
    capacidad_excedida=fields.Boolean('Capacidad excedida')
    warnings=fields.Text('Advertencias',compute='onchange_items')
    rutas_ids=fields.One2many('lcd.rutas_horarios','optimizacion_id','Rutas')

    @api.model
    def create(self, vals):
        #Chequeo que la cantidad de dias de fabricacion sean igual a la cantidad de dias de entrega
        fechas_fab=vals['fechas_fabricacion'].split(',')
        fechas_ent=vals['fechas_entrega'].split(',')
        if len(fechas_fab)!=len(fechas_ent):
            raise UserError('La cantidad de días de fecha de entrega debe ser igual a la cantidad de días de fecha de fabricación')
        #Chequeo que las fechas no esten ocupadas en otra optimizacion
        for fecha in fechas_fab:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_fabricacion ilike '%"+fecha+"%'")
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de fabricación "'+fecha+'" ya se encuentra ocupada en otra optimización')
        for fecha in fechas_ent:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_entrega ilike '%"+fecha+"%'")
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de entrega "'+fecha+'" ya se encuentra ocupada en otra optimización')
        #Asigno nombre por secuencia
        vals['name']=self.env['ir.sequence'].next_by_code('optimizacion.logistica')
        return super(OptimizacionLogistica, self).create(vals)

    def write(self, vals):
        res = super(OptimizacionLogistica, self).write(vals)
        #Chequeo que la cantidad de dias de fabricacion sean igual a la cantidad de dias de entrega
        fechas_fab=self.fechas_fabricacion.split(',')
        fechas_ent=self.fechas_entrega.split(',')
        if len(fechas_fab)!=len(fechas_ent):
            raise UserError('La cantidad de días de fecha de entrega debe ser igual a la cantidad de días de fecha de fabricación')
        #Chequeo que las fechas no esten ocupadas en otra optimizacion
        for fecha in fechas_fab:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_fabricacion ilike '%"+fecha+"%' and id<>"+str(self.id))
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de fabricación "'+fecha+'" ya se encuentra ocupada en otra optimización')
        for fecha in fechas_ent:
            self.env.cr.execute("select count(1) from optimizacion_logistica where fechas_entrega ilike '%"+fecha+"%' and id<>"+str(self.id))
            res=self.env.cr.fetchall()
            if res[0][0]!=0:
                raise UserError('La fecha de entrega "'+fecha+'" ya se encuentra ocupada en otra optimización')
        return res

    #en base a una fecha, devuelve la siguente fecha de fabricación si tipo es 0 y devuelve la siguente fecha de entrega si tipo es 1
    def get_next_fecha(self,fecha,tipo):
        if tipo==0:
            fechas=self.fechas_fabricacion.split(',')
        else:
            fechas=self.fechas_entrega.split(',')
        index=0
        total_fechas=len(fechas)
        while index<(total_fechas-1):
            if fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5]==fecha:
                return fechas[index+1][-4:]+"-"+fechas[index+1][:2]+"-"+fechas[index+1][3:-5]
            index+=1
        return False

    #en base a una fecha de fabricación, devuelve la fecha de entrega correspondiente
    def get_fecha_correlativa(self,fecha):
        fechas=self.fechas_fabricacion.split(',')
        fechas_correl=self.fechas_entrega.split(',')
        index=0
        total_fechas=len(fechas)
        while index<=(total_fechas-1):
            print('index:',index)
            print('fecha:',fecha)
            print('fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5]:',fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5])
            if fechas[index][-4:]+"-"+fechas[index][:2]+"-"+fechas[index][3:-5]==fecha:
                print('return:',fechas_correl[index][-4:]+"-"+fechas_correl[index][:2]+"-"+fechas_correl[index][3:-5])
                return fechas_correl[index][-4:]+"-"+fechas_correl[index][:2]+"-"+fechas_correl[index][3:-5]
            index+=1
        return False

    def procesar_lista(self,lista,fechas_fab,fechas_ent,dict_categ,categorias_cant):
        #lista= lista de items a optimizar (0:id_bolsadet, 1:categoria prod, 2:cantidad_a_fabricar(cant-cant_a_realizar), 3:fabricable si-no, 4:mayorista si-no)
        #fechas_fab= lista de fechas de fabricacion
        #fechas_ent= lista de fechas de entrega
        #dict_categ= Contiene un dict con el id de la categoría y una lista con: 1- su capacidad maxima de fabricación 2- su capacidad maximo según el porcentaje mayorista
        #categorias_cant= Contiene un dict con el id de la categoría y: 1- la cantidad actual que se va completando para optimizar 2- cantidad mayorista que se va completando, 3- fecha de fabricacion
        fechas_fab
        optimizar=True
        lista_remanente=[]
        print('lista:',lista)
        lineas_a_optimizar=[]
        while optimizar==True:
            #Voy guardando el remanente en lista_aux
            lista_aux=[]
            for linea in lista:
                print('#########################')
                print('#########################')
                print('linea:',linea)
                #Guardo items de lista en variables
                id_bolsadet=linea[0]
                categoria=linea[1]
                cantidad_a_fabricar_linea=linea[2]
                fabricable=linea[3]
                mayorista=linea[4]
                #Defino variables generales
                cantidad_fabricada_categ=categorias_cant[categoria][0]
                cantidad_fabricada_categ_mayorista=categorias_cant[categoria][1]
                cantidad_tope=dict_categ[categoria][0]
                cantidad_tope_mayorista=dict_categ[categoria][1]
                #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no. Si se completó, avanzo a la proxima fecha de fabricación
                if cantidad_tope==cantidad_fabricada_categ:
                    #Es igual ==> Avanzo de fecha de fabricación y de entrega
                    fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                    print('nueva fecha_de_fabricacion:',fecha_de_fabricacion)
                    #Cambio fecha y reseteo contador de capacidad
                    categorias_cant[categoria][0]=0
                    categorias_cant[categoria][1]=0
                    categorias_cant[categoria][2]=fecha_de_fabricacion
                    cantidad_fabricada_categ=0
                    cantidad_fabricada_categ_mayorista=0
                    print('cantidad_fabricada_categ:',cantidad_fabricada_categ)
                    print('cantidad_fabricada_categ_mayorista:',cantidad_fabricada_categ_mayorista)
                    print('fecha_de_fabricacion:',fecha_de_fabricacion)
                    print('cantidad_tope:',cantidad_tope)
                    print('cantidad_tope_mayorista:',cantidad_tope_mayorista)

                else:
                    fecha_de_fabricacion=categorias_cant[categoria][2]
                    print('####entro por else')
                    print('cantidad_fabricada_categ:',cantidad_fabricada_categ)
                    print('cantidad_fabricada_categ_mayorista:',cantidad_fabricada_categ_mayorista)
                    print('fecha_de_fabricacion:',fecha_de_fabricacion)
                    print('cantidad_tope:',cantidad_tope)
                    print('cantidad_tope_mayorista:',cantidad_tope_mayorista)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
                print('ffffffffffffffffffffffffffffffffffffffff')
                print('fecha_de_entrega:',fecha_de_entrega)
                print('ffffffffffffffffffffffffffffffffffffffff')
                #Si no es fabricable entra pero no tiene fabricación
                if fabricable==False:
                    lineas_a_optimizar.append((id_bolsadet,cantidad_a_fabricar_linea,fabricable,False,fecha_de_entrega))
                    continue
                if mayorista==True:
                    #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
                    if cantidad_a_fabricar_linea>cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista:
                        #La cantidad mayorista de la linea excede la capacidad mayorista permitida de la categoria, completo hasta la cantidad límite y el remanente lo dejo al final para ver si es posible meterla en la optimizacion
                        lineas_a_optimizar.append((id_bolsadet,cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista, fabricable, fecha_de_fabricacion, fecha_de_entrega))
                        #Si es que hay remanente sin optimizar lo cargo en el remanente para ser procesado en otra instancia
                        if cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista)>0:
                            lista_remanente.append((id_bolsadet,categoria,cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista), fabricable, mayorista))
                        #actualizo cant por fabricar y cant por fabricar mayorista
                        categorias_cant[categoria][0]=categorias_cant[categoria][0]+cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista
                        categorias_cant[categoria][1]=categorias_cant[categoria][1]+cantidad_tope_mayorista-cantidad_fabricada_categ_mayorista
                    else:
                        #La cantidad mayorista de la linea no excede la capacidad diaria mayorista permitida de la categoria, agrego toda la linea
                        lineas_a_optimizar.append((id_bolsadet,cantidad_a_fabricar_linea,fabricable,fecha_de_fabricacion,fecha_de_entrega))
                        #actualizo cant por fabricar y cant por fabricar mayorista
                        categorias_cant[categoria][0]=categorias_cant[categoria][0]+cantidad_a_fabricar_linea
                        categorias_cant[categoria][1]=categorias_cant[categoria][1]+cantidad_a_fabricar_linea
                #Si la cantidad de la linea excede el límite diario de fabricación, optimizo al maximo posible
                elif cantidad_a_fabricar_linea>cantidad_tope-cantidad_fabricada_categ:
                    lineas_a_optimizar.append((id_bolsadet,cantidad_tope-cantidad_fabricada_categ,fabricable,fecha_de_fabricacion,fecha_de_entrega))
                    categorias_cant[categoria][0]=categorias_cant[categoria][0]+(cantidad_tope-cantidad_fabricada_categ)
                    #Si es que hay remanente sin optimizar lo cargo en lineas_pendientes
                    if cantidad_a_fabricar_linea-(cantidad_tope-cantidad_fabricada_categ)>0:
                        lista_aux.append((id_bolsadet,categoria,cantidad_a_fabricar_linea-(cantidad_tope-cantidad_fabricada_categ), fabricable, mayorista))
                else:
                    #La cantidad de la linea no excede el límite diario de fabricación, optimizo toda la linea
                    lineas_a_optimizar.append((id_bolsadet,cantidad_a_fabricar_linea, fabricable, fecha_de_fabricacion,fecha_de_entrega))
                    categorias_cant[categoria][0]=categorias_cant[categoria][0]+(cantidad_a_fabricar_linea)
                print('lista_aux:',lista_aux)
            #Ahora chequeo si hay que seguir optimizando
            optimizar=False
            for linea in lista_aux:
                #Defino variables generales
                categoria=linea[1]
                mayorista=linea[4]
                fecha_de_fabricacion=categorias_cant[categoria][2]
                #Si tiene otra fecha para fabricar puedo seguir optimizando
                if fecha_de_fabricacion!=False:
                    optimizar=True
                    break
            lista=lista_aux
        #Terminé de optimizar, devuelvo listados
        print('lineas_a_optimizar:',lineas_a_optimizar)
        return lineas_a_optimizar,lista_remanente, categorias_cant

    def cargar_optimizacion(self):
        self.items.unlink()
        #Defino % mayorista
        porcentaje_mayoristas=self.env['ir.config_parameter'].search([('key','=','optimizacion.maximo_fabricacion_mayoristas')])
        if not porcentaje_mayoristas:
            raise UserError('Es necesario definir un porcentaje de distribución Mayoristas')
        porcentaje_mayoristas=porcentaje_mayoristas.value
        #Preparo listado de fechas de entrega y de fabricacion
        fechas_ent=self.fechas_entrega.split(',')
        fechas_fab=self.fechas_fabricacion.split(',')
        #Armo un diccionario de categorias con sus capacidades de fabricacion
        categorias=self.env['product.category'].search([]).read(['id','capacidad_fabricacion'])
        #dict_categ Contiene un diccionario con el id de la categoría y una lista con: 1- su capacidad maxima de fabricación 2- su capacidad maximo según el porcentaje mayorista
        #categorias_cant Contiene un diccionario con el id de la categoría y: 1- la cantidad actual que se va completando para optimizar 2- cantidad mayorista que se va completando, 3- fecha de fabricacion        
        dict_categ={}
        categorias_cant={}
        for item in categorias:
            dict_categ[item['id']]=[item['capacidad_fabricacion'],round(float(item['capacidad_fabricacion'])*float(porcentaje_mayoristas)/100),0]
            categorias_cant[item['id']]=[0,0,fechas_fab[0][-4:]+"-"+fechas_fab[0][:2]+"-"+fechas_fab[0][3:-5]]
        lista_prioridad_maxima=[]
        lista_sin_prioridad=[]
        fechas_string=""
        for item in fechas_ent:
            fechas_string+="'"+item[-4:]+item[:2]+item[3:-5]+"',"
        fechas_string=fechas_string[:-1]
        #Son de prioridad máxima aquellas lineas cuya fecha cierta coincida con la fecha de entrega seleccionada
        #Son de prioridad máxima aquellas lineas cuya fecha de entrega de pedido llega a los dias maximos por canal de venta de entrega
        consulta_max="select bvd.id,bvd.categ_id,bvd.cantidad-bvd.cantidad_realizada, bvd.fabricar, bvd.mayorista from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and (bvd.fecha_cierta in ("+fechas_string+") or bvd.fecha_canal_venta in ("+fechas_string+")) order by bv.fecha, bvd.fabricar nulls first"
        self.env.cr.execute(consulta_max)
        ids=''
        lineas_a_optimizar=[]
        for item in self.env.cr.fetchall():
            print('item:',item)
            #si no es fabricable lo agrego como optimizado y directamente para el primer dia de entrega
  #          if item[3]==False:
 #               lineas_a_optimizar.append((item[0],item[2],item[3],False,self.get_fecha_correlativa(categorias_cant[item[1]][2])))
#            else:
            lista_prioridad_maxima.append((item[0],item[1],item[2],item[3],item[4]))
            ids+=str(item[0])+','
        print('ids:',ids)
        #El resto de los items que no están en la lista de prioridad se ordenan por fecha mas vieja
        if ids=='':
            consulta="select bvd.id,bvd.categ_id,bvd.cantidad-bvd.cantidad_realizada, bvd.fabricar, bvd.mayorista from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad order by bv.fecha, bvd.fabricar nulls first"
        else:
            consulta="select bvd.id,bvd.categ_id,bvd.cantidad-bvd.cantidad_realizada, bvd.fabricar, bvd.mayorista from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and bvd.id not in ("+ids[:-1]+") order by bv.fecha, bvd.fabricar nulls first"
        self.env.cr.execute(consulta)
        for item in self.env.cr.fetchall():
            #si no es fabricable lo agrego como optimizado y directamente para el primer dia de entrega
     #       if item[3]==False:
    #            lineas_a_optimizar.append((item[0],item[2],item[3],False,self.get_fecha_correlativa(categorias_cant[item[1]][2])))
   #         else:
            lista_sin_prioridad.append((item[0],item[1],item[2],item[3],item[4]))
        ###################################################################################################################################
        ######Proceso primero la lista de prioridad maxima, luego la lista sin prioridad y al final el remanente que quedó sin optimizar
        ###################################################################################################################################
        ##########procesar_lista devuelve las lineas_a_optimizar, una lista de lineas sin optimizar y el diccionario categorias_cant que tiene la capacidad restante de fabricación
        lineas_sin_optimizar=[]
        lista1,lista2,categorias_cant=self.procesar_lista(lista_prioridad_maxima,fechas_fab,fechas_ent,dict_categ,categorias_cant)
        lineas_a_optimizar=lineas_a_optimizar+lista1
        lineas_sin_optimizar=lineas_sin_optimizar+lista2
        lista1,lista2,categorias_cant=self.procesar_lista(lista_sin_prioridad,fechas_fab,fechas_ent,dict_categ,categorias_cant)
        lineas_a_optimizar=lineas_a_optimizar+lista1
        lineas_sin_optimizar=lineas_sin_optimizar+lista2
        lista1,lista2,categorias_cant=self.procesar_lista(lineas_sin_optimizar,fechas_fab,fechas_ent,dict_categ,categorias_cant)
        lineas_a_optimizar=lineas_a_optimizar+lista1
        #####################################################################
        for linea in lineas_a_optimizar:
            self.env['optimizacion.logistica.detalle'].create({'optimizacion_id':self.id, 'bolsa_line_id':linea[0], 'cantidad_a_realizar':linea[1],'fabricar':linea[2], 'fecha_fabricacion':linea[3], 'fecha_entrega':linea[4], 'estado':'borrador'})
            bolsa_det=self.env['bolsa.ventas.detalle'].browse(linea[0])
            bolsa_det.write({'cantidad_a_realizar':bolsa_det.cantidad_a_realizar+linea[1]})
        self.onchange_items()

    def cargar_optimizacion_old(self):
        self.items.unlink()
        lista_prioridad_maxima=[]
        lista_sin_prioridad=[]
        producto_fabricable=self.env.ref('mrp.route_warehouse0_manufacture').id
        fechas_ent=self.fechas_entrega.split(',')
        fechas_fab=self.fechas_fabricacion.split(',')
        fechas_string=""
        for item in fechas_ent:
            fechas_string+="'"+item[-4:]+item[:2]+item[3:-5]+"',"
        fechas_string=fechas_string[:-1]
        #Son de prioridad máxima aquellas lineas cuya fecha cierta coincida con la fecha de entrega seleccionada
        #Son de prioridad máxima aquellas lineas cuya fecha de entrega de pedido llega a los dias maximos por canal de venta de entrega
        consulta_max="select bvd.id from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and (bvd.fecha_cierta in ("+fechas_string+") or bvd.fecha_canal_venta in ("+fechas_string+")) order by bv.fecha"
        self.env.cr.execute(consulta_max)
        for item in self.env.cr.fetchall():
            lista_prioridad_maxima.append(item[0])
#        lista_prioridad_maxima+=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('fecha_cierta','in',fechas_ent),('cantidad_a_realizar','<','cantidad')], order='bolsa_id.fecha').ids
#        lista_prioridad_maxima+=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('fecha_canal_venta','in',fechas_ent),('cantidad_a_realizar','<','cantidad'),('id','not in', lista_prioridad_maxima)],order='bolsa_id.fecha').ids
        consulta="select bvd.id from bolsa_ventas_detalle bvd inner join bolsa_ventas bv on bvd.bolsa_id=bv.id where bvd.estado in ('pendiente','en_proceso') and bvd.cantidad_a_realizar<bvd.cantidad and bvd.id not in ("+consulta_max+") order by bv.fecha"
#        lista_sin_prioridad=self.env['bolsa.ventas.detalle'].search([('estado','in',['pendiente','en_proceso']),('cantidad_a_realizar','<','cantidad'),('id','not in', lista_prioridad_maxima)], order='bolsa_id.fecha').ids
        self.env.cr.execute(consulta)
        for item in self.env.cr.fetchall():
            lista_sin_prioridad.append(item[0])
        porcentaje_mayoristas=self.env['ir.config_parameter'].search([('key','=','optimizacion.maximo_fabricacion_mayoristas')])
        if not porcentaje_mayoristas:
            raise UserError('Es necesario definir un porcentaje de distribución Mayoristas')
        porcentaje_mayoristas=porcentaje_mayoristas.value
        #Armo un diccionario de categorias con sus capacidades de fabricacion
        categorias=self.env['product.category'].search([]).read(['id','capacidad_fabricacion'])
        #dict_categ Contiene un diccionario con el id de la categoría y una lista con: 1- su capacidad maxima de fabricación 2- su capacidad maximo según el porcentaje mayorista
        dict_categ={}
        #categorias_cant Contiene un diccionario con el id de la categoría y: 1- la cantidad actual que se va completando para optimizar 2- cantidad mayorista que se va completando, 3- fecha de fabricacion
        categorias_cant={}
        for item in categorias:
            dict_categ[item['id']]=[item['capacidad_fabricacion'],round(float(item['capacidad_fabricacion'])*float(porcentaje_mayoristas)/100),0]
            categorias_cant[item['id']]=[0,0,fechas_fab[0][-4:]+"-"+fechas_fab[0][:2]+"-"+fechas_fab[0][3:-5]]
        #####################################################################
        #lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no)
        lineas_a_optimizar=[]
        #lineas_pendientes lista de (id bolsa detalle,cant remanente,categoria,indice)
        lineas_pendientes=[]
        #Pongo en lineas_a_optimizar las que tienen prioridad primero y despues las que tienen menor prioridad, llevo al limite de la capacidad si es que está por excederla
        indice=0
        fin_optimizacion=False
        for linea in self.env['bolsa.ventas.detalle'].browse(lista_prioridad_maxima):
            cantidad_por_fabricar=categorias_cant[linea.product_id.categ_id.id][0]
            cantidad_por_fabricar_mayorista=categorias_cant[linea.product_id.categ_id.id][1]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
            cantidad_a_fabricar_linea=linea.cantidad-linea.cantidad_a_realizar
            cantidad_tope=dict_categ[linea.product_id.categ_id.id][0]
            cantidad_tope_mayorista=dict_categ[linea.product_id.categ_id.id][1]
            print('cantidad_tope:',cantidad_tope)
            print('cantidad_por_fabricar:',cantidad_por_fabricar)
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                print('ES igual')
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
                print('fecha_de_fabricacion:',fecha_de_fabricacion)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea.product_id.categ_id.id][0]=0
                categorias_cant[linea.product_id.categ_id.id][1]=0
                categorias_cant[linea.product_id.categ_id.id][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
                cantidad_por_fabricar_mayorista=0
            #Si tiene cantidad tope=0 entra pero no tiene fabricacion
            if linea.product_id.route_ids ==False or (producto_fabricable not in linea.product_id.route_ids.ids):
                lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,False,False,fecha_de_entrega))
                continue
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea.mayorista==True:
                if cantidad_a_fabricar_linea>cantidad_tope_mayorista-cantidad_por_fabricar_mayorista:
                    #La cantidad mayorista de la linea excede la capacidad mayorista permitida de la categoria, completo hasta la cantidad límite y el remanente lo dejo al final para ver si es posible meterla en la optimizacion
                    lineas_a_optimizar.append((linea.id,cantidad_tope_mayorista-cantidad_por_fabricar_mayorista,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion,fecha_de_entrega))
                    #Si es que hay remanente sin optimizar lo cargo en lineas_pendientes
                    if cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista)>0:
                        lineas_pendientes.append((linea.id,cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista), linea.product_id.categ_id.id, indice))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                else:
                    #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                    lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion,fecha_de_entrega))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_a_fabricar_linea
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_a_fabricar_linea
            #Si la cantidad de la linea excede el límite de fabricación, optimizo al maximo posible
            elif cantidad_a_fabricar_linea>cantidad_tope-cantidad_por_fabricar:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(cantidad_tope-cantidad_por_fabricar)
                lineas_a_optimizar.append((linea.id,cantidad_tope-cantidad_por_fabricar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion,fecha_de_entrega))
            else:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(linea.cantidad-linea.cantidad_a_realizar)
                lineas_a_optimizar.append((linea.id,linea.cantidad-linea.cantidad_a_realizar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True, fecha_de_fabricacion, fecha_de_entrega))
            indice+=1
        #Pongo en lineas_a_optimizar las que tienen menor prioridad
        for linea in self.env['bolsa.ventas.detalle'].browse(lista_sin_prioridad):
            cantidad_por_fabricar=categorias_cant[linea.product_id.categ_id.id][0]
            cantidad_por_fabricar_mayorista=categorias_cant[linea.product_id.categ_id.id][1]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
            cantidad_a_fabricar_linea=linea.cantidad-linea.cantidad_a_realizar
            cantidad_tope=dict_categ[linea.product_id.categ_id.id][0]
            cantidad_tope_mayorista=dict_categ[linea.product_id.categ_id.id][1]
            print('cantidad_tope:',cantidad_tope)
            print('cantidad_por_fabricar:',cantidad_por_fabricar)
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                print('ES igual')
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
                print('fecha_de_fabricacion:',fecha_de_fabricacion)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea.product_id.categ_id.id][0]=0
                categorias_cant[linea.product_id.categ_id.id][1]=0
                categorias_cant[linea.product_id.categ_id.id][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
                cantidad_por_fabricar_mayorista=0
            #Si tiene cantidad tope=0 entra pero no tiene fabricacion
            if linea.product_id.route_ids ==False or (producto_fabricable not in linea.product_id.route_ids.ids):
                lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,False,False,fecha_de_entrega))
                continue
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea.mayorista==True:
                if cantidad_a_fabricar_linea>cantidad_tope_mayorista-cantidad_por_fabricar_mayorista:
                    #La cantidad mayorista de la linea excede la capacidad mayorista permitida de la categoria, completo hasta la cantidad límite y el remanente lo dejo al final para ver si es posible meterla en la optimizacion
                    lineas_a_optimizar.append((linea.id,cantidad_tope_mayorista-cantidad_por_fabricar_mayorista, cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista, True, fecha_de_fabricacion, fecha_de_entrega))
                    #Si es que hay remanente sin optimizar lo cargo en lineas_pendientes
                    if cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista)>0:
                        lineas_pendientes.append((linea.id,cantidad_a_fabricar_linea-(cantidad_tope_mayorista-cantidad_por_fabricar_mayorista), linea.product_id.categ_id.id, indice))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_tope_mayorista-cantidad_por_fabricar_mayorista
                else:
                    #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                    lineas_a_optimizar.append((linea.id,cantidad_a_fabricar_linea,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion,fecha_de_entrega))
                    #actualizo cant por fabricar y cant por fabricar mayorista
                    categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+cantidad_a_fabricar_linea
                    categorias_cant[linea.product_id.categ_id.id][1]=categorias_cant[linea.product_id.categ_id.id][1]+cantidad_a_fabricar_linea
            #Si la cantidad de la linea excede el límite de fabricación, optimizo al maximo posible
            elif cantidad_a_fabricar_linea>cantidad_tope-cantidad_por_fabricar:
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(cantidad_tope-cantidad_por_fabricar)
                lineas_a_optimizar.append((linea.id,cantidad_tope-cantidad_por_fabricar,cantidad_a_fabricar_linea,linea.product_id.categ_id.id,linea.mayorista,True,fecha_de_fabricacion,fecha_de_entrega))
            else:
                print('categorias_cant:',categorias_cant)
                print('categorias_cant[linea.product_id.categ_id.id]:',categorias_cant[linea.product_id.categ_id.id])
                categorias_cant[linea.product_id.categ_id.id][0]=categorias_cant[linea.product_id.categ_id.id][0]+(linea.cantidad-linea.cantidad_a_realizar)
                lineas_a_optimizar.append((linea.id,linea.cantidad-linea.cantidad_a_realizar, cantidad_a_fabricar_linea, linea.product_id.categ_id.id, linea.mayorista, True, fecha_de_fabricacion,fecha_de_entrega))
            indice+=1
            print('lineas_a_optimizar:',lineas_a_optimizar)
        print('#############################################')
        print('lineas_a_optimizar:',lineas_a_optimizar)
        print('#############################################')
        #Chequeo elementos descartados
        for linea in lineas_pendientes:
            #lineas_pendientes lista de (id bolsa detalle,cant remanente,categoria,mayorista si/no)
            cantidad_por_fabricar=categorias_cant[linea[2]][0]
            fecha_de_fabricacion=categorias_cant[linea.product_id.categ_id.id][2]
            fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
            cantidad_a_fabricar_linea=linea[1]
            cantidad_tope=dict_categ[linea[2]][0]
            cantidad_tope_mayorista=dict_categ[linea[2]][1]
            #chequeo si para la categoría que se está analizando se completó la capacidad para esa fecha o no
            if cantidad_tope==cantidad_por_fabricar:
                fecha_de_fabricacion=self.get_next_fecha(fecha_de_fabricacion,0)
                fecha_de_entrega=self.get_fecha_correlativa(fecha_de_fabricacion)
                #Si ya no tengo otra fecha de fabricación, tengo que dejar de optimizar con esa categoria
                if fecha_de_fabricacion==False:
                    continue
                #Cambio fecha y reseteo contador de capacidad
                categorias_cant[linea[2]][0]=0
                categorias_cant[linea[2]][1]=0
                categorias_cant[linea[2]][2]=fecha_de_fabricacion
                cantidad_por_fabricar=0
            #Si es mayorista chequeo si la cantidad de la linea excede o no la capacidad maxima de categoría teniendo en cuenta el porcentaje mayorista
            if linea[1]>cantidad_tope-cantidad_por_fabricar:
                #La cantidad remanente de la linea excede la capacidad permitida de la categoria, completo hasta la cantidad límite
                #si la fecha de la linea es la misma que la fecha de la linea a optimizar, la sumo, sino la agrego aparte con la nueva fecha de fabricacion
                if lineas_a_optimizar[linea[3]][6]==fecha_de_fabricacion:
                    lineas_a_optimizar[linea[3]][1]=lineas_a_optimizar[linea[3]][1]+(cantidad_tope-cantidad_por_fabricar)
                else:
#                               0                   1               2                       3           4               5
#lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no)
                    lineas_a_optimizar.append((linea[0], cantidad_tope-cantidad_por_fabricar, cantidad_tope-cantidad_por_fabricar,linea[2], linea[3], True,fecha_de_fabricacion,fecha_de_entrega))
                #actualizo cant por fabricar
                dict_categ[linea[2]][0]=dict_categ[linea[2]][0]+cantidad_tope-cantidad_por_fabricar
            else:
                #La cantidad mayorista de la linea no excede la capacidad mayorista permitida de la categoria, agrego toda la linea
                #si la fecha de la linea es la misma que la fecha de la linea a optimizar, la sumo, sino la agrego aparte con la nueva fecha de fabricacion
                if lineas_a_optimizar[linea[3]][6]==fecha_de_fabricacion:
                    lineas_a_optimizar[linea[3]][1]=lineas_a_optimizar[linea[3]][1]+linea[1]
                else:
                    lineas_a_optimizar.append((linea[0], linea[1], cantidad_tope-cantidad_por_fabricar,linea[2], linea[3], True,fecha_de_fabricacion,fecha_de_entrega))
                #actualizo cant por fabricar y cant por fabricar mayorista
                categorias_cant[linea[2]][0]=categorias_cant[linea[2]][0]+linea[1]

        #Creo las lineas de optimización   0                1               2                       3           4               5               6
        #lineas_a_optimizar lista de (id bolsa detalle,cant a optimizar,cant total-cant realizada,categoria,mayorista si/no,fabricar si/no,fecha fabricacion)
        for linea in lineas_a_optimizar:
            if linea[1]==0:
                continue
            self.env['optimizacion.logistica.detalle'].create({'optimizacion_id':self.id, 'bolsa_line_id':linea[0], 'cantidad_a_realizar':linea[1], 'fecha_fabricacion':linea[6], 'fecha_entrega':linea[7], 'fabricar':linea[5], 'estado':'borrador'})
            bolsa_det=self.env['bolsa.ventas.detalle'].browse(linea[0])
            bolsa_det.write({'cantidad_a_realizar':bolsa_det.cantidad_a_realizar+linea[1]})
        self.onchange_items()

    def asignar_camion_bodega(self):
        return {'name': ('Asignar Camión/Bodega'),'view_mode': 'form','res_model': 'lcd.wzd_optimizacion_camion_bodega','type': 'ir.actions.act_window','context': {'active_ids': self.items.ids}, 'target': 'new',}

    @api.onchange('items')
    def onchange_items(self):
        #Calculo totales
        self.totales_categ=False
        self.totales_prod=False
        categs={}
        prods={}
        camiones={}
        lista_categs=[]
        lista_prods=[]
        producto_fabricable=self.env.ref('mrp.route_warehouse0_manufacture').id
        #Recorro el detalle y voy sumando las cantidades por fecha por categoría y por fecha por producto, ademas calculo la capacidad de los camiones por dia
        for item in self.items:
            #Sumo camion y fecha y volumen
            if item.camion_id:
                if (item.camion_id.id,item.fecha_entrega) in camiones:
                    camiones[(item.camion_id.id,item.fecha_entrega)]=camiones[(item.camion_id.id,item.fecha_entrega)]+item.volumen
                else:
                    camiones[(item.camion_id.id,item.fecha_entrega)]=item.volumen
            #Si no es fabricable no lo cuento
            if item.product_id.route_ids ==False or (producto_fabricable not in item.product_id.route_ids.ids):
                continue
            #Sumo por categoria
            if (item.categ_id.id,item.fecha_fabricacion) in categs:
                categs[(item.categ_id.id,item.fecha_fabricacion)]=categs[(item.categ_id.id,item.fecha_fabricacion)]+item.cantidad_a_realizar
            else:
                categs[(item.categ_id.id,item.fecha_fabricacion)]=item.cantidad_a_realizar
            #Sumo por producto
            if (item.product_id.id,item.fecha_fabricacion) in prods:
                prods[(item.product_id.id,item.fecha_fabricacion)]=prods[(item.product_id.id,item.fecha_fabricacion)]+item.cantidad_a_realizar
            else:
                prods[(item.product_id.id,item.fecha_fabricacion)]=item.cantidad_a_realizar

        for nombre,cantidad in prods.items():
            lista_prods.append((0, 0, {'product_id': nombre[0],'fecha':nombre[1],'total': cantidad}))
        warning=''
        danger=''
        #Chequeo que todas las lineas tengan camion y bodega asignada
        if len(self.items.filtered(lambda v: len(v.bodega_id)==0 or len(v.camion_id)==0)):
            danger+='Todas las líneas deben tener camión y bodega asignados <br>==========================<br>'
        capacidad_excedida=False
        #1 - amarillo - 2- rojo
        colores={}
        for nombre,cantidad in categs.items():
            lista_categs.append((0, 0, {'categ_id': nombre[0],'fecha':nombre[1],'total': cantidad}))
            categ=self.env['product.category'].browse(nombre[0])
            if categ.maximo_permitido!=0:
                if categ.maximo_permitido<cantidad:
                    danger+="La categoría "+categ.name+" excedió su máximo permitido de '"+str(categ.maximo_permitido)+"' para la fecha "+nombre[1].strftime('%d/%m/%Y')+". Cantidad indicada: "+str(cantidad)+"<br>"
                    capacidad_excedida=True
                    colores[(nombre[0],nombre[1])]=2
                elif categ.capacidad_fabricacion<cantidad:
                    warning+="La categoría "+categ.name+" excedió su capacidad de fabricación de "+str(categ.capacidad_fabricacion)+"' para la fecha "+nombre[1].strftime('%d/%m/%Y')+". Cantidad indicada: "+str(cantidad)+"<br>"
                    colores[(nombre[0],nombre[1])]=1
        print('camiones:',camiones)
        for camion,volumen in camiones.items():
            obj_camion=self.env['lcd.camion'].browse(camion[0])
            if volumen>obj_camion.capacidad:
                print('obj_camion:',obj_camion)
                print('obj_camion.placa:',obj_camion.placa)
                print('camion[1]:',camion[1])
                print('obj_camion.capacidad:',obj_camion.capacidad)
                print('volumen:',volumen)
                warning+="La capacidad del camión "+obj_camion.placa+" está excedida para la fecha "+camion[1].strftime('%d/%m/%Y')+". Capacidad camión:"+str(obj_camion.capacidad)+", volumen a llevar: "+str(volumen)+"<br>"
        for item in self.items:
            print('colores:',colores)
            print('item.fecha_fabricacion:',item.fecha_fabricacion)
            print('fields.Date.from_string(item.fecha_fabricacion):',fields.Date.from_string(item.fecha_fabricacion))
            if (item.categ_id.id,(fields.Date.from_string(item.fecha_fabricacion))) in colores:
                item.color=colores[(item.categ_id.id,(fields.Date.from_string(item.fecha_fabricacion)))]
            else:
                item.color=False
        if capacidad_excedida==False:
            self.capacidad_excedida=False
        else:
            self.capacidad_excedida=True
        self.totales_categ=lista_categs
        self.totales_prod=lista_prods
        warnings=''
        if danger!='':
            warnings+='<font style="color: rgb(207, 36, 21);">'+danger+'==========================<br></font>'
        if warning!='':
            warnings+='<font style="color: rgb(219, 129, 11);">'+warning+'</font>'
        self.warnings=warnings

    def confirmar(self):
        #Chequeo que todas las lineas tengan camion y bodega asignada
        if len(self.items.filtered(lambda v: len(v.bodega_id)==0 or len(v.camion_id)==0)):
            raise UserError('Todas las líneas deben tener camión y bodega asignados')  
        #Chequeo que todas las lineas tengan zona definida
        print("self.items.filtered(lambda v: v.zona_id==False or v.zona_id.id==self.env.ref('lcd_optimizacion_logistica.sale_order_zona_sin_zona').id):",self.items.filtered(lambda v: v.zona_id==False or v.zona_id.id==self.env.ref('lcd_optimizacion_logistica.sale_order_zona_sin_zona').id))
        if len(self.items.filtered(lambda v: len(v.zona_id)==0 or v.zona_id.id==self.env.ref('lcd_optimizacion_logistica.sale_order_zona_sin_zona').id))>0:
            raise UserError('Todas las líneas deben tener zona asignada')  
        #Chequeo capacidad de planta
        if self.capacidad_excedida==True:
            raise UserError('La capacidad de planta está excedida')

        camiones={}
        excepciones=''
        for item in self.items.filtered(lambda v: v.estado=='borrador'):
            #Genero  ordenes de entrega, chequeo disponibilidad y reservo
            print('linea:',item.bolsa_line_id.order_line_id.order_id.name)
            vals_delivery={}
            vals_delivery['partner_id']=item.bolsa_line_id.order_line_id.order_id.partner_id.id
            vals_delivery['commercial_partner_id']=item.bolsa_line_id.order_line_id.order_id.partner_id.commercial_partner_id.id
            vals_delivery['line_ids']=[(0,0,{
                        "order_line_id": item.bolsa_line_id.order_line_id.id,
                        "name": item.bolsa_line_id.order_line_id.name,
                        "product_id": item.product_id.id,
                        "qty_ordered": item.bolsa_line_id.order_line_id.product_uom_qty,
                        "qty_procured": item.bolsa_line_id.order_line_id.qty_procured,
                        "quantity": item.cantidad_a_realizar})]
            print('obj_delivery')
            try:
                obj_delivery=self.env['manual.delivery'].with_context(active_ids=[item.bolsa_line_id.order_line_id.id],active_model='sale.order.line').create(vals_delivery)
                obj_delivery.confirm()
                self.env['stock.picking'].search([('optimizacion_detalle_id','=',False),('origin','=',item.bolsa_line_id.order_line_id.order_id.name)]).write({'optimizacion_detalle_id':item.id})
                self.env['mrp.production'].search([('optimizacion_detalle_id','=',False),('origin','=',item.bolsa_line_id.order_line_id.order_id.name)]).write({'optimizacion_detalle_id':item.id})
            except Exception as e:
                excepciones+=item.bolsa_line_id.order_line_id.order_id.name+":"+e.name+"\n"
                print('e:',e)
            if (item.camion_id,item.fecha_entrega,item.bodega_id) not in camiones:
                camiones[(item.camion_id,item.fecha_entrega,item.bodega_id)]=[item]
            else:
                camiones[(item.camion_id,item.fecha_entrega,item.bodega_id)].append(item)
        if excepciones!='':
            raise UserError(excepciones)
        for camion,rutas in camiones.items():
            ruta=self.env['lcd.rutas_horarios'].create({'camion_id':camion[0].id,'fecha_despacho':camion[1],'bodega_id':camion[2].id,'optimizacion_id':self.id,'estado':'borrador'})
            for linea in rutas:
                self.env['lcd.rutas_horarios_detalle'].create({'ruta_id':ruta.id,'cantidad':linea.cantidad_a_realizar,'optimizacion_det_id':linea.id,'sequence':1000})
            #Defino ruta consultando con google maps
            ruta.calcular_ruta()
        #Cambio estados
        self.write({'estado':'optimizado'})
        for item in self.items.filtered(lambda v: v.estado=='borrador'):
            item.write({'estado':'terminado'})

class OptimizacionLogisticaDetalle(models.Model):
    _name = 'optimizacion.logistica.detalle'
    _description = 'Detalle de Optimizacion Logistica'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    bolsa_line_id=fields.Many2one('bolsa.ventas.detalle','Linea de Bolsa de Ventas')
    bolsa_id=fields.Many2one('bolsa.ventas',related='bolsa_line_id.bolsa_id',store=True)
    pedido=fields.Char(related='bolsa_line_id.pedido',string='Pedido',store=True)
    pedido_id=fields.Many2one(related='bolsa_line_id.pedido_id',string='Pedido',store=True)
    mrp_production_id=fields.Many2one('mrp.production','Órden de Producción')
    fecha_pedido=fields.Datetime(related='bolsa_line_id.fecha_pedido',string='Fecha Pedido',store=True)
    partner_id=fields.Many2one('res.partner',related='bolsa_line_id.partner_id',string='Cliente',store=True)
    direccion=fields.Char(related='bolsa_line_id.direccion',string='Dirección',store=True)
    telefono=fields.Char(related='bolsa_line_id.telefono',string='Teléfono',store=True)
    celular=fields.Char(related='bolsa_line_id.celular',string='Celular',store=True)
    latitud=fields.Float(related='bolsa_line_id.latitud',string='Latitud',store=True)
    longitud=fields.Float(related='bolsa_line_id.longitud',string='Longitud',store=True)
    product_id=fields.Many2one('product.product',related='bolsa_line_id.product_id',string='Producto',store=True)
    volumen=fields.Float(related='bolsa_line_id.volumen',string='Volumen',store=True)
    fecha_cierta=fields.Date(related='bolsa_line_id.fecha_cierta',string='Fecha Cierta',store=True)
    categ_id=fields.Many2one('product.category',related='bolsa_line_id.categ_id',string='Categoría',store=True)
    zona_id=fields.Many2one('sale.order.zona',related='bolsa_line_id.zona_id',string='Zona',store=True)
    canal_venta_id=fields.Many2one('sale.order.canal',related='bolsa_line_id.canal_venta_id',string='Canal de Venta',store=True)
    tipo_entrega_id=fields.Many2one('sale.order.tipo_entrega',related='bolsa_line_id.tipo_entrega_id',string='Tipo Entrega',store=True)
    cantidad_ov=fields.Float(related='bolsa_line_id.cantidad',string='Cantidad OV')
    cantidad_realizada=fields.Float(related='bolsa_line_id.cantidad_realizada',string='Cantidad Realizada')
    cantidad_a_realizar=fields.Float(string='A Realizar')
    fecha_fabricacion=fields.Date(string='Fecha Fabricación')
    fecha_entrega=fields.Date(string='Fecha Entrega')
    fabricar=fields.Boolean(string='¿Fabricar?')
    estado=fields.Selection([('borrador','Borrador'),('en_proceso','En Proceso'),('terminado','Terminado'),('cancelado','Cancelado')],string='Estado',default='borrador')
    bodega_id=fields.Many2one('lcd.bodega',string='Bodega')
    camion_id=fields.Many2one('lcd.camion',string='Camión')
    color=fields.Integer('Color')

    def unlink(self):
        for rec in self:
            if rec.bolsa_line_id.estado!='cancelado':
                rec.bolsa_line_id.write({'cantidad_a_realizar':rec.bolsa_line_id.cantidad_a_realizar-rec.cantidad_a_realizar})
        return super(OptimizacionLogisticaDetalle, self).unlink()

    def write(self, vals):
        if 'cantidad_a_realizar' in vals:
            cant_anterior=self.cantidad_a_realizar
        res = super(OptimizacionLogisticaDetalle, self).write(vals=vals)
        if 'cantidad_a_realizar' in vals:
            cant_nueva=self.cantidad_a_realizar            
            self.bolsa_line_id.write({'cantidad_a_realizar':self.bolsa_line_id.cantidad_a_realizar-(cant_anterior-cant_nueva)})
        return res

    #No permitir que seleccionen una fecha de fabricacion fuera de las seleccionadas en la cabecera
    @api.onchange('fecha_fabricacion')
    def onchange_fecha_fab(self):
        fecha_elegida=self.fecha_fabricacion.strftime("%Y-%m-%d")
        fecha_elegida=fecha_elegida[5:-3]+"/"+fecha_elegida[-2:]+"/"+fecha_elegida[:4]
        if fecha_elegida not in self.optimizacion_id.fechas_fabricacion.split(','):
            raise UserError('Debe elegir una fecha de fabricación contenida en el rango de cabecera')

    #No permitir que seleccionen una fecha de entrega fuera de las seleccionadas en la cabecera
    @api.onchange('fecha_entrega')
    def onchange_fecha_ent(self):
        fecha_elegida=self.fecha_entrega.strftime("%Y-%m-%d")
        fecha_elegida=fecha_elegida[5:-3]+"/"+fecha_elegida[-2:]+"/"+fecha_elegida[:4]
        if fecha_elegida not in self.optimizacion_id.fechas_entrega.split(','):
            raise UserError('Debe elegir una fecha de entrega contenida en el rango de cabecera')

class OptimizacionLogisticaDetalleCateg(models.Model):
    _name = 'optimizacion.logistica.detalle_categ'
    _description = 'Detalle de Optimizacion Logistica- Total por Categoría'
    _rec_name = 'categ_id'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    fecha=fields.Date('Fecha')
    categ_id=fields.Many2one('product.category','Categoría')
    total=fields.Float('Total')

class OptimizacionLogisticaDetalleProd(models.Model):
    _name = 'optimizacion.logistica.detalle_prod'
    _description = 'Detalle de Optimizacion Logistica- Total por Producto'
    _rec_name = 'product_id'

    optimizacion_id=fields.Many2one('optimizacion.logistica')
    fecha=fields.Date('Fecha')
    product_id=fields.Many2one('product.product','Producto')
    total=fields.Float('Total')
