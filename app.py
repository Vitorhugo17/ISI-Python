# imports
import os
import pandas as pd
import numpy as np
import warnings
from flask import Flask, request, Response
import json

warnings.filterwarnings('ignore')


app = Flask(__name__)


@app.route('/', methods=['POST'])
def home():
    if 'idUtilizador' in request.json:
        id = int(request.json['idUtilizador'])
        dataset = pd.read_json(json.dumps(request.json['data']))
    else:
        return Response(json.dumps({"message": "idUtilizador not included"}), status="400",  mimetype='application/json')

    quantidadeComprada = pd.DataFrame(dataset.groupby(['idUtilizador', 'idProduto'])['quantidade'].mean())

    quantidadeComprada['quantidadeCompras'] = dataset.groupby(['idUtilizador', 'idProduto'])['quantidade'].count()

    quantidadeComprada = quantidadeComprada.reset_index('idProduto')

    matrix = dataset.pivot_table(index="idUtilizador", columns="idProduto", values="quantidade")

    quantidadeComprada = quantidadeComprada.sort_values('quantidadeCompras', ascending=False)

    index = quantidadeComprada.index

    index = list(dict.fromkeys(index))

    resultado = {}
    
    for x in index:
        if x == id:
            idProduto = quantidadeComprada.at[x, 'idProduto']
            if isinstance(idProduto, int):
                user_rating = matrix[idProduto]

                similar = matrix.corrwith(user_rating)

                correlation = pd.DataFrame(similar, columns=['correlation'])
                correlation.dropna(inplace=True)
                correlation = correlation.join(quantidadeComprada['quantidadeCompras'])
                correlation.sort_values('correlation', ascending=False)
                correlation = correlation.reset_index()
                
                resultado = {'idUtilizador': x, 'idProduto': correlation['index'].iloc[1], 'certeza': correlation['correlation'].iloc[1]}
            else:
                user_rating = matrix[idProduto]

                similar = matrix.corrwith(user_rating)

                correlation = pd.DataFrame(similar, columns=['correlation'])
                correlation.dropna(inplace=True)
                correlation = correlation.join(quantidadeComprada['quantidadeCompras'])
                correlation.sort_values('correlation', ascending=False)
                correlation = correlation.reset_index()
        
                resultado = {'idUtilizador': int(x), 'idProduto': int(correlation['index'].iloc[1]), 'certeza': float(correlation['correlation'].iloc[1])}
                    
    return Response(json.dumps(resultado),  mimetype='application/json')

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
