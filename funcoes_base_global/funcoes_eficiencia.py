import pandas as pd
from thermo.eos import *
from thermo.eos_mix import *
import numpy as np
import math
from thermo.chemical import *
from thermo.mixture import *
import pandas as pd
from collections import OrderedDict
import os


def get_parameters(composicao):

    temp_critica =[]
    press_critica = []
    mw = []
    omega = []
    cp_g = []
    cv_g = [] 
    componentes = []
    
    for tag in composicao:
        
        temp_critica.append(tag.Tc)
        press_critica.append(tag.Pc)
        mw.append(tag.MW)
        omega.append(tag.omega)
        cp_g.append(tag.Cpg)
        cv_g.append(tag.Cvg)
        componentes.append(tag.name)
        
    dados = {   'Componentes': componentes,
                'Tcs': temp_critica,
                'Pcs': press_critica,
                'MW': mw,
                'omegas': omega,
                'Cp_g_ID': cp_g,
                'Cv_g_ID': cv_g}
    
    return (dados)


def dados_compressor(B , metric_unit = 'mm'):
    
    A = B.copy()
    
    if metric_unit == 'mm':
        A['diametro_cilindro'] = A['diametro_cilindro'] * 0.001
        A['diametro_haste'] = A['diametro_haste'] * 0.001
        A['curso_pistao'] = A['curso_pistao'] * 0.001
    
    
    A['vol_deslc_cilindro'] = (A['qtd_efeitos'] *A['diametro_cilindro']**2 - A['diametro_haste']**2) * math.pi * A['curso_pistao']/4
    A['vazao_volumetrica'] = A['vol_deslc_cilindro'] * A['rpm'] * 60 * A['qtd_cilindros']
    A['vel_pistao'] = (2 * A['curso_pistao'] * A['rpm'])/60
  
   
    return A


def recorrencia(df, dados, dataSheetComp, tags_suc, tags_desc, tags_comp):
    
    
    EOS_INFO = pd.DataFrame(index = df.index)
    EOS_INFO['lista'] = df.apply(lambda x : eos_estagios(x, tags_suc, tags_desc, tags_comp, dados, dataSheetComp), axis = 1)
    EOS_INFO = pd.DataFrame(EOS_INFO['lista'].values.tolist(), columns=['Ef_Politropica','Head_Politropica','Ef_Isentropica','Head_Isentropica','Z_Suc','Z_Desc','MW','T_Suc','r','k', 'Densidade_Suc', 'Densidade_Desc', 'Ef_Volumetrica', 'Pot_Compressao', 'Pot_Politropica', 'Pot_Isentropica'])
    EOS_INFO = EOS_INFO.set_index(df.index)

    return EOS_INFO


def eos_estagios (x, tags_suc, tags_desc,tags_comp, dados, dataSheetComp):
    
    Tsys = list(x[[tags_suc[0], tags_desc[0]]])
    Psys = list(x[[tags_suc[1], tags_desc[1]]])
    comp = list(x[tags_comp])
    
    EOS_2oSUC = EOS_MIX(comp, dados, Tsys[0], Psys[0])
    EOS_2oDESC = EOS_MIX(comp, dados, Tsys[1], Psys[1])
    
    return(consolida_value_estagio)(EOS_2oSUC, EOS_2oDESC, Tsys, Psys, dataSheetComp)


