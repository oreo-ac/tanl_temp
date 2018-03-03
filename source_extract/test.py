
import sys
import re

if __name__ == '__main__':
    reference = "Charles K. Stevens"
    print(re.findall(r"[ ].[.][ ]", "Charles K. Stevens"))
    
    