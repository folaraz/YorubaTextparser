from tkinter.filedialog import askopenfilename
import os
from tkinter import *
from tkinter import ttk
import sys
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from collections import Counter


class Textparser(object):
    def __init__(self, ouput_text, text_file=None):
        self.text_file = text_file
        self.output_text = ouput_text
        self.stopwords = stopwords.words('english')
        self.sent_tok = sent_tokenize(self.output_text)
        self.word_tok = word_tokenize(self.output_text)
        self.opening_phrases = ['in the olden days', 'a long time ago', 'once upon a time', 'a great while ago',
                                'a long time ago','a story, a story, let it come, let it go']
        self.keyterms = ["sing", "singing", "song"]
        self.english_vocab = set(w.lower() for w in nltk.corpus.words.words())
        self.objects = ["plates", "wares", "raffia", "mats", "throne", "beancakes", "forest","village"
                        "trees", "tree", "house", "pit", "spears","clothes", "firewoood", "wood", " beads",
                        "stones", "bush", "gold", "meat", "jungle", "den", "iroko", "rock", "beehive", "drum",
                        "buckets", "spoon", "stick", "bowl", "water", "food", "web", "door", "court", "machete"
                        "rope", "arrow", "boat", "pot", "iron", "mat", "hoe", "cutlass", "yam"]

    def openings(self):
        story_text = self.sent_tok
        suspect_beg = story_text[:1]
        for sentences in suspect_beg:
            sent = sent_tokenize(sentences.lower())
        for openers in self.opening_phrases:
            if openers in sent[0]:
                return openers
        else:
            return "There isn't any opener in this folktale."

    def first_process(self):
        sentences = nltk.sent_tokenize(self.output_text)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chuncked_sentences = nltk.chunk.ne_chunk_sents(tagged_sentences, binary=True)

        def extract_entity_names(t):
            entity_names = []
            if hasattr(t, 'label') and t.label:
                if t.label() == 'NE':
                    entity_names.append(' '.join([child[0] for child in t]))
                else:
                    for child in t:
                        entity_names.extend(extract_entity_names(child))
            return entity_names
        entity_names = []
        for tree in chuncked_sentences:
            entity_names.extend(extract_entity_names(tree))
        return set(entity_names)

    def second_process(self):
        freq_word_controled = [wrds for wrds in self.word_tok if wrds.lower() not in self.stopwords]
        freq_word_controled = nltk.FreqDist(freq_word_controled)
        word_count = Counter(freq_word_controled)
        words_needed_in_text = []
        word_count.pop('.')
        word_count.pop(',')
        for words in word_count:
            if 20 > word_count[words] > 8:
                words_needed_in_text.append(words)
        for wrd in words_needed_in_text:
            if len(wrd) <=3:
                words_needed_in_text.pop(words_needed_in_text.index(wrd))
        return words_needed_in_text

    def summarized_text(self):
        summarized_text = []
        parser = PlaintextParser.from_file(self.text_file, Tokenizer("english"))
        summarizer = LexRankSummarizer()

        summary = summarizer(parser.document, 6)
        for sent in summary:
            summarized_text.append(sent)
        return summarized_text

    def get_object(self):
        props = [words for words in self.word_tok if words in self.objects]
        unique_obj = set(props)
        obj = [ob for ob in unique_obj]
        if obj:
            return obj
        else:
            return None

    def get_song(self):
        sentences_needed = []
        percent_eng = []
        percent_eng_dict = {}
        for sentences in self.sent_tok:
            s = sentences
            for keys in self.keyterms:
                if keys in s.lower():
                    index = self.sent_tok.index(sentences)
                    sentences_needed.append(self.sent_tok[index])
                else:
                    return 'No song in this folk tale'
        for items in sentences_needed:
            counter = 0
            words_sing_tok = word_tokenize(items)
            tok_sing = [w for w in words_sing_tok if w not in self.stopwords]
            for words in tok_sing:
                if words in self.english_vocab:
                    counter += 1
            percentage_english = (counter / len(tok_sing) * 100)
            percent_eng.append(percentage_english)
            percent_eng_dict[percentage_english] = items
        percent_eng.sort()
        if percent_eng == []:
            return "There is no song in this folktale."
        else:
            if percent_eng[0] >= 55:
                return "There is no song in this folktale."
            else:
                return self._clean_song(percent_eng_dict[percent_eng[0]])

    def _clean_song(self, song):
        song_tok = word_tokenize(song)
        for keys in self.keyterms:
            index=song_tok.index(keys)
            if index:
                break
        streamlined_song = song_tok[index:-index]
        processed_song = ' '
        for words in streamlined_song:
            words += ' '
            processed_song += words
        return processed_song


class Gui_Textparser(object):
    def __init__(self, master):
        self.tkObj = ttk
        self.root = master
        self.content = ttk.Frame(self.root,)
        self.bottomframe = Text(self.content, relief="sunken", width=300, height=300)
        File_descriptor = ttk.Label(self.content, text="Select File:")
        self.file_name = ttk.Entry(self.content)

        Browse_button = ttk.Button(self.content, text="Browse...", command=self.callback)
        Parse_button = ttk.Button(self.content, text="Parse", command=self.write_to_entry)
        Quit_button = ttk.Button(self.content, text="Quit", command=self.quit)
        Reset_button = ttk.Button(self.content, text="Reset", command=restart_program)

        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        File_descriptor.grid(column=0, row=0, sticky=E)
        self.file_name.grid(column=1, row=0, sticky=(E, W))
        Parse_button.grid(row=1, column=1)
        Browse_button.grid(row=0, column=2, sticky=W)
        Quit_button.grid(row=1, column=2, sticky=E)
        Reset_button.grid(row=1, column=0, sticky=W)
        self.bottomframe.grid(column=0, row=5, columnspan=5, rowspan=5, sticky=(N, S, E, W))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=3)
        self.content.columnconfigure(2, weight=3)
        self.root.rowconfigure(1, weight=1)

    def quit(self):
        quit()

    def callback(self):
        self.name = askopenfilename(filetypes=(("Text file", "*.txt"),
                                                ("document", "*.doc;*.docx")
                                                ))
        print(self.file_name.insert(END, os.path.split(self.name)[1]))

    def write_to_entry(self):
        with open(self.name, 'r') as in_file:
            text = in_file.read()
            outputstring = u' '.join(text.split())
        a, b, c, d, e, f = self.get_output(outputstring)
        self.bottomframe.insert('end', "=============================================================================="
                                       "=======THE OPENING OF THE FOLKTALE============================================="
                                       "==============================")
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', a)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', "==============================================================================="
                                       "SETTINGS OF THE FOLKTALE======================================================"
                                       "==============================")
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '                    FIRST ALGORITHM')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')

        self.bottomframe.insert('end', b)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')

        self.bottomframe.insert('end', '                   SECOND ALGORITHM')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', c)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '=============================================================================='
                                       '============PROPS OF THE FOLKTALE=============================================='
                                       '============================')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', d)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '==============================================================================='
                                       'SONG IN THE FOLKTALE==========================================================='
                                       '============================')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', e)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '==============================================================================='
                                       'SUMMARIZATION OF THE FOLKTALE================================================='
                                       '=============================')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', f)
        self.bottomframe.insert('end', '\n')
        self.bottomframe.insert('end', '\n')

        self.bottomframe.config(state=DISABLED)

    def get_output(self, outputstring):
        self.parser = Textparser(outputstring, text_file=self.name)
        return self.parser.openings(), self.parser.first_process(), self.parser.second_process(), \
               self.parser.get_object(), self.parser.get_song(), self.parser.summarized_text()


def restart_program():
    """Restart the current program again"""
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    master = Tk()
    me = Gui_Textparser(master)
    master.mainloop()
