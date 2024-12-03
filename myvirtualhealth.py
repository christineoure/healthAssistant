# -*- coding: utf-8 -*-
"""MyVirtualHealth.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qEMv-RyeVZVB3gYRheaVaVMybTwqFjtz

**Step 1: Import Libraries**
"""

# !pip install emoji

# !pip install spacy scispacy tensorflow
# !pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz

import seaborn as sns
import nltk
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest, chi2
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.naive_bayes import MultinomialNB
import re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
import pandas as pd
import nltk
from nltk.corpus import stopwords
from collections import Counter
import re
import nltk
import re
from bs4 import BeautifulSoup
nltk.download('punkt_tab')

"""**Step 2: Load the Dataset**"""

from google.colab import drive
drive.mount('/content/drive')

train_path = '/content/drive/MyDrive/Diseases/Medical Chatbot Dataset/train_data_chatbot.csv'
val_path = '/content/drive/MyDrive/Diseases/Medical Chatbot Dataset/validation_data_chatbot.csv'

train_data = pd.read_csv(train_path)
val_data = pd.read_csv(val_path)

# Merge the datasets into one
combined_data = pd.concat([train_data, val_data], ignore_index=True)

pd.set_option('display.max_colwidth', None)
combined_data.head()

combined_data.info()

combined_data.describe()

"""**Step 3: Visualize the Distribution of Labels (1 vs. -1)**"""

# Distribution of target labels (assuming there is a column for classification like 'intent')
combined_data['label'].value_counts()

sns.countplot(data=combined_data, x='label')
plt.title('Distribution of Labels')
plt.xlabel('Label')
plt.ylabel('Count')
plt.show()

"""**Step 4: Text Preprocessing**

a. Convert All Text to Lowercase

"""

combined_data['short_question'] = combined_data['short_question'].str.lower()
combined_data['short_answer'] = combined_data['short_answer'].str.lower()
combined_data

"""b. Tokenization"""

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

# Tokenize questions and answers
combined_data['tokens_question'] = combined_data['short_question'].apply(nltk.word_tokenize)
combined_data['tokens_answer'] = combined_data['short_answer'].apply(nltk.word_tokenize)

combined_data

"""Remove all the punctuations and numbers from the dataset"""

def preprocess_text(text):
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()
    # Remove non-alphanumeric characters
    text = re.sub(r'[^\w\s]', '', text)
    # Lowercase the text
    text = text.lower()
    return text

combined_data['short_question'] = combined_data['short_question'].apply(preprocess_text)
combined_data['short_answer'] = combined_data['short_answer'].apply(preprocess_text)
combined_data['tags'] = combined_data['tags'].apply(preprocess_text)

combined_data[['short_question', 'short_answer', 'tags']]

"""remove stopwords and add custom stopwords"""

# Load the necessary stopwords
nltk.download('stopwords')
english_stopwords = set(stopwords.words('english'))

# Sample function to extract potential medical terms
def extract_medical_terms(text):
    tokens = nltk.word_tokenize(text)
    words = [word.lower() for word in tokens if word.isalpha()]
    return words

# Combine all text fields to extract common words
all_text = " ".join(combined_data['short_question'].fillna('') + " " + combined_data['short_answer'].fillna(''))

# Extract words and calculate frequency
word_list = extract_medical_terms(all_text)
word_freq = Counter(word_list)


common_medical_terms = {word for word, count in word_freq.items() if count > 5}  # Adjust the frequency threshold

# Custom medical stopwords list
custom_medical_stopwords = {
    'symptoms', 'treatment', 'disease', 'condition', 'patients', 'medical', 'doctor',
    'infection', 'diagnosis', 'therapy', 'medicine', 'health', 'cure', 'clinical',
    'pain', 'fever', 'rash', 'virus', 'vaccine', 'bacteria', 'headache', 'flu',
    'cough', 'allergy', 'asthma', 'diabetes', 'hypertension', 'antibiotics',
    'antivirals', 'immunization', 'surgery', 'cancer', 'tumor', 'arthritis',
    'cardiovascular', 'diarrhea', 'fatigue', 'insomnia', 'inflammation',
    'antibiotic', 'antiviral', 'aspirin', 'ibuprofen', 'paracetamol', 'glucose',
    'cholesterol', 'blood', 'x-ray', 'ultrasound', 'radiotherapy', 'chemotherapy',
    'therapy', 'prescription', 'dose', 'side-effects', 'prescribe', 'recovery',
    'care', 'hospital', 'clinic', 'symptom', 'prescribed', 'tablet', 'capsule',
    'ointment', 'syrup', 'bacterial', 'swelling', 'anxiety', 'depression',
    'fracture', 'burn', 'scar', 'sprain', 'autoimmune', 'contagious'
}

# Combine custom medical stopwords with extracted terms and standard English stopwords
all_stopwords = english_stopwords.union(custom_medical_stopwords).union(common_medical_terms)

### 2. Remove Stopwords from the Dataset

