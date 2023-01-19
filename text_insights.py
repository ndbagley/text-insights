
from collections import defaultdict, Counter
from nltk.corpus import stopwords
import nltk
import pandas as pd
import sankey as sk
import matplotlib.pyplot as plt
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
stop_words = set(stopwords.words('english'))


class TextInsight:
    """ This class is for gaining insights through text using visualizations.
    This class has three different visualizations it can display.
    1. A sankey diagram that shows the relationship between each text and the most frequently occurring words
    2. A subplot of pie charts showing the breakdown of the parts of speech within each text
    3. A line chart plotting the top k most frequently occurring word for each text against how often the word occurs"""

    def __init__(self):
        """ Constructor
            data: a dictionary storing all relevant information about each text """

        self.data = defaultdict(dict)

    def _save_results(self, label, results):
        """ Saves the file-specific results in the state data
            label: the label to use as a reference to this specific set of results
            results: the data that was extracted using the parser """

        # storing each piece of the results in the state 'data' dictionary
        for k, v in results.items():
            self.data[k][label] = v

    @staticmethod
    def _default_parser(filename, stopwords):
        """ Default parser to read, clean, and extract data from given text
            filename: given file to extract text information from (works for txt files) """

        # opening the file and getting rid of newline characters
        with open(filename, 'r', encoding='utf8') as f:
            words = f.read().replace('\n', '')

        # normalizing the text
        normalized = TextInsight._normalize_text(words)
        # removing stopwords to obtain final list of words
        final_words = TextInsight._load_stop_words(normalized, stopwords)

        # creating a list of the words paired with their part of speech
        pos_tags = nltk.pos_tag(final_words)
        pos = [x[1] for x in pos_tags]
        pos = [x[:2] for x in pos]

        # keeping the results in a dictionary
        results = {
            'wordcount': Counter(final_words),
            'poscount': Counter(pos),
            'numwords': len(final_words),
        }

        return results

    @staticmethod
    def _normalize_text(words):
        """ Used to normalize the given chunk of text by removing punctuation, converting to lowercase,
        and eliminating stopwords
            words: the string that is to be normalized """

        # creating a punctuation list
        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

        # removing all punctuation from the text
        new_words = words
        for c in words:
            if c in punc:
                new_words = new_words.replace(c, '')

        # converting the text to lowercase
        new_words = new_words.lower()

        # converting the block text into a list of words
        as_list = new_words.split()

        return as_list

    @staticmethod
    def _load_stop_words(text, stopwords):
        """ Removes all stop words from the provided text.
            text: the list of text to remove stopwords from
            stopwords: the list of stopwords to remove from the given text """

        # removing stopwords and creating a filtered list
        filtered_text = []
        for w in text:
            if w not in stopwords:
                filtered_text.append(w)

        return filtered_text

    def load_text(self, filename, label="", parser=None, stopwords=stop_words):
        """ Registers the text file with the NLP framework.
            filename: name of the file that is going to be read and parsed
            label: the given label for the file that will be used as a reference in data storage
            parser: the parser that will extract data from text. By default it uses _default_parser()
            stopwords: the list of stopwords to remove from text. By default it uses the nltk list of stopwords"""

        # using default parser if parameter is None
        if parser is None:
            results = TextInsight._default_parser(filename, stopwords)
        # otherwise using the given parser
        else:
            results = parser(filename, stopwords)

        # setting the label as the filename if none is provided
        if label == "":
            label = filename

        # storing the specific file data in the state data dictionary
        self._save_results(label, results)

    def wordcount_sankey(self, word_list=None, k=5):
        """ Creates a sankey diagram mapping each file to word counts
            word_list: the list of words to display as the target in the sankey diagram (defaults to None)
            k: the number of top-appearing words to show from each file (defaults to 5) """

        # pulling the wordcount data from the state data
        wc = self.data['wordcount']
        df = pd.DataFrame(columns=['label', 'word', 'count'])

        # using the words from word_list if present
        if word_list:
            for key, v in wc.items():
                for w in word_list:
                    print(v[w])
                    if v[w]:
                        df.loc[len(df.index)] = [key, w, v[w]]
        # otherwise using the k most common words in each text
        else:
            top_words = []
            for key, v in wc.items():
                top_words.append(v.most_common(k))
            top_words = [item for sublist in top_words for item in sublist]
            top_words = set([x[0] for x in top_words])
            for key, v in wc.items():
                for w in top_words:
                    if v[w]:
                        df.loc[len(df.index)] = [key, w, v[w]]

        # generate the sankey diagram
        sk.make_sankey(df, 'label', 'word', vals='count')

    def pos_piecharts(self):
        """ Creates a pie chart for each file showing the respective percentages of their parts of speech """

        # pulling the pos data from the state data
        pos = self.data['poscount']

        # creating mapping of pos codes to words
        pos_codes = {'JJ': 'adjective', 'NN': 'noun', 'RB': 'adverb', 'VB': 'verb'}

        # initializing a smoothed dictionary that will contain fewer parts of speech
        smoothed_pos = {}
        for k in pos.keys():
            smoothed_pos[k] = {}
        for k in smoothed_pos.keys():
            smoothed_pos[k]['other'] = 0

        # adding the respective counts of the parts of speech to a nested dictionary
        for k, v in pos.items():
            for k2, v2 in v.items():
                if k2 in pos_codes.keys():
                    smoothed_pos[k][pos_codes[k2]] = v2
                else:
                    smoothed_pos[k]['other'] += v2

        # creating dataframes for each file containing part of speech data
        df_list = []
        for k in smoothed_pos.keys():
            to_df = {'pos': list(smoothed_pos[k].keys()), 'count': list(smoothed_pos[k].values())}
            df = pd.DataFrame(to_df)
            df_list.append((k.upper(), df))

        # creating a figure to plot respective pie charts on
        fig, axs = plt.subplots(len(df_list))
        fig.tight_layout()

        # creating a color mapping for the charts to maintain consistency
        colors={'noun': 'red', 'verb': 'blue', 'adjective': 'green', 'adverb': 'yellow', 'other': 'orange'}
        # plotting each
        for i in range(len(df_list)):
            y = df_list[i][1]['count']
            labels = df_list[i][1]['pos']
            title = df_list[i][0]
            axs[i].set_title(title)
            axs[i].pie(y, labels=labels, autopct='%1.1f%%', shadow=True, colors=[colors[v] for v in labels])

        plt.show()

    def top_word_percentage(self, k=10):
        """ Creates a graph comparing the top-word usage of the different texts
            k: the number of top words to display in the graph for each text """

        # pulling the word count information from the state data
        freq = self.data['wordcount']

        # grabbing the top k words for each text
        top_k = []
        for key, v in freq.items():
            k_dict = {key: {}}
            for w, c in v.most_common(k):
                k_dict[key][w] = c
            top_k.append(k_dict)

        # converting the nested dictionaries to a list of tuples
        to_graph = []
        for t in top_k:
            for key, v in t.items():
                to_graph.append((key, list(v.values())))

        # generating x labels representing the ranking of word frequency
        x = [i for i in range(1, k + 1)]

        # plotting the lines
        for g in to_graph:
            plt.plot(x, g[1], label=g[0])
        plt.xlabel('Word Frequency Ranking')
        plt.ylabel('Word Frequency')
        plt.title('Word Frequency vs Word Ranking')
        plt.legend()
        plt.show()
