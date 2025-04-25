import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from random import *
import matplotlib.pyplot as plt
from matplotlib.dates import (DAILY,HOURLY,MINUTELY,DateFormatter,
                              rrulewrapper, RRuleLocator, drange)

import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib import ticker

import datetime
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

def plot_variables_full(df, variables_array, start_date, end_date, **params):
    """
        Descrição: Função responsável por apresentar o gráfico com as seguintes características:

            - Delimitação de período a ser apresentado;
            - Escolha das variáveis;
            - Uma curva de tendência utilizando uma filtro de média móvel (personalizado);
            - Personalização das fontes;
            - Marcação de períodos com blocos personalizados;
            - Marcação de dias;
            - Plot do erro Absoluto (entre duas variaveis especificadas);
            - Salve do gráfico;
            - Salve do csv do dataframe delimitado;

        =====================================================================

        Parâmetros:

            df:
                DataFrame a ser plotado (obrigatório)

            variables_array:
                Variáveis do DataFrame a serem plotados (obrigatório)

            start_date:
                Início do período a ser plotado (obrigatório)

            end_date:
                Fim do período a ser plotado (obrigatório)

        ======================================================================

            **params (Foi implementado essa forma de parâmetro **kwargs onde terá a possibilidade de passar um dicionários com os parametros a seres escolhidos.
             Esse conjuntos de parametros são todos opcionais): 

                ylabel:
                    Descrição da label para o eixo y (Default: '')

                xlabel:  
                    Descrição da label para o eixo x (Default: "Data")

                titulo:
                    Título para o gráfico (Default: '') (É utilizado um combinação dos nomes das colunas))

                days_interval:
                    Intervalo de dias que será plotado (Default: 2)

                minutes_interval:
                    Intervalo de minutos que será plotado (Default: 180)

                save_figure_name:
                    Nome do arquivo da imagem do gráfico que será salvo (Default: '')

                error:
                    Erro entre duas variáveis (Default: False)

                abs_error
                    Erro absoluto entre duas variáveis (Default: False)

                rolling_time:
                    Janela do filtro de média móvel a ser calculada(Default: 0)

                figure_heigh:
                    Altura da figura do gráfico (Default: 10)

                figure_width:
                    Comprimento da figura do gráfico (Default: 30)

                ticks:
                    Ticks do eixo Y a serem personalizado (Default: []) 
                    Ex: [0, 1, 0.1] ==>> eixo y ==  [0. , 0.1, 0.2, ...  0.8, 0.9, 1. ]

                tendencia:
                    Plota a curva de cada variável e sua respectiva tendência (Default.: False)

                label_font_size:
                    Tamanho da fonte da label (eixos) (Default: 18)

                label_font_weight
                    Espessura da fonte do label (eixos) (Default: 'bold')

                title_font_weight:
                    Espessura da fonte do título  (Default: 'bold')

                tick_font_weight:
                    Espessura da fonte do tick  (Default: 'bold')

                tick_font_size:
                    Tamanho da fonte da tick  (Default: 14)

                legenda_font_size
                    Tamanho da fonte da legenda  (Default: 16)

                treino_true_data:
                    Janela do treino limpo para ser destacada (Ex.: [data_ini:str, data_fim:str])

                treino_true_color:
                    Cor do bloco de treino limpo (Ex.: 'green')

                treino_true_alpha:
                    Quantidade de transparencia do bloco de treino limpo (Default.: 0.3)

                treino_true_label:
                    Legenda do bloco de treino limpo (Default.: 'Período de Treino Limpo)

                treino_falso_data:
                    Janelas do treino sujo para ser destacada (Ex.: [(data_ini:str, data_fim:str)])

                treino_falso_color:
                    Cor do bloco de treino sujo (Ex.: 'red')

                treino_falso_alpha:
                    Quantidade de transparência do bloco de treino sujo (Default.: 0.3)

                treino_falso_label:
                    Legenda do bloco de treino sujo (Default.: 'Período de Treino Sujo)

                bloco_destaque_data:
                    Janelas do bloco extra para ser destacada (Ex.: [(data_ini:str, data_fim:str)])

                bloco_destaque_color:
                    Cor do bloco extra (Ex.: 'yellow')

                bloco_destaque_label:
                    Legenda do bloco extra (Default.: 'Período Extra')

                bloco_destaque_alpha:
                    Quantidade de transparencia do bloco extra (Default.: 0.3)

                dia_destaque_data:
                    Datas a serem destacada (Ex.:[data])

                dia_destaque_color:
                    Cor da data destacada (Default: 'red')

                dia_destaque_label:
                    Descrição da data destacada (Default: 'Dia Destaque')

                reta_tendencia_data:
                    Períodos das retas de tendências a serem plotadas (Ex.: [(data_ini, data_fim)])

                reta_tendencia_color:
                    Cores a serem definidas para cada reta de tendência

                reta_tendencia_label:
                    Descrição na legenda de cada reta de tendência (Default: Reta de Tendência (Tag))

                reta_tendencia_ordem:
                    Descrição da ordem do FIT de todas as linhas de tendência (Default: 1)

                interval_yticker:
                    Intervalo inteiro no qual será distribuído os valores do eixo Y 

                show_legenda:
                    Mostrar a legenda (Default:True)

                label_legenda:
                    Descrição da label para a legenda (Default: nome da variavel)
                
                linestyle:
                    Estilo da linha (Default: '-') Ex:'-' ==> ______ | ':' => ...... | '-.' ==> --.--. | '--' ==> ------
                
                marker:
                    Marcação do ponto no gráfico (Default:'o')  Ex: '.' ',' 's' '*'  ... 

                linewidth:
                    Espessura da linha (Default: 1.5)


    ==============================================================================

            Exemplo de uso (Exemplo passando apenas os parâmetros obrigatórios):
                params = {    
                    "treino_true_data": [(date_ini_limpo,date_fim_limpo )],
                    "treino_false_data":[(date_ini_sujo,date_fim_sujo )],
                    "bloco_destaque_data":[(date_ini_bloco,date_fim_bloco )], 
                    "dia_destaque_data":[date_ini_limpo],  
                    "linha_tendencia_data": [(data_reta_tendencia_ini, data_reta_tendencia_fim)],
                    "linha_tendencia_color": ['red']  
                
                }

                plt_variables_full(dataframe_tags, dataframe.columns, dataframe_tags.index.min(), dataframe.index.max(), **params)
                

    Obs.: o uso do **kwargs tem a possibilidade do uso de um dicionário com os parâmetros, ou também pela a forma convencional (passando cada um por vez)
    
    """
    #Recuperando parametros de **params
    ylabel = params.get("ylabel",'')
    xlabel = params.get( "xlabel","Data")
    titulo = params.get( "titulo",'')
    days_interval = params.get( "days_interval",2)
    minutes_interval = params.get("minutes_interval",180)
    save_figure_name = params.get("save_figure_name",'')
    error = params.get("error",False)
    rolling_time = params.get("rolling_time",0)
    abs_error = params.get("abs_error",False )
    figure_heigh = params.get("figure_heigh",10)
    figure_width = params.get( "figure_width",30)
    ticks = params.get( "ticks",[])
    tendencia = params.get( "tendencia",False)
    show_legenda = params.get( "show_legenda",True)
    label_legenda =  params.get("label_legenda",'')

    #Recuperando parametros de estilização do gráfico
    label_font_size = params.get("label_font_size", 18)
    label_font_weight = params.get("label_font_weight", "bold")

    title_font_size = params.get("title_font_size", 20)
    title_font_weight = params.get("title_font_weight", "bold")

    tick_font_weight =  params.get("tick_font_weight", "bold")
    tick_font_size = params.get("tick_font_size", 14)

    legenda_font_size = params.get("legenda_font_size", 16)

    reta_tendencia_data = params.get("reta_tendencia_data", [])
    reta_tendencia_color = params.get("reta_tendencia_color",['darkmagenta'])
    reta_tendencia_label = params.get("reta_tendencia_label", "Reta de Tendência")
    reta_tendencia_ordem = params.get("reta_tendencia_ordem",1)
    interval_yticker = params.get("interval_yticker")

    linestyle = params.get("linestyle",'-')
    marker = params.get("marker","o")
    linewidth = params.get("linewidth", 1.5)

    df_filtered = df[ (df.index > start_date) & (df.index < end_date) ]
    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)

    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)
    legenda_tag= []
    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots()
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()

    if(error):
        if(label_legenda == ''):
            label_legenda = 'Erro'
        
        if(abs_error):
            error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
            if(rolling_time>0):
                plot, =plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time).mean(), linestyle=linestyle, marker=marker, linewidth=linewidth, label= f'{label_legenda} (Absoluto)');
            else:
                plot, = plt.plot_date(df_filtered.index, error_abs, linestyle=linestyle, marker=marker, label="Erro");
            legenda_tag.append(plot)

        
        else:
            error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
            if(rolling_time>0):
                plot_legenda, = plt.plot_date(df_filtered.index, error_.rolling(rolling_time).mean(), linestyle=linestyle, marker=marker, linewidth=linewidth, label="Erro Tendência");
                legenda_tag.append(plot_legenda)
            else:
                plot, = plt.plot_date(df_filtered.index, error_, linestyle=linestyle, marker=marker, linewidth=linewidth, label="Erro");
                legenda_tag.append(plot)

        
    else:
        for variable in variables_array:

            if((label_legenda == '' ) | (len(variables_array) > 1 )):
                label_legenda = variable

            if(tendencia):
                plot, = plt.plot_date(df_filtered.index, df_filtered[variable], linestyle=linestyle, marker=marker, linewidth=linewidth,label=label_legenda);
                legenda_tag.append(plot)
                if(rolling_time>0):
                    plt_tendencia, = plt.plot_date(df_filtered.index, df_filtered[variable].rolling(rolling_time).mean(), linestyle=linestyle, marker=marker, linewidth=linewidth, label=f'{label_legenda} (Tendência)');
                    legenda_tag.append(plt_tendencia)                    
            else:                            
                if(rolling_time>0):
                    plt_tendencia, = plt.plot_date(df_filtered.index, df_filtered[variable].rolling(rolling_time).mean(), linestyle=linestyle, marker=marker, linewidth=linewidth, label=f'{label_legenda}');
                    legenda_tag.append(plt_tendencia)                    
                else:
                    plot, = plt.plot_date(df_filtered.index, df_filtered[variable], linestyle=linestyle, marker=marker, linewidth=linewidth,label=label_legenda);
                    legenda_tag.append(plot)
                        


    if(len(titulo)>0):        
        plt.title(titulo, fontsize=title_font_size, fontweight= title_font_weight)
    elif(error):
        plt.title('Error', fontsize=title_font_size, fontweight=title_font_weight)
    else:
        plt.title(' - '.join(variables_array), fontsize=title_font_size, fontweight= title_font_weight)

    ax.tick_params(labelsize=tick_font_size)
    plt.rcParams['figure.titleweight'] = tick_font_weight
    plt.rcParams['font.weight'] = tick_font_weight
    
    # Adicionando  da Reta de tendência 
    legenda_reta_tendencia = []
    if(reta_tendencia_data):
        for i in range(len(variables_array)):

            for reta in reta_tendencia_data:
                ini = pd.Timestamp(reta[0])
                fim = pd.Timestamp(reta[1])

                if(ini>fim):
                    raise(ValueError (f'O o período para o fit da reda de tendência da variável {df_filtered.columns[i]} está com a Data Início maior que Data Fim.'))
                
                df_filtrado = df_filtered[(df_filtered.index > ini) & (df_filtered.index < fim)]            
                x = np.arange(len(df_filtrado)) 
                y = df_filtrado[df_filtrado.columns[i]].values
                
                coefs = np.polyfit(x,y,reta_tendencia_ordem)
                ffit = np.poly1d(coefs) 
                
                df_filtrado['ffit'] = ffit(x)
                legenda, = plt.plot(df_filtrado.index, df_filtrado['ffit'], color=reta_tendencia_color[i],  linestyle='--', label=f'{reta_tendencia_label}')
            legenda_reta_tendencia.append(legenda)
   
    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1]+ticks[2], ticks[2]))

    if(interval_yticker):
        ax.yaxis.set_major_locator(ticker.MultipleLocator(interval_yticker))   

    if(days_interval<2):
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(which='major', rotation=90, pad=60)

        ax.xaxis.set_minor_locator(minor_loc)
        ax.xaxis.set_minor_formatter(minor_formatter)
        ax.xaxis.set_tick_params(which='minor', rotation=90)
    else:
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_tick_params(which='major', rotation=90, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)

    if(len(ylabel)>0):
        plt.ylabel(ylabel, fontsize=label_font_size, fontweight = label_font_weight)
        
    if(len(xlabel)>0):
        plt.xlabel(xlabel, fontsize=label_font_size, fontweight = label_font_weight)

    #Dia Destaque
    legenda_data_line = []
    dia_destaque_data = params.get("dia_destaque_data",[])
    if(len(dia_destaque_data) > 0):
        color_dia = params.get("dia_destaque_color", 'r')
        label_dia = params.get('dia_destaque_label', "Dia Destaque")
        
        for dia in dia_destaque_data:                
            if( ( pd.to_datetime(dia,format='%d/%m/%Y') >= pd.to_datetime(start_date,format='%d/%m/%Y'))
             & ( pd.to_datetime(dia,format='%d/%m/%Y') <= pd.to_datetime(end_date,format='%d/%m/%Y')) ):
                plt.axvline(x=dia, color = color_dia, lw=2)
                line_limpeza = Line2D([0], [0], color=color_dia, lw=2)
                line_limpeza.set_label(label_dia)
                legenda_data_line.append(line_limpeza)

    # Data Blocos (True, False, Bloco destaque)
    legenda_bloco = []   
    tipos_blocos = ["treino_true", "treino_false", "bloco_destaque"]
    dic_bloco = {"treino_true":["green", "Treino (limpo)"], "treino_false": ["red", "Treino (sujo)"], "bloco_destaque": ["yellow", "Bloco Destaque"]}
    
    for bloco in tipos_blocos:
        bloco_data = params.get(f"{bloco}_data")
        if(bloco_data and len(bloco_data)>0):
            color_bloco = params.get(f'{bloco}_color', dic_bloco[bloco][0])
            label_bloco = params.get(f'{bloco}_label', f'Período de {dic_bloco[bloco][1]}')
            alpha_bloco = params.get(f'{bloco}_alpha', 0.2)
            
            for data in bloco_data: 
                ini = pd.Timestamp(data[0])
                fim = pd.Timestamp(data[1])
                if(ini>fim):
                    raise(ValueError(f'O parametro {bloco} está com a Data Início maior que Data Fim.'))
                plt.axvspan(ini,fim, color=color_bloco, alpha=alpha_bloco)
                legenda = mpatches.Patch(color=color_bloco, label=label_bloco,alpha=alpha_bloco)
            legenda_bloco.append(legenda)
    
    if(show_legenda and ( len(legenda_tag)>0 or len(legenda_data_line)>0 or len(legenda_bloco)>0)):
        plt.legend(handles=legenda_tag + legenda_data_line + legenda_bloco + legenda_reta_tendencia, fontsize=legenda_font_size, loc='best')
    
    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=150, bbox_inches='tight')

    plt.show() 

    # Removendo estilos        
    plt.clf()
    plt.close()