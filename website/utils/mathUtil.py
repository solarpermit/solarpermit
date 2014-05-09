

class MathUtil():
    
    def is_number(self, s):
        try:
            float(s.replace(',', ''))
            return True
        except ValueError:
            return False        
    
    def round(self, num):
        if (num > 0):
            return int(num+.5)
        else:
            return int(num-.5)    