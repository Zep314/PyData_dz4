import re
st = '16 830,00 ₽'

print("".join(re.findall('[0-9.,]',st)).replace(',','.'))
