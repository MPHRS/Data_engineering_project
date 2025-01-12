import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
from collections import Counter
import os

os.makedirs("dashboard", exist_ok=True)
DATA_PATH = "data/processed/cleaned_data.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
data = pd.read_csv(DATA_PATH)

def calculate_gc_content(sequence):
    if not sequence:
        return 0
    gc_count = sequence.count('G') + sequence.count('C')
    return (gc_count / len(sequence)) * 100

data['Length'] = data['Sequence'].str.len()
data['GC_Content'] = data['Sequence'].apply(calculate_gc_content)

app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
])

app.layout = html.Div([
    html.H1("Genetic Data Analysis", style={'text-align': 'center'}),

    html.Div([
        dcc.Graph(id='length-distribution'),
        dcc.Graph(id='gc-distribution'),
    ], className='row'),

    html.Div([
        dcc.Dropdown(
            id='kmer-dropdown',
            options=[{'label': f'{k}-mers', 'value': k} for k in range(2, 6)],
            value=3,
            placeholder="Select k-mer length"
        ),
        dcc.Graph(id='kmer-histogram'),
    ], className='row'),

    html.Div([
        dcc.Graph(id='class-distribution')
    ], className='row'),

], className='container-fluid')

@app.callback(
    Output('length-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_length_distribution(_):
    fig = px.histogram(data, x='Length', title="Sequence Length Distribution",
                       labels={'x': 'Sequence Length', 'y': 'Frequency'})
    return fig

@app.callback(
    Output('gc-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_gc_distribution(_):
    fig = px.histogram(data, x='GC_Content', title="GC Content Distribution",
                       labels={'x': 'GC Content (%)', 'y': 'Frequency'}, nbins=50)
    return fig

@app.callback(
    Output('kmer-histogram', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_kmer_histogram(k):
    if not k:
        return {}
    k = int(k)
    kmer_counts = Counter()
    for sequence in data['Sequence']:
        for i in range(len(sequence) - k + 1):
            kmer = sequence[i:i + k]
            kmer_counts[kmer] += 1

    kmer_df = pd.DataFrame(kmer_counts.items(), columns=['k-mer', 'Count'])
    kmer_df = kmer_df.sort_values(by='Count', ascending=False).head(50)
    fig = px.bar(kmer_df, x='k-mer', y='Count', title=f"Top {k}-mer Frequencies",
                 labels={'k-mer': f'{k}-mers', 'Count': 'Frequency'})
    return fig

@app.callback(
    Output('class-distribution', 'figure'),
    Input('kmer-dropdown', 'value')
)
def update_class_distribution(_):
    if 'Promoter' not in data.columns:
        raise ValueError("Column 'Promoter' not found in the dataset")

    counts = data['Promoter'].value_counts()
    fig = px.pie(values=counts, names=counts.index, title="Class Distribution")
    return fig

# Save metrics
METRICS_PATH = "dashboard/data_analysis_metrics.csv"
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
metrics_df.to_csv(METRICS_PATH, index=False)
print(f"Metrics saved to {METRICS_PATH}")

# Run app
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')


