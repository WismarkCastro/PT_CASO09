##
# EDA para prueba técnica ANALISTA BASES DE DATOS (CASO 09)
# Realizada por Wismark Castro Gómez
# 02/05/2023
##

#Importe librerías
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc
from collections import Counter

#Carga/transformación de datos

infoInicial = pd.read_csv('disney_plus_titles.csv')
column_names = infoInicial.columns.tolist()
infoInicial["idx"] = infoInicial["show_id"].str.extract('(\d+)')
infoInicial = infoInicial[["idx"]+list(infoInicial.columns[:-1])]

type_value = infoInicial['type'].unique()
type_counts = pd.DataFrame({'type': type_value, 'ocurrencias': infoInicial['type'].value_counts()})
porcentajes = round((infoInicial['type'].value_counts()) /len(infoInicial) * 100, 2)

if infoInicial['title'].isnull().values.any():
    mensaje = "Hay valores faltantes en la columna"
else:
    mensaje = "No hay valores faltantes en la columna"

top_directors = infoInicial['director'].value_counts().head(5)
top_directors_list = list(top_directors.items())
top_directors_df = pd.DataFrame(top_directors_list, columns=['director', 'count'])
top_directors_df = top_directors_df.head(5)

nombres_separados = infoInicial['cast'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)

top_nombres = nombres_separados.value_counts()
top_nombres = top_nombres.head(10)

top_nombres_df = pd.DataFrame({'nombre': top_nombres.index, 'frecuencia': top_nombres.values})

conteo_nombres = nombres_separados.groupby(nombres_separados).nunique().sort_values(ascending=False)
conteo_nombres_df = pd.DataFrame({'nombre': conteo_nombres.index, 'cantidad': conteo_nombres.values})

#limpieza de datos en Country
infoInicial_Country = infoInicial
infoInicial_Country = infoInicial_Country.assign(country=infoInicial_Country['country'].str.split(','))
infoInicial_Country = infoInicial_Country.explode('country')
infoInicial_Country = infoInicial_Country.dropna(subset=['country'])
countMap = infoInicial_Country.groupby('country').size().reset_index(name='count')

#Datos fecha formateo
infoInicial['date_added'] = pd.to_datetime(infoInicial['date_added'])
infoInicial['date'] = infoInicial['date_added'].dt.date
countByDay = infoInicial.groupby('date').size().reset_index(name='count')

#formato Rating

infoInicial_rat = infoInicial.dropna(subset=['rating'])
ratings = infoInicial_rat['rating'].unique()
#Diccionario de colores para el mapeo usando librería px
color_map = {rating: px.colors.qualitative.Prism[i % len(px.colors.qualitative.Prism)] for i, rating in enumerate(ratings)}

#Extraemos los dos escenarios, uno para las series por temporadas y otro para las peliculas por minutos
infoInicial_seasons = infoInicial[infoInicial['duration'].str.contains('Season')]
infoInicial_min = infoInicial[infoInicial['duration'].str.contains('min')]

#Extraemos la parte numérica de esta información
infoInicial_seasons['num_seasons'] = infoInicial_seasons['duration'].str.extract('(\d+)').astype(int)
infoInicial_min['num_min'] = infoInicial_min['duration'].str.extract('(\d+)').astype(int)

#extraemos las categorías de listed_in 
categorias = infoInicial['listed_in'].str.split(', ')
tabla_categorias = pd.DataFrame({'categoria': [item for sublist in categorias for item in sublist]})

tabla_categorias = tabla_categorias.groupby('categoria').size().reset_index(name='counts')

tabla_categorias = tabla_categorias.sort_values(by='counts', ascending=False).head(5)
tabla_categorias['porcentaje'] = tabla_categorias['counts'] / len(infoInicial) * 100