# Function to remove stopwords from tokenized text
def remove_stopwords(token_list):
    if isinstance(token_list, list):
        return [word for word in token_list if word.lower() not in all_stopwords]
    return token_list

# Tokenize the 'short_question' and 'short_answer' columns for stopword removal
nltk.download('punkt')
combined_data['tokens_question'] = combined_data['short_question'].apply(nltk.word_tokenize)
combined_data['tokens_answer'] = combined_data['short_answer'].apply(nltk.word_tokenize)

# Apply stopword removal
combined_data['tokens_question'] = combined_data['tokens_question'].apply(remove_stopwords)
combined_data['tokens_answer'] = combined_data['tokens_answer'].apply(remove_stopwords)

# Display the cleaned data for verification
pd.set_option('display.max_colwidth', None)
combined_data[['tokens_question', 'tokens_answer']]



stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Example of applying lemmatization (alternatively, use stemming)
combined_data['lem_question'] = combined_data['tokens_question'].apply(
    lambda x: [lemmatizer.lemmatize(word) for word in x]
)
combined_data['lem_answer'] = combined_data['tokens_answer'].apply(
    lambda x: [lemmatizer.lemmatize(word) for word in x]
)

pd.set_option('display.max_colwidth', None)
combined_data

# Combine 'short_question' and 'short_answer' into 'combined_text'
combined_data['combined_text'] = combined_data['short_question'] + " " + combined_data['short_answer']

# Apply TF-IDF vectorization
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
X = tfidf_vectorizer.fit_transform(combined_data['combined_text'])  # Note: Do NOT use .toarray() here

# Target variable
y = combined_data['label']

def clean_text(text):
    # Remove punctuation, numbers, and special characters
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    return text

combined_data['cleaned_question'] = combined_data['short_question'].apply(clean_text)
combined_data['cleaned_answer'] = combined_data['short_answer'].apply(clean_text)

def remove_numbers_and_string_form_numbers(text):
    # Remove numbers (e.g., 123)
    text = re.sub(r'\d+', '', text)
    # Remove string form numbers (e.g., one, two, three)
    # You might need a more comprehensive list of string form numbers
    string_form_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    for num in string_form_numbers:
        text = text.replace(num, '')
    return text

# Apply the function to the 'short_question' and 'short_answer' columns
combined_data['short_question'] = combined_data['short_question'].apply(remove_numbers_and_string_form_numbers)
combined_data['short_answer'] = combined_data['short_answer'].apply(remove_numbers_and_string_form_numbers)

# Check the distribution of classes
class_counts = combined_data['label'].value_counts()

# Plot the distribution of classes
plt.figure(figsize=(8, 5))
sns.barplot(x=class_counts.index, y=class_counts.values, palette='viridis')
plt.title('Distribution of Classes (Labels)')
plt.xlabel('Label')
plt.ylabel('Count')
plt.xticks(rotation=0)
plt.show()

# Count the occurrences of each tag
tag_counts = combined_data['tags'].value_counts() # This line was commented out, uncomment it to define tag_counts

# Display the top 10 tags
top_n = 10
top_tags = tag_counts.head(top_n)

# Plot the top 10 tags
plt.figure(figsize=(10, 5))
sns.barplot(x=top_tags.index, y=top_tags.values, palette='viridis')
plt.title(f'Top {top_n} Tags Distribution')
plt.xlabel('Tags')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

top_n = 10
top_tags = tag_counts[:top_n]
sns.barplot(x=top_tags.index, y=top_tags.values, palette='viridis')
plt.title(f'Top {top_n} Tags')
plt.xlabel('Tags')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.show()

# Remove square brackets and single quotes from 'tags' column
combined_data['tags'] = combined_data['tags'].str.replace(r"[\[\]']", '', regex=True)

# Display the first few rows to verify the changes
combined_data[['tags']].head()

# Count the occurrences of each tag
tag_counts = combined_data['tags'].value_counts()

# Select the top 10 tags
top_10_tags = tag_counts.head(10)

# Plot the distribution of the top 10 tags
plt.figure(figsize=(10, 5))
sns.barplot(x=top_10_tags.index, y=top_10_tags.values, palette='viridis')
plt.title('Top 10 Tags Distribution (Cleaned)')
plt.xlabel('Tags')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.show()

unique_tags = combined_data['tags'].unique()

# Display the unique tags
print(f"Number of unique tags: {len(unique_tags)}")
print("Unique tags:")
# unique_tags
unique_tags[:10]

def handle_negations(text):
    words = text.split()
    negation_mapping = {"not": "not_", "no": "not_", "never": "not_", "none": "not_"}
    result = []
    negate = False
    for word in words:
        if word in negation_mapping:
            negate = True
            result.append(negation_mapping[word])
        elif negate:
            result.append(f"not_{word}")
            negate = False
        else:
            result.append(word)
    return " ".join(result)

combined_data['neg_handled_question'] = combined_data['cleaned_question'].apply(handle_negations)
combined_data['neg_handled_answer'] = combined_data['cleaned_answer'].apply(handle_negations)

