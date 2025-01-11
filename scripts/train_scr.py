import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import os

# 1. Загрузка данных
print("Loading data...")
data_path = "data/processed/cleaned_data.csv"  # Указан путь к очищенным данным
data = pd.read_csv(data_path)

# Просмотр структуры данных
print("Data preview:")
print(data.head())
print(f"Number of rows in data: {len(data)}")
print(f"Columns: {data.columns}")
print(f"Missing values in each column:\n{data.isnull().sum()}")

# 2. Проверка данных
sequences = data['Sequence'].astype(str)
labels = data['Promoter'].astype(int)

# Проверка распределения меток
print(f"Labels distribution: {np.bincount(labels)}")

# 3. Обработка текстовых данных
print("Processing sequences...")
chars = sorted(list(set(''.join(sequences))))
char_to_idx = {ch: idx + 1 for idx, ch in enumerate(chars)}  # Индексируем с 1
vocab_size = len(char_to_idx) + 1
print(f"Vocabulary size: {vocab_size}")

# Преобразование последовательностей в индексы
encoded_sequences = [[char_to_idx[ch] for ch in seq] for seq in sequences]

# Паддинг последовательностей до максимальной длины
max_seq_length = max(len(seq) for seq in encoded_sequences)
padded_sequences = [seq + [0] * (max_seq_length - len(seq)) for seq in encoded_sequences]
padded_sequences = np.array(padded_sequences)
print(f"Shape of padded_sequences: {padded_sequences.shape}")

# 4. Разделение данных на обучающую и тестовую выборки
indices = np.arange(len(padded_sequences))
np.random.seed(42)
np.random.shuffle(indices)
padded_sequences = padded_sequences[indices]
labels = labels.iloc[indices]

X_train, X_test, y_train, y_test = train_test_split(
    padded_sequences, labels, test_size=0.2, random_state=42, stratify=labels
)
print(f"Train/Test split: {len(X_train)} train, {len(X_test)} test")

# 5. Датасет и DataLoader
class PromoterDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.long)
        self.labels = torch.tensor(labels.values, dtype=torch.float32)

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]

train_dataset = PromoterDataset(X_train, y_train)
test_dataset = PromoterDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# 6. Модель
class PromoterLSTM(nn.Module):
    def __init__(self, vocab_size, embed_size, lstm_units, dropout_rate):
        super(PromoterLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.lstm = nn.LSTM(embed_size, lstm_units, batch_first=True)
        self.dropout = nn.Dropout(dropout_rate)
        self.fc = nn.Linear(lstm_units, 1)

    def forward(self, x):
        x = self.embedding(x)
        _, (hidden, _) = self.lstm(x)
        hidden = hidden.squeeze(0)
        x = self.dropout(hidden)
        return torch.sigmoid(self.fc(x))

# 7. Грид-сёрч по гиперпараметрам
grid_params = {
    'embed_size': [16, 32],
    'lstm_units': [32, 64],
    'dropout_rate': [0.2, 0.3],
    'batch_size': [16, 32]
}

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

best_model = None
best_accuracy = 0
history_list = []

if not os.path.exists('models'):
    os.makedirs('models')

for embed_size in grid_params['embed_size']:
    for lstm_units in grid_params['lstm_units']:
        for dropout_rate in grid_params['dropout_rate']:
            print(f"Testing configuration: embed_size={embed_size}, lstm_units={lstm_units}, dropout_rate={dropout_rate}")
            
            model = PromoterLSTM(vocab_size, embed_size, lstm_units, dropout_rate).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
            criterion = nn.BCELoss()

            # Обучение
            train_losses, val_losses = [], []
            for epoch in range(20):
                model.train()
                train_loss = 0
                for sequences, labels in train_loader:
                    sequences, labels = sequences.to(device), labels.to(device)

                    optimizer.zero_grad()
                    outputs = model(sequences).squeeze()
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    train_loss += loss.item()
                
                train_losses.append(train_loss / len(train_loader))
                
                # Валидация
                model.eval()
                val_loss = 0
                with torch.no_grad():
                    for sequences, labels in test_loader:
                        sequences, labels = sequences.to(device), labels.to(device)
                        outputs = model(sequences).squeeze()
                        loss = criterion(outputs, labels)
                        val_loss += loss.item()

                val_losses.append(val_loss / len(test_loader))
                print(f"Epoch {epoch + 1}, Train Loss: {train_losses[-1]:.4f}, Val Loss: {val_losses[-1]:.4f}")

                # Early stopping
                if epoch > 2 and val_losses[-1] > min(val_losses[-3:]):
                    print("Early stopping.")
                    break

            # Оценка модели
            model.eval()
            y_true, y_pred = [], []
            with torch.no_grad():
                for sequences, labels in test_loader:
                    sequences, labels = sequences.to(device), labels.to(device)
                    outputs = model(sequences).squeeze()
                    y_true.extend(labels.cpu().numpy())
                    y_pred.extend((outputs.cpu().numpy() > 0.5).astype(int))

            accuracy = np.mean(np.array(y_true) == np.array(y_pred))
            print(f"Test Accuracy: {accuracy:.4f}")

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = model
                torch.save(model.state_dict(), "models/best_model_weights.pth")

            history_list.append({
                'embed_size': embed_size,
                'lstm_units': lstm_units,
                'dropout_rate': dropout_rate,
                'accuracy': accuracy
            })

# 8. Итоговые результаты
print(f"Best model accuracy: {best_accuracy:.4f}")
print("All configurations and results:")
with open('models/training_report.txt', 'w') as f:
    for h in history_list:
        f.write(str(h) + '\n')
        print(h)

# 9. Сохранение графика обучения
plt.figure(figsize=(10, 5))
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Training and Validation Loss')
plt.savefig('models/training_loss.png')

# 10. Оценка лучшей модели
print("Evaluating best model on random sequences...")
if best_model:
    best_model.load_state_dict(torch.load("models/best_model_weights.pth"))
    best_model.eval()
    random_indices = np.random.choice(len(X_test), size=20, replace=False)
    random_sequences = X_test[random_indices]
    random_labels = y_test.iloc[random_indices]
    y_true, y_pred = [], []
    with torch.no_grad():
        for seq, label in zip(random_sequences, random_labels):
            seq_tensor = torch.tensor(seq, dtype=torch.long).unsqueeze(0).to(device)
            output = best_model(seq_tensor).item()
            y_true.append(label)
            y_pred.append(int(output > 0.5))

    print("Random Sequences Evaluation:")
    report = classification_report(y_true, y_pred, digits=4)
    print(report)
    with open('models/final_evaluation_report.txt', 'w') as f:
        f.write(report)
