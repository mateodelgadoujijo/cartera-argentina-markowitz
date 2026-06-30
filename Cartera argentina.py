# Construyo la frontera eficiente de una cartera de activos argentinos
# Identifico la cartera de mínima varianza y la de máximo Sharpe 
# Analizo cómo se comporta a la luz del contexto macro/geopolítico del país.
# Cartera 50% energética (PAM,CEPU,YPF) y 50% financiera (GGAL,SUPV,BMA)
import seaborn as sns
import matplotlib.pyplot as plt
import yahooquery 
import pandas as pd
import numpy as np 
from yahooquery import Ticker
#Bloque 1: Bajando los datos
tickers=["PAM","CEPU","YPF","GGAL","SUPV","BMA"]

acciones = Ticker(tickers)

data=acciones.history(start="2025-06-29",end="2026-06-29")

precios= data["adjclose"].unstack(level="symbol")
#print(precios.head())#
#print(precios.shape)#
precios.to_csv("precios.csv")

#Bloque 2: Retornos y riesgo
#Paso 1--> Retornos diarios
retornos = precios.pct_change().dropna()
#print(retornos.head())#

#Paso 2--> Retorno esperado y volatilidad anualizados
retorno_anual = retornos.mean() * 252
volatilidad_anual= retornos.std() * (252 ** 0.5)
#print(retorno_anual)#
#print(volatilidad_anual)#

#Paso 3--> Matriz de varianzas y covarianzas
cov_anual = retornos.cov() * 252
#print(cov_anual)#

#Paso 4--> graficando las matrices de correlación
correlacion = retornos.corr()

sns.heatmap(correlacion, annot=True, cmap="coolwarm",vmin=0, vmax=1)
plt.title("Correlación entre activos")
plt.savefig("correlacion.png",dpi=300,bbox_inches="tight")
plt.show()


#Bloque 3--> simulando miles de carteras
n_carteras = 10000
ret_carteras= []
riesgo_carteras=[]
pesos_carteras = []

for i in range(n_carteras):
    pesos = np.random.random(6)
    pesos = pesos / np.sum(pesos)
    
    ret = np.dot(pesos, retorno_anual)
    riesgo = np.sqrt(np.dot(pesos.T, np.dot(cov_anual,pesos)))
    
    ret_carteras.append(ret)
    riesgo_carteras.append(riesgo)
    pesos_carteras.append(pesos)

#print(len(ret_carteras))
#print(max(ret_carteras),min(riesgo_carteras))
plt.figure()
plt.scatter(riesgo_carteras, ret_carteras, s=3)
plt.xlabel("Riesgo(volatilidad anual")
plt.ylabel("Retorno anual esperado")
plt.title("Carteras simuladas - ADRs argentinos")
plt.show()

#Bloque 4--> el ratio de sharpe
ret_carteras = np.array(ret_carteras)
riesgo_carteras = np.array(riesgo_carteras)
rf = 0.05
sharpe= (ret_carteras - rf) / riesgo_carteras

idx_sharpe = np.argmax(sharpe)
idx_minvar = np.argmin(riesgo_carteras)
#print(sharpe[idx_sharpe])

plt.figure()
plt.scatter(riesgo_carteras, ret_carteras, c=sharpe, cmap="viridis", s=3 )
plt.colorbar(label= "Ratio de Sharpe")
plt.scatter(riesgo_carteras[idx_sharpe], ret_carteras[idx_sharpe], c="red", marker="*", s=300,  label="Máx Sharpe")
plt.scatter(riesgo_carteras[idx_minvar], ret_carteras[idx_minvar], c="blue", marker="*",s=300, label="Mín varianza")
plt.xlabel("Riesgo(volatilidad anual)")
plt.ylabel("Retorno anual esperado")
plt.title("Frontera eficiente - ADRs argentinos")
plt.legend()
plt.show()


#Bloque 5--> hacia una cartera óptima
activos = retorno_anual.index
x = np.arange(len(activos))
ancho = 0.35

plt.figure()
plt.bar(x - ancho/2, pesos_carteras[idx_sharpe], ancho, label="Máx Sharpe")
plt.bar(x + ancho/2, pesos_carteras[idx_minvar], ancho, label="Mín varianza")
plt.xticks(x, activos)
plt.ylabel("Peso en la cartera")
plt.title("Composición de las carteras óptimas")
plt.legend()
plt.show()



#Bloque 6: graficando los retornos
base100 = precios / precios.iloc[0] * 100

plt.figure(figsize=(10,6))
for activo in base100.columns:
    plt.plot(base100.index, base100[activo], label=activo)
plt.xlabel("Fecha")
plt.ylabel("Retorno acumulado (base 100)")
plt.title("Evolución de los ADRs argentinos (base 100)")
plt.legend()
plt.show()
    

