import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from collections import Counter
import os

# Создание папки dashboard, если её нет
if not os.path.exists("dashboard"):
    os.makedirs("dashboard")

# Загрузка данных
data = pd.read_csv("data/processed/cleaned_data.csv")

# Функции анализа данных
def calculate_gc(seq):
    return (seq.count('G') + seq.count('C')) / len(seq) * 100

data['Length'] = data['Sequence'].str.len()
data['GC_Content'] = data['Sequence'].apply(calculate_gc)

# Дэшборд
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"])

app.layout = html.Div([
    html.H1("Анализ генетических данных", style={'text-align': 'center'}),

    html.Div([
        dcc.Graph(id='length-distribution'),
        dcc.Graph(id='gc-distribution'),
    ], className='row'),

    html.Div([
        dcc.Dropdown(
            id='kmer-dropdown',
            options=[{'label': f'{k}-меры', 'value': k} for k in range(2, 6)],
            value=3,
            placeholder="Выберите длину k-меров"
        ),
        dcc.Graph(id='kmer-histogram'),
    ], className='row'),

    html.Div([
        dcc.Graph(id='class-distribution')
    ], className='row'),

], className='container-fluid')

# Колбэки для обновления графиков
@app.callback(
    Output('length-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_length_distribution(k):
    fig = px.histogram(data, x='Length', title="Распределение длин последовательностей",
                       labels={'x': 'Длина последовательности', 'y': 'Частота'})
    return fig

@app.callback(
    Output('gc-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_gc_distribution(k):
    fig = px.histogram(data, x='GC_Content', title="Распределение GC-содержания",
                       labels={'x': 'GC-содержание (%)', 'y': 'Частота'}, nbins=50)
    return fig

@app.callback(
    Output('kmer-histogram', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_kmer_histogram(k):
    k = int(k)
    kmer_counts = Counter()

    for seq in data['Sequence']:
        for i in range(len(seq) - k + 1):
            kmer = seq[i:i + k]
            kmer_counts[kmer] += 1

    kmer_df = pd.DataFrame(kmer_counts.items(), columns=['k-mer', 'Count']).sort_values(by='Count', ascending=False).head(50)
    fig = px.bar(kmer_df, x='k-mer', y='Count', title=f"Частоты топ-{k}-меров",
                 labels={'k-mer': f'{k}-меры', 'Count': 'Частота'})
    return fig

@app.callback(
    Output('class-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_class_distribution(k):
    counts = data['Promoter'].value_counts()
    fig = px.pie(values=counts, names=['Non-Promoter', 'Promoter'], title="Распределение классов")
    return fig

# Сохранение метрик в файл
output_path = "dashboard/data_analysis_metrics.csv"
data_metrics = {
    "Metric": [
        "GC Content Mean", "GC Content Std", "Unique Sequences Ratio",
        "Average Sequence Length", "Min Sequence Length", "Max Sequence Length"
    ],
    "Value": [
        data['GC_Content'].mean(),
        data['GC_Content'].std(),
        len(data['Sequence'].unique()) / len(data),
        data['Length'].mean(),
        data['Length'].min(),
        data['Length'].max()
    ]
}
metrics_df = pd.DataFrame(data_metrics)
metrics_df.to_csv(output_path, index=False)
print(f"Metrics saved to {output_path}")

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