#campo descripción  
text = ' '.join(infoInicial['description'])
ignored_words = ['the', 'and', 'of', 'in', 'to', 'a', 'an', 'is', 'for', 'with', 'on', 'that', 'by', 'as', 'at', 'from', 'or', 'it', 'be', 'this', 'which', 'can', 'not', 'are', 'all', 'has', 'was', 'were', 'we', 'you', 'they', 'he', 'she', 'his', 'her', 'their', 'them', 'my', 'our', 'your', 'up', 'down', 'out', 'into', 'up', 'down', 'over', 'under', 'then', 'now', 'just', 'but', 'so', 'how', 'what', 'when', 'where', 'who', 'why', 'get', 'got', 'go', 'gone', 'come', 'came', 'been', 'do', 'does', 'did', 'done', 'make', 'made', 'take', 'took', 'taken', 'see', 'saw', 'seen', 'look', 'looked', 'like', 'really', 'very', 'much', 'more', 'some', 'many', 'most', 'other', 'each', 'every', 'own', 'than', 'too', 'very', 'will', 'would', 'could', 'should', 'might', 'may', 'must', 'shall', 'can', 'not', 'cannot', 'could', 'would', 'should', 'should', 'ought', 'i', 'me', 'mine', 'myself', 'we', 'us', 'ours', 'ourselves', 'you', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves']
word_list = [word.lower() for word in text.split()]
word_list = [word.strip('.,!?"-') for word in word_list if word not in ignored_words]
counter = Counter(word_list)
most_common_words = counter.most_common(50)
df_desc = pd.DataFrame(most_common_words, columns=['word', 'frequency'])


# Inicializando la app
app = Dash(__name__)



#Implementación de Graficos 
fig_show_idx = go.Figure(
    data=[go.Histogram(x=infoInicial['idx'])],
    layout=go.Layout(title='Distribución de valores en la columna "idx"')
)

fig_type = px.bar(type_counts, x='type', y='ocurrencias')
fig_type.update_traces(marker_color='#F6B1A7')

fig_title = px.scatter(infoInicial, x='release_year', y='rating', color='title', hover_name='title')

fig_dir = px.bar(top_directors_df, x='director', y='count', title='Top 5 directores')
fig_dir.update_layout(
    yaxis_title="Cantidad de películas"
)
fig_dir.update_traces(marker_color='#F49E91')

fig_cast = px.scatter(top_nombres_df, x='nombre', y='frecuencia', size='frecuencia', title='Top 10 nombres más frecuentes en "cast"')
fig_cast.update_layout(showlegend=False, xaxis_title='Nombre', yaxis_title='Frecuencia')


fig_country = px.choropleth(countMap, locations='country', locationmode='country names', color='count')

fig_date = px.line(countByDay, x='date', y='count')

fig_release_year = px.histogram(infoInicial, x='release_year', nbins=10)
fig_release_year.update_traces(marker_color='#F47966')

fig_rating = px.histogram(infoInicial, x='rating', color='rating', color_discrete_map=color_map, nbins=10, facet_col='type')

#Graficos de duración de contenido
fig_seasons = px.histogram(infoInicial_seasons, x='num_seasons', nbins=30)
fig_seasons.update_layout(title='Duración en temporadas en Disney+')
fig_seasons.update_traces(marker_color='#DE4C2D')

fig_min = px.histogram(infoInicial_min, x='num_min', nbins=30)
fig_min.update_layout(title='Duración en minutos en Disney+')
fig_min.update_traces(marker_color='#E7553E')

fig_categorias = px.bar(tabla_categorias, x='porcentaje', y='categoria', orientation='h',color='categoria', color_discrete_sequence=px.colors.qualitative.Prism)
fig_categorias.update_layout(title='Top 5 categorías')



fig_desc = px.bar(df_desc, x='frequency', y='word', orientation='h', color='word', 
                  labels={'frequency': 'Frecuencia', 'word': 'Palabra'}, 
                  title='Palabras más frecuentes en la descripción de los títulos')

fig_desc.update_layout(xaxis_title='Frecuencia', yaxis_title='Palabra', 
                       plot_bgcolor='rgba(0,0,0,0)', 
                       paper_bgcolor='rgba(0,0,0,0)',
                       font=dict(color='black'), 
                       hovermode='closest')



#Estructura página
app.layout = html.Div(
    [
    html.Hr(),
    html.Div([
        html.Img(src="https://previews.123rf.com/images/speedfighter/speedfighter1009/speedfighter100900085/7787783-espa%C3%B1a-o-espa%C3%B1ol-escudo-aislado-sobre-fondo-blanco.jpg",
                style={"height": "40px", "marginRight": "20px", "alignSelf": "flex-start"}),
        html.H1('Disney plus titles EDA - (Caso09)', style = {'textAlign': 'center', 'color': '#cf2e2e', 'fontSize': 30, "fontWeight": "bold"})
    ], style={"width": "100%", "display": "flex", "alignItems": "center", "justifyContent": "center"}),
    html.Hr(),
    html.Div(className='row' , children='Analisis de datos archivo prueba técnica', style = {'textAlign': 'center', 'color': '#ff6900','fontSize': 15}),
    html.Hr(),
    html.H4('Info general'),
    html.Div("Este dashboard presenta un análisis exploratorio de los datos de la plataforma de streaming Disney+. Los datos incluyen información sobre los programas disponibles en la plataforma, así como su popularidad y calificación, de manera que es más sencillo tener una idea general de la información respectiva."),
    html.H4('Campos(Columnas)'),
    #Info columnas - 1 - show_id
    html.Div([
        html.Div("Nombre: "+column_names[0], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Div("El campo contiene "+str(infoInicial['show_id'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Div("Si bien, el campo corresponde a un id, presenta letras en la información, de la siguiente manera: "),
        html.Div(""+infoInicial['show_id'].head(5)+", "),
        html.Div("Por lo que es sugerido, o reemplazar la parte literal de la información, o generar una columna nueva con unicamente el dato numérico(opción utilizada)"),
        html.Div("Entendiendo a idx como la parte numérica de la columna show_id tendríamos esta gráfica a total(Histograma)"),
       
        html.Div([
        # Gráfico de histograma
        dcc.Graph(
            id='histograma',
            figure=fig_show_idx
        )], style={'width': '60%', 'flex-direction': 'column', 'align-items': 'center'}),
        ] ),

    #Info columnas - 2 - type
    html.Div([
        html.Div("Nombre: "+column_names[1], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Div("El campo contiene "+str(infoInicial['type'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        dcc.Graph(
            id='grafico-type',
            figure=fig_type
        ),

        html.Div("Teniendo en cuenta el anterior gráfico podemos decir que el catálogo de películas es por mucho mayor al de series, siendo una diferencia de "+str(porcentajes[0])+"% frente a un "+str(porcentajes[1])+"%, respecto al total de los registros"),
    ]),

    #Info columnas - 3 - title
    html.Div([
        html.Div("Nombre: "+column_names[2], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['title'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul(mensaje),
        html.Ul(
            dcc.Graph(id='scatter-plot', figure=fig_title)
        ),
        html.Ul("Teniendo en cuenta el anterior gráfico podemos decir que para la categoría de rating [G] (Para todas las edades), la cantidad de titulos que se han generado se ha mantenido en la franja de 1937 a la actualidad, a diferencia de, por ejemplo, la categoría de titulos en PG-13, que se han visto representadas desde el año 1993 en adelante. (realizando la comparación junto con la variable -release year-). Esto nos podría indicar a demás, que la distribución de titulos mas grandes apuntan al público en general respecto a sectores especializados de la audiencia."),
    ]),

    #Info columnas - 4 - title
    html.Div([
        html.Div("Nombre: "+column_names[3], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['director'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con director.".format(len(infoInicial['director']) - infoInicial['director'].isna().sum())),
        html.Ul("Según esta información nuestros 5 directores mas comunes son:"),
        html.Ul([html.Ul(f'{director}: {count} veces') for director, count in top_directors_list]),
        dcc.Graph(
        id='top-directors-bar-chart',
        figure=fig_dir
        ),
        html.Ul("Podemos observar que nuestro director con más apariciones en nuestra data es "+str(top_directors_list[0][0])+" seguido de "+str(top_directors_list[1][0])+", lo que los hace los directores mas presentes en la plataforma, con una mayor cantidad de trabajos beneficiados por el sistema de streaming.")

    ]),

     #Info columnas - 5 - cast
    html.Div([
        html.Div("Nombre: "+column_names[4], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['cast'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("Sin embargo, esta columna cuenta con datos concatenados por comas, en donde mas de un actor trabaja en alguna producción, como por ejemplo: "+str(infoInicial['cast'].iloc[0])+" para nuestro primer registro. ("+str(infoInicial['title'].iloc[0])+")"),
        html.Ul("Teniendo en cuenta los actores únicos del set de datos, tenemos que hay un total de "+str(len(conteo_nombres_df))+", de los cuales destacan: "),
        dcc.Graph(id='grafico-top-nombres', figure=fig_cast),
        html.Ul(["El artista mas representativo en la muestra es {} con un total de {} lo cual es considerablemente bastante mas que su inmediato 'competidor', por una diferencia de {}.".format(
        top_nombres.index[0], top_nombres.iloc[0],top_nombres.iloc[0] - top_nombres.iloc[1])]),
    ]),
 
    #Info columnas - 6 - country
    html.Div([
        html.Div("Nombre: "+column_names[5], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['country'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(pais).".format(len(infoInicial['country']) - infoInicial['country'].isna().sum())),
        html.Ul("Se hace necesario realizar un proceso de limpieza a los datos, eliminando los registros NaN para facilidad de manejo y representación gráfica"),
        dcc.Graph(figure=fig_country),
        html.Ul("Podemos observar que la gran mayoría de presencia está en {}, indicando que es la región con mayor cantidad de registros en nuestro set de datos, con amplia mayoría, mientras que en regiones como latinoamérica unicamente se contempla presencia en Panamá, denotando que son estas regiones las mayoras productoras de contenido para la plataforma.".format(infoInicial_Country["country"].iloc[0]))
    ]),

    #Info columnas - 7 - date_added
    html.Div([
        html.Div("Nombre: "+column_names[6], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['date_added'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(fecha de inclusión).".format(len(infoInicial['date_added']) - infoInicial['date_added'].isna().sum())),
        dcc.Graph(figure=fig_date),
        html.Ul("Es notable que el crecimiento mas grande que se tuvo en la inclusión de contenido corresponde a la franja entre el 1 de Octubre a 12 de Noviembre de 2019, fecha que coindide con el lanzamiento de la plataforma, y para la cual se ha mantenido (según la data suministrada) constante en el tiempo con tres importantes momentos: Enero de 2020(28), Abril 3 de 2020(26), y Noviembre 12 de 2021(28), correspondiendo a alzas en la inclusión de contenido en la plataforma. "),
    ]),

    #Info columnas - 8 - release_year
    html.Div([
        html.Div("Nombre: "+column_names[7], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['release_year'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(fecha de estreno/libreración en plataforma).".format(len(infoInicial['release_year']) - infoInicial['release_year'].isna().sum())),
        dcc.Graph(figure=fig_release_year),
        html.Ul("Teniendo presente que el campo release_year podría hacer referencia al año en la que se estrenó el titulo, se puede notar una gran alza para la sección correspondiente al año 2010 - 2019, con un total de 554 estrenos/lanzamientos registrados en la data, fenómeno que se podría relacionar con la explosión de consumo de contenido on demand y el cambio del ecosistema de producción y distribución audiovisual, enfocado en el uso de las plataformas y su influencia en el hábito del consumo."),
    ]),

    #Info columnas - 9 - rating
    html.Div([
        html.Div("Nombre: "+column_names[8], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['rating'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(Clasificación/publico).".format(len(infoInicial['rating']) - infoInicial['rating'].isna().sum())),
        dcc.Graph(figure=fig_rating),
        html.Ul("La distribución de peliculas para el rating G es bastante mas grande respecto a las series, en donde predomina la categorpia TV-PG, y nota la ausencia de la cateogía G, indicandonos hacia que rango de publico está apostando la plataforma en cuantoa  su contenido."),
    ]),

    #Info columnas - 10 - duration
    html.Div([
        html.Div("Nombre: "+column_names[9], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['duration'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(Duración).".format(len(infoInicial['duration']) - infoInicial['duration'].isna().sum())),
        html.Ul("Para este caso en particular tenemos información de series distribuidas en temporadas y películas en minutos, por lo que las detallaremos por separado."),
        dcc.Graph(figure=fig_seasons),
        dcc.Graph(figure=fig_min),
        html.Ul("Tendriamos una visualización de la información en la que se aprecia que la gran mayoría de series tienen una duración de 1 temporada. El caso con la duración de las películas es en mayoría de 90 - 99 min en general, sin embargo, hay un dato interesante respecto a la distribución y es que se muestra una importante candidad de registros para la duración entre 0 a 9 min, lo que indicaría la presencia de series muy cortas, tal vez apuntando al consumo rápido y una mayor interactividad con el público y su tendencia por el contenido veloz."),
    ]),

    #Info columnas - 11 - listed_in
    html.Div([
        html.Div("Nombre: "+column_names[10], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['listed_in'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(Listada en/Categorías).".format(len(infoInicial['listed_in']) - infoInicial['listed_in'].isna().sum())),
        html.Ul("En este apartado tenemos información de más de una categoría en varios registros, sin embargo, las detallaremos por separado"),
        dcc.Graph(figure=fig_categorias),
        html.Ul("Para esta sección, tomaremos las principales 5 categorías del contenido del dataset, observando que Family y Animation son las más presentes en la plataforma. Esto probablemente a que la compañia tiene un reconocimiento mas que excelente por producciones que hacen parte de la cultura popular desde los inicios de la animación como industria de entretenimiento."),
    ]),

    #description
    #Info columnas - 11 - description
    html.Div([
        html.Div("Nombre: "+column_names[11], style = {'textAlign': 'left', "fontWeight": "bold"}),
        html.Ul("El campo contiene "+str(infoInicial['description'].nunique())+" valores únicos, lo que corresponde con "+str(len(infoInicial.index))+" registros."),
        html.Ul("De los anteriores, tenemos {} registros con dato(description).".format(len(infoInicial['description']) - infoInicial['description'].isna().sum())),
        html.H1(children='Histograma de frecuencia de palabras'),
        dcc.Graph(figure = fig_desc         
        ),
        html.Ul("En esta gráfica podemos dar una apreciación de las palabras mas frecuentes en la descripción de los títulos, dandonos una idea de que tanto se usan y su presencia en la plataforma. La información podría ser cotejada con el equipo creativo tanto para ver que tanto se está repitiendo y generar nuevas ideas, o verificar que ha funcionado y continuar con esa tendencia."),
    ]),

    ])



#Características HMTL
#app.css.append_css({
#    'external_url': 'https://fonts.googleapis.com/css?family=Montserrat:400,400i,700,700i&display=swap'
#})

# Ejecución de app
if __name__ == '__main__':
    app.run_server(debug=True)