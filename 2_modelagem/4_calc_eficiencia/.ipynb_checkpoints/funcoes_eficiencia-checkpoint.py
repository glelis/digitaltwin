
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

def recorrencia(df, dados, dataSheetComp, tags_suc, tags_desc):
    
    
    EOS_INFO = pd.DataFrame(index = df.index)
    EOS_INFO['lista'] = df.apply(lambda x : eos_estagios(x, tags_suc, tags_desc), axis = 1)
    EOS_INFO = pd.DataFrame(EOS_INFO['lista'].values.tolist(), columns=['Ef_Politropica','Head_Politropica','Ef_Isentropica','Head_Isentropica','Z_Suc','Z_Desc','MW','T_Suc','r','k', 'Densidade_Suc', 'Densidade_Desc'])
    EOS_INFO = EOS_INFO.set_index(df.index)

    return EOS_INFO

def eos_estagios (x, tags_suc, tags_desc, dados = dados, dataSheetComp = data_segundo_estagio):
    
    #print(x)
    
    Tsys = list(x[[tags_suc[0], tags_desc[0]]])
    Psys = list(x[[tags_suc[1], tags_desc[1]]])
    comp = list(x[['Eteno', 'Etano', 'Propeno', 'Propano', 'Buteno', 'Butano', 'Hexeno', 'Hexano']])
    
    
    EOS_2oSUC = EOS_MIX(comp, dados, Tsys[0], Psys[0])
    EOS_2oDESC = EOS_MIX(comp, dados, Tsys[1], Psys[1])
    
    return(consolida_value_estagio)(EOS_2oSUC, EOS_2oDESC, Tsys, Psys, dataSheetComp)

def EOS_MIX(comp, dadosDf, Tsys, Psys):
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
    return [Z_EOS, mwAVG, densidade, EOS.V_g, k]

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
    
    massa_especifica =  EOS_2oSUC[2]          #SAIDA PARA A PROXIMA FUNÇÃO --> MASSA ESPECIFICA
    
    Zsuc = EOS_2oSUC[0]                       #SAIDA PARA A PROXIMA FUNÇÃO --> ZSUC
    Zdesc = EOS_2oDESC[0]                     #SAIDA PARA A PROXIMA FUNÇÃO --> ZDESC
    
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
    
    
    # k = (k_2oSUC + k_2oDESC)/2 
    k = 1.179041

    Tsuc = Tsys[0]                                #SAIDA PARA A PROXIMA FUNÇÃO --> Tsuc
    Tdesc = Tsys[1]
    
    TdescI2o =((r**((k-1)/k))*(Tsuc))

    ef_volumetrica = eficiencia_volumetrica(dataSheetComp, Zsuc, Zdesc, k, r)
    vazao_massica = vazao_volumetrica(ef_volumetrica, dataSheetComp, massa_especifica)
    ef_adiabatica = eficiencia_adia_isental(Tdesc, r, Tsuc, k)
    headAdia = head_adia(k, Zsuc, Zdesc, EOS_2oDESC, r, Tsuc)
    potComp = potencia_comp(vazao_massica, headAdia, ef_adiabatica)
    ef_poli = eficiencia_politropica(k, r, Tsuc, Tdesc)
 
    MW = EOS_2oSUC[1]
  
    headPoli = head_poli(k, Zsuc, Zdesc, MW, Tsuc, ef_poli, r)
    potPoli = potencia_comp_poli(vazao_massica, headPoli, ef_poli)

    POTENCIA_POLI = potencia_eixo(potPoli)
    POTENCIA_ISEN = potencia_eixo(potComp)

    resultado = [ef_poli, headPoli, ef_adiabatica, headAdia, Zsuc, Zdesc, EOS_2oSUC[1], Tsuc, r, k, densidade_suc, densidade_desc]

    return resultado

def kgfMAN(P):
    Pvem = P/98066.5 - 1.03323
    return Pvem

def kgfABS(P):
    Pvem = P/98066.5 
    return Pvem

def eficiencia_politropica(k, r, Tsuc, Tdesc):
    ef_politropica =((k  -1)/k  )*math.log(r)*100/math.log((Tdesc     )/(Tsuc      ))
    return ef_politropica

def head_poli(k, Zsuc, Zdesc, MW, Tsuc, ef_poli, r):
    head = (k /(k  -1))*((Zsuc+Zdesc)/2)*(8.31447/MW) *(Tsuc      )*(ef_poli/100)*((r** (((k  -1)/k  )*(100/ef_poli)))-1)
    return head

def potencia_comp_poli(vazao_massica, headPoli, ef_poli):
    potencia = (vazao_massica/3600)*headPoli/(ef_poli*0.01)
    return potencia

def eficiencia_volumetrica(dataSheetComp, Zsuc, Zdesc, k, r):
    vazamento = 0.07
    ef_volumetrica = (0.97-(dataSheetComp[6]/100)*((Zsuc/Zdesc)*r**(1/k)-1)-vazamento)*100
    return ef_volumetrica

def vazao_volumetrica(ef_volumetrica, dataSheetComp,massa_especifica):
    vaz_volumetrica = (ef_volumetrica/100)*dataSheetComp[8]*dataSheetComp[7]*60
    vaz_massica = vaz_volumetrica*massa_especifica                #SAIDA DE VAZAO MASSICA
    vaz_volumetrica_padrao = vaz_massica/(101.325*massa_especifica/(8.31447*273.15))
    return vaz_volumetrica

def eficiencia_adia_isental(Tdesc, r, Tsuc, k):
    ef_adiabatica = ((Tsuc)/(Tdesc-Tsuc))*(r **((k-1)/k)-1)*100
    return ef_adiabatica

def head_adia(k, Zsuc, Zdesc,  EOS_2oDESC, r, Tsuc):
    head_adiabatico = (k/(k-1))*((Zsuc+Zdesc)/2)*(8.31447/EOS_2oDESC[1])*(Tsuc)*((r**((k-1)/k))-1)
    return head_adiabatico

def potencia_comp(vazao_massica, headAdia, ef_adiabatica):
    pot_compressao = (vazao_massica/3600)*headAdia/(ef_adiabatica*0.01)
    return  pot_compressao

def potencia_eixo(potComp):
    mecEf = 73
    pot_eixo=potComp/(mecEf*0.01)
    return pot_eixo