def EOS_MIX(comp, dadosDf, Tsys, Psys):

    # EOS = SRKMIX(Tcs = list(dadosDf.Tcs),
    #           Pcs = list(dadosDf.Pcs), 
    #           omegas = list(dadosDf.omegas), 
    #           zs = comp, 
    #           T=Tsys, 
    #           P=Psys )
    
    # Z_EOS = (Psys*EOS.V_g)/(8.31447*Tsys)
    # mwAVG = np.sum(comp * dadosDf.MW)/np.sum(comp)
    # densidade = (mwAVG*1E-3)/EOS.V_g
    # cp_Real = np.sum(dadosDf.Cp_g_ID * comp) + EOS.Cp_dep_g
    # cv_Real = np.sum(dadosDf.Cv_g_ID * comp) + EOS.Cv_dep_g
    # k = cp_Real/ cv_Real
    # EOS_V_g = EOS.V_g
    # return [Z_EOS, mwAVG, densidade, EOS_V_g, k]


   try: 
       EOS = SRKMIX(Tcs = list(dadosDf.Tcs),
                 Pcs = list(dadosDf.Pcs), 
                 omegas = list(dadosDf.omegas), 
                 zs = comp, 
                 T=Tsys, 
                 P=Psys )
   
       Z_EOS = (Psys*EOS.V_g)/(8.31447*Tsys)
       mwAVG = np.sum(comp * dadosDf.MW)/np.sum(comp)
       densidade = (mwAVG*1E-3)/EOS.V_g
       cp_Real = np.sum(dadosDf.Cp_g_ID * comp) + EOS.Cp_dep_g
       cv_Real = np.sum(dadosDf.Cv_g_ID * comp) + EOS.Cv_dep_g
       k = cp_Real/ cv_Real
       EOS_V_g = EOS.V_g
       return [Z_EOS, mwAVG, densidade, EOS_V_g, k]
   
   except:
       Z_EOS = np.nan
       mwAVG = np.nan
       densidade = np.nan
       cp_Real = np.nan
       cv_Real = np.nan
       k = np.nan        
       EOS_V_g = np.nan
       #print('error')
       return [Z_EOS, mwAVG, densidade, EOS_V_g, k]



def EOS_SIMPLE(comp, dadosDf, Tsys, Psys):
    
    TC = dadosDf.Tcs*comp
    PC = dadosDf.Pcs*comp
    OMEGA = dadosDf.omegas * comp
    mwAVG = np.sum(comp * dadosDf.MW)
    EOS = SRK(Tc = TC,
              Pc = PC, 
              omega = OMEGA, 
              T=Tsys, 
              P=Psys )
    
    Z_EOS = (Psys*EOS.V_g)/(8.31447*Tsys)
    
    densidade = (mwAVG*1E-3)/EOS.V_g
    cp_Real = np.sum(dadosDf.Cp_g_ID * comp) + EOS.Cp_dep_g
    cv_Real = np.sum(dadosDf.Cv_g_ID * comp) + EOS.Cv_dep_g
    k = cp_Real/ cv_Real
    return [Z_EOS, mwAVG, densidade, EOS.V_g, k]


def consolida_value_estagio(EOS_2oSUC, EOS_2oDESC, Tsys, Psys, dataSheetComp):
    
    try: 
        if EOS_2oSUC[0] != np.nan:
            massa_especifica =  EOS_2oSUC[2]          #SAIDA PARA A PROXIMA FUNÇÃO --> MASSA ESPECIFICA

            z_suc = EOS_2oSUC[0]                       #SAIDA PARA A PROXIMA FUNÇÃO --> z_suc
            z_desc = EOS_2oDESC[0]                     #SAIDA PARA A PROXIMA FUNÇÃO --> z_desc

            PsucMAN = kgfMAN(Psys[0])                 #SAIDA PARA A PROXIMA FUNÇÃO --> PSUCMAN
            PdescMAN = kgfMAN(Psys[1])                #SAIDA PARA A PROXIMA FUNÇÃO --> PDESCMAN

            PsucABS = kgfABS(Psys[0])                 #SAIDA PARA A PROXIMA FUNÇÃO --> PSUCABS
            PdescABS = kgfABS(Psys[1])                #SAIDA PARA A PROXIMA FUNÇÃO --> PDESCABS

            r = PdescABS/PsucABS                      #SAIDA PARA A PROXIMA FUNÇÃO --> R
        #     print(PdescABS)
        #     print(PsucABS)
        #     print(r)
        #     print("\n")

            k_2oSUC = EOS_2oSUC[4]
            k_2oDESC = EOS_2oDESC[4]

            densidade_suc = EOS_2oSUC[2]
            densidade_desc = EOS_2oDESC[2]


            k = (k_2oSUC + k_2oDESC)/2 
            #k = 1.179041

            t_suc = Tsys[0]                                #SAIDA PARA A PROXIMA FUNÇÃO --> t_suc
            t_desc = Tsys[1]

            TdescI2o =((r**((k-1)/k))*(t_suc))

            ef_volumetrica = eficiencia_volumetrica(dataSheetComp, z_suc, z_desc, k, r)
            vazao_massica = vazao_volumetrica(ef_volumetrica, dataSheetComp, massa_especifica)
            #vazao_massica = vazao_massica(ef_volumetrica, dataSheetComp, massa_especifica)
            ef_adiabatica = eficiencia_adia_isental(t_desc, r, t_suc, k)
            head_adiabatico = head_adia(k, z_suc, z_desc, EOS_2oDESC, r, t_suc)
            potComp = potencia_comp(vazao_massica, head_adiabatico, ef_adiabatica)
            ef_poli = eficiencia_politropica(k, r, t_suc, t_desc)

            MW = EOS_2oSUC[1]

            head_politropico = head_poli(k, z_suc, z_desc, MW, t_suc, ef_poli, r)
            potPoli = potencia_comp_poli(vazao_massica, head_politropico, ef_poli)

            potencia_politropica = potencia_eixo(potPoli)
            potencia_isentropica = potencia_eixo(potComp)

            resultado = [ef_poli, head_politropico, ef_adiabatica, head_adiabatico, z_suc, z_desc, EOS_2oSUC[1], t_suc, r, k, densidade_suc, densidade_desc, ef_volumetrica, potComp, potencia_politropica, potencia_isentropica]
        else:
            print('error_2')
            resultado = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    except:
        print('error_3')
        resultado = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    return resultado