from sklearn.model_selection import train_test_split

# Assuming 'combined_data' is the DataFrame with all data
# 'label' is the target variable

# Split data into features (X) and target (y)
X = combined_data.drop(columns=['short_question'])  # Features
y = combined_data['label']  # Target variable

# Train-test split (e.g., 80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Display the distribution of labels in the train and test sets to verify balance
print("Training set label distribution:")
print(y_train.value_counts(normalize=True))

print("\nTest set label distribution:")
print(y_test.value_counts(normalize=True))

# Print shapes of the train and test splits
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)

# Print sizes of the splits
print("\nNumber of samples in training set:", len(X_train))
print("Number of samples in test set:", len(X_test))

# Check class balance for the training set
print("Class distribution in y_train:")
print(y_train.value_counts(normalize=True))
print("\nAbsolute counts in y_train:")
print(y_train.value_counts())

# Check class balance for the testing set
print("\nClass distribution in y_test:")
print(y_test.value_counts(normalize=True))
print("\nAbsolute counts in y_test:")
print(y_test.value_counts())

# Plot distribution of labels in training set
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
sns.countplot(x=y_train)
plt.title('Training Set Label Distribution')
plt.xlabel('Label')
plt.ylabel('Count')

# Plot distribution of labels in testing set
plt.subplot(1, 2, 2)
sns.countplot(x=y_test)
plt.title('Testing Set Label Distribution')
plt.xlabel('Label')
plt.ylabel('Count')

plt.tight_layout()
plt.show()



# Assuming X_train still contains text columns
# Create a dictionary to store LabelEncoders for each column
label_encoders = {}

# Get all unique text columns from both train and test sets
all_text_columns = pd.concat([X_train, X_test]).select_dtypes(include=['object']).columns.unique()

# Fit LabelEncoders for each column and store them in the dictionary
for column in all_text_columns:
    # Create a new LabelEncoder for each column
    label_encoders[column] = LabelEncoder()
    # Combine unique values from both train and test for fitting
    all_unique_values = pd.concat([X_train[column].astype(str), X_test[column].astype(str)]).unique()
    label_encoders[column].fit(all_unique_values)

    # Transform both train and test sets using the fitted encoder
    if column in X_train.columns:  # Check if column exists in X_train
        X_train[column] = label_encoders[column].transform(X_train[column].astype(str))
    if column in X_test.columns:  # Check if column exists in X_test
        X_test[column] = label_encoders[column].transform(X_test[column].astype(str))

# Train the Logistic Regression model
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)
for column in X_test.select_dtypes(include=['object']).columns:
    le = label_encoders[column]
    X_test[column] = X_test[column].astype(str).map(lambda s: le.transform([s])[0] if s in le.classes_ else -1) # using -1 as an indicator for unknown values

# Predict on the test set
y_pred_lr = lr_model.predict(X_test)

# Evaluate the model
print("Logistic Regression Accuracy:", accuracy_score(y_test, y_pred_lr))
print("Logistic Regression Classification Report:\n", classification_report(y_test, y_pred_lr))

# Create and train the Decision Tree model
dt_model = DecisionTreeClassifier()
dt_model.fit(X_train, y_train)

# Predict on the test set
y_pred_dt = dt_model.predict(X_test)

# Evaluate the model
print("Decision Tree Accuracy:", accuracy_score(y_test, y_pred_dt))
print("Decision Tree Classification Report:\n", classification_report(y_test, y_pred_dt))

# Train Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predict and evaluate
y_pred_rf = rf_model.predict(X_test)
print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Random Forest Classification Report:\n", classification_report(y_test, y_pred_rf))

# Train Naive Bayes (suitable for TF-IDF / count-based features)
nb_model = MultinomialNB()

# Before fitting, adjust X_train to have non-negative values
X_train_non_negative = X_train.copy()  # Create a copy to avoid modifying the original DataFrame

# For each column, shift values to be non-negative
for column in X_train_non_negative.columns:
    min_val = X_train_non_negative[column].min()
    if min_val < 0:
        X_train_non_negative[column] = X_train_non_negative[column] - min_val


nb_model.fit(X_train_non_negative, y_train)  # Fit with non-negative data
# Predict and evaluate
y_pred_nb = nb_model.predict(X_test) # You might need to transform X_test as well
print("Naive Bayes Accuracy:", accuracy_score(y_test, y_pred_nb))
print("Naive Bayes Classification Report:\n", classification_report(y_test, y_pred_nb))

# !pip install joblib

import joblib
from google.colab import files  # For downloading files in Google Colab

# Save Logistic Regression model
joblib.dump(lr_model, 'logistic_regression_model.pkl')

# Download the model
files.download('logistic_regression_model.pkl')

# Save Decision Tree model
joblib.dump(dt_model, 'decision_tree_model.pkl')

# Download the model
files.download('decision_tree_model.pkl')

# Save Random Forest model
joblib.dump(rf_model, 'random_forest_model.pkl')

# Download the model
files.download('random_forest_model.pkl')