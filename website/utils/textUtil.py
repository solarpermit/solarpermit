import re
import unicodedata

class TextUtil():
    
    #remove special characters
    @staticmethod
    def clean(text):
        text = unicode(text)
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    
    #only allow centain characters
    @staticmethod
    def remove_special_chars(text):
        text = text.strip()
        text = re.sub('[^A-Za-z0-9\s.\-\.:;,_=\'\"]+', '', text) #only allow these chars
        text = re.sub('[\a]', '', text) #remove \a is same as \07
        return text
    
    @staticmethod
    def get_quoted_words(text):
        words = []
        index = 0
        word_start = None
        word_end = None
        for char in text:
            if char == '"' and word_start == None:
                word_start = index + 1
            elif char == '"':
                word_end = index
                words.append(text[word_start:word_end])
                word_start = None
                word_end = None
            index += 1
        return words
    
    #can handle None value
    @staticmethod
    def lower(text):
        if text != None:
            return text.lower()
        return None
    
    #get the first number from the text
    @staticmethod
    def get_first_number(text):
        #go backward to look for number
        has_number = False
        number = ''
        for char in text:
            if char in '.01234567890':
                number = number + char
                has_number = True
            elif has_number == True: #already has number but this is not, stop
                break
        return number
    
    #get the last number from the text
    @staticmethod
    def get_last_number(text):
        #go backward to look for number
        has_number = False
        number = ''
        for char in reversed(text):
            if char in '.01234567890':
                number = char + number
                has_number = True
            elif has_number == True: #already has number but this is not, stop
                break
        return number
    
    @staticmethod
    def get_hour_minute(text):
        hour = ''
        minute = ''
        separator_count = text.count(':')
        if separator_count > 0:
            segments = text.split(':')
            hour = TextUtil.get_last_number(segments[0])
            minute = TextUtil.get_first_number(segments[1])
        else:
            hour = TextUtil.get_first_number(text)
        if minute == '':
            minute = '00'
        return hour, minute
            
            