import sys
try:
    with open('glb_output.log', 'rb') as f:
        d = f.read()
    text = d.decode('utf-16le', errors='ignore')
    with open('out.log', 'w', encoding='utf-8') as f:
        f.write(text)
except Exception as e:
    with open('out.log', 'w', encoding='utf-8') as f:
        f.write(str(e))
