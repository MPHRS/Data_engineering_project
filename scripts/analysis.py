import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from collections import Counter

sns.set_theme(style="darkgrid")

def plot_sequence_lengths(data):
    """Гистограмма распределения длин последовательностей."""
    data['Length'] = data['Sequence'].str.len() 
    plt.figure(figsize=(10, 6))
    sns.histplot(data['Length'], bins=50, kde=False, color='blue')  
    plt.title("Распределение длин последовательностей")
    plt.xlabel("Длина последовательности")
    plt.ylabel("Частота")
    plt.tight_layout()
    plt.savefig("sequence_length_distribution.png")
    plt.close()

def plot_kmer_histogram(data, k=3):
    """Гистограмма частот k-меров."""
    sequences = data['Sequence']
    kmer_counts = Counter()

    for seq in sequences:
        for i in range(len(seq) - k + 1):
            kmer = seq[i:i+k]
            kmer_counts[kmer] += 1

    kmer_df = pd.DataFrame(kmer_counts.items(), columns=['k-mer', 'Count']).sort_values(by='Count', ascending=False)
    top_kmers = kmer_df.head(50)

    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_kmers, x='k-mer', y='Count', palette="viridis")
    plt.title(f"Частоты топ-{k}-меров")
    plt.xlabel("k-меры")
    plt.ylabel("Частота")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("kmer_histogram.png")
    plt.close()

def plot_class_distribution(data):
    """Круговая диаграмма распределения классов."""
    counts = data['Promoter'].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=['Non-Promoter', 'Promoter'], autopct='%1.1f%%', startangle=90, colors=['red', 'green'])
    plt.title("Распределение классов")
    plt.savefig("class_distribution.png")
    plt.close()

def plot_gc_content(data):
    """Распределение GC-содержания."""
    def calculate_gc(seq):
        return (seq.count('G') + seq.count('C')) / len(seq) * 100

    data['GC_Content'] = data['Sequence'].apply(calculate_gc)
    plt.figure(figsize=(10, 6))
    sns.histplot(data['GC_Content'], bins=50, kde=True, color='purple')
    plt.title("Распределение GC-содержания")
    plt.xlabel("GC-содержание (%)")
    plt.ylabel("Частота")
    plt.savefig("gc_content_distribution.png")
    plt.close()

def main(input_file):
    data = pd.read_csv(input_file)

    print("Выполняется анализ данных...")
    plot_sequence_lengths(data)
    plot_kmer_histogram(data)
    plot_class_distribution(data)
    plot_gc_content(data)
    print("Анализ завершен. Графики сохранены.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Анализ генетических данных.")
    parser.add_argument('--input', required=True, help="Путь к входному CSV файлу.")
    args = parser.parse_args()

    main(args.input)
