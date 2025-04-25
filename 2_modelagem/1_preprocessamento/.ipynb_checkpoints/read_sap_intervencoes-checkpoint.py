{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import os\n",
    "import json"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def path_out(name):\n",
    "    path = os.path.join('out',name)\n",
    "    return(path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def read_csv(name):\n",
    "    df = pd.read_csv(path_out(name))\n",
    "    df['Data'] =pd.to_datetime(df['Data'])\n",
    "    df.index = df['Data']\n",
    "    df = df.drop('Data' , axis = 1)\n",
    "    df = df.drop('Data.1' , axis = 1)\n",
    "    return df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def dicionario():\n",
    "    name = 'dados_sap_processados_out.csv'\n",
    "    #name = 'dados_sap_out.xlsx'\n",
    "    df = read_csv(name)\n",
    "    \n",
    "    name = 'tabela_de_intervencoes_out.csv'\n",
    "    df_2 = read_csv(name)\n",
    "    \n",
    "    \n",
    "    df['Tp'].loc[df['Tp'].str.contains('Z8')] = 'Prev.'\n",
    "    df['Tp'].loc[df['Tp'].str.contains('Z')] = 'Corr.'\n",
    "    \n",
    "    df_2['intervencoes'] = 'Inter.'\n",
    "    \n",
    "    dicionario_sap = df['Tp'].to_dict()\n",
    "    dicionario_intervencoes = df_2['intervencoes'].to_dict()\n",
    "    \n",
    "    dicionario_important_dates = dicionario_intervencoes\n",
    "    dicionario_important_dates.update(dicionario_sap)\n",
    "    \n",
    "    return (dicionario_sap, dicionario_intervencoes, dicionario_important_dates)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "metadata": {},
   "outputs": [],
   "source": [
    "#name = 'tabela_de_intervencoes_out.csv'\n",
    "#df_2 = read_csv(name)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "metadata": {},
   "outputs": [],
   "source": [
    "#name = 'dados_sap_out.csv'\n",
    "#df = read_csv(name)\n",
    "#\n",
    "#df['Tp'].loc[df['Tp'].str.contains('Z8')] = 'M Preventiva'\n",
    "#df['Tp'].loc[df['Tp'].str.contains('Z')] = 'M Corretiva'\n",
    "#\n",
    "#dicionario_sap = df['Tp'].to_dict()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "metadata": {},
   "outputs": [],
   "source": [
    "#name = 'tabela_de_intervencoes_out.csv'\n",
    "#df_2 = read_csv(name)\n",
    "#dicionario_intervencoes = df_2['Motivo'].to_dict()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "metadata": {},
   "outputs": [],
   "source": [
    "#dicionario_sap,dicionario_intervencoes = dicionario()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "{Timestamp('2010-02-16 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2010-03-12 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2010-03-13 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2010-06-11 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2010-09-02 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2010-10-16 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2011-01-16 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2011-03-24 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2011-03-25 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2011-11-28 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2011-12-08 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2012-01-15 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2012-02-25 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2012-06-14 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2012-09-15 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2012-10-15 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2013-07-19 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2013-08-20 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2013-11-09 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2014-10-16 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2014-11-07 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2016-06-16 00:00:00'): 'M Preventiva',\n",
       " Timestamp('2017-10-03 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2018-01-17 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2018-04-05 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2018-04-18 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2018-05-03 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2018-08-20 00:00:00'): 'M Corretiva',\n",
       " Timestamp('2019-03-10 00:00:00'): 'M Corretiva'}"
      ]
     },
     "execution_count": 74,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#dicionario_sap"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