def kgfMAN(P):
    Pvem = P/98066.5 - 1.03323
    return Pvem

def kgfABS(P):
    Pvem = P/98066.5 
    return Pvem

def eficiencia_politropica(k, r, t_suc, t_desc):
    ef_politropica =((k-1)/k)*math.log(r)*100/math.log((t_desc)/(t_suc))
    return ef_politropica

def head_poli(k, z_suc, z_desc, MW, t_suc, ef_poli, r):
    head = (k /(k  -1))*((z_suc+z_desc)/2)*(8.31447/MW) *(t_suc      )*(ef_poli/100)*((r** (((k  -1)/k  )*(100/ef_poli)))-1)
    return head

def potencia_comp_poli(vazao_massica, head_politropico, ef_poli):
    potencia = (vazao_massica/3600)*head_politropico/(ef_poli*0.01)
    return potencia

def eficiencia_volumetrica(dataSheetComp, z_suc, z_desc, k, r):
    vazamento = 0.07
    ef_volumetrica = (0.97-(dataSheetComp[6]/100)*((z_suc/z_desc)*r**(1/k)-1)-vazamento)*100
    return ef_volumetrica

def vazao_volumetrica(ef_volumetrica, dataSheetComp,massa_especifica):
    vaz_volumetrica = (ef_volumetrica/100)*dataSheetComp[8]*dataSheetComp[7]*60
    vaz_massica = vaz_volumetrica*massa_especifica                #SAIDA DE VAZAO MASSICA
    vaz_volumetrica_padrao = vaz_massica/(101.325*massa_especifica/(8.31447*273.15))
    return vaz_massica

#def vazao_massica(ef_volumetrica, dataSheetComp,massa_especifica):
#    vaz_volumetrica = (ef_volumetrica/100)*dataSheetComp[8]*dataSheetComp[7]*60
#    vaz_massica = vaz_volumetrica*massa_especifica                #SAIDA DE VAZAO MASSICA
#    #vaz_volumetrica_padrao = vaz_massica/(101.325*massa_especifica/(8.31447*273.15))
#    return vaz_massica 


def eficiencia_adia_isental(t_desc, r, t_suc, k):
    ef_adiabatica = ((t_suc)/(t_desc-t_suc))*(r **((k-1)/k)-1)*100
    return ef_adiabatica

def head_adia(k, z_suc, z_desc,  EOS_2oDESC, r, t_suc):
    head_adiabatico = (k/(k-1))*((z_suc+z_desc)/2)*(8.31447/EOS_2oDESC[1])*(t_suc)*((r**((k-1)/k))-1)
    return head_adiabatico

def potencia_comp(vazao_massica, head_adiabatico, ef_adiabatica):
    pot_compressao = (vazao_massica/3600)*head_adiabatico/(ef_adiabatica*0.01)
    return  pot_compressao

def potencia_eixo(potComp):
    mecEf = 73
    pot_eixo=potComp/(mecEf*0.01)
    return pot_eixo
