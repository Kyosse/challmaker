# Somewhat Vaguely Graphical

| Name | Category | Difficulty |
| :---: | :---: | :---: |
| Somewhat Vaguely Graphical | [Steganography](../README.md) | [Medium](../../../Difficulty/Medium.md) |

This is a challenge I made for the [InterIUT2026 CTF](https://github.com/InterIUT-2026) organized by [HACK2G2](https://hack2g2.fr/).

The idea is to hide information inside SVG tags. Since this is a harder challenge, I wanted to make it multi-step.

- [Somewhat Vaguely Graphical](#somewhat-vaguely-graphical)
  - [Description](#description)
  - [Solution](#solution)
  - [Creation of the chall files](#creation-of-the-chall-files)

## Description

We know that some critical passwords are transmitted inside strange messages. Some teams of Null-Syndicate think they have found one of these messages.

Find the flag hidden inside this image.

---

Nous savons que certains mots de passe critique sont envoyés à travers des messages étranges. Des équipes de Null-Syndicate pensent avoir intercepté un de ces messages.

Retrouvez le mot de passe transmis dans cette image.

## Solution

The idea is to find multiple elements hidden inside the SVG file.

### Step 1. Find the JS script

When we open the SVG file in a browser, we can see that it is visually heavy.  
This is all a distraction. If we open it in an IDE, we can inspect its source code.  
SVG accepts many tags. The one we are looking for is the `script` tag, which works the same way as in HTML.

```
grep -n "<script\|milsec:\|CDATA" complex.svg | head -20
```

We find a `<script type="text/javascript">` tag of ~300 KB at the end of the file.  
It is unusual to find a `script` tag inside an SVG. While some use cases exist for animated SVGs, we need to check whether that is the case here.

---

### Step 2. Deobfuscation of JS

The script looks like this:

```javascript
/* NOC-7 · runtime overlay · do not edit */
(function(){
  var _0xkivspq = [
    String.fromCharCode(...[51,77,69,119,121,78,106,50,117]),
    String.fromCharCode(...[73,68,77,110,98,71,108,119]),
    // ... 3418 entrées ...
  ];
  var _0xorder = [1842, 7, 2901, 44, ...];   // ordre de reconstruction
  var _0xrebuilt = _0xorder.map(function(i){ return _0xkivspq[i]; });
  var _0xdecoded = _0xrebuilt.join('');
  var _0xresult  = atob(_0xdecoded);          // base64 → SVG brut
  ...
```

**Structure:**
- An array of chunks encoded with `String.fromCharCode`
- An array with the reconstruction order of the chunks
- `join('')` → base64 → `atob()` → output

You can either add a `console.log` and extract the output directly, or rewrite the logic as a script:

```python
import re, base64

with open("complex.svg", "r") as f:
    src = f.read()

# 1. Extraire le script
script = re.search(r'<!\[CDATA\[(.*?)//\]\]>', src, re.DOTALL).group(1)

# 2. Extraire les chunks (String.fromCharCode)
raw_chunks = re.findall(r'String\.fromCharCode\(\.\.\.\[([^\]]+)\]\)', script)
chunks = ["".join(chr(int(n)) for n in c.split(",")) for c in raw_chunks]

# 3. Extraire l'ordre
order_match = re.search(r'var _0x\w+ = \[([0-9,\s]+)\];\s*var _0x\w+ = _0x\w+\.map', script)
order = list(map(int, order_match.group(1).split(",")))

# 4. Reconstruire et décoder
b64 = "".join(chunks[i] for i in order)
file_svg = base64.b64decode(b64).decode()

with open("file.svg", "w") as f:
    f.write(file_svg)

print("[+] flag.svg extrait")
```
In the end, this script simply reconstructs a file from shuffled chunks.

---

### Step 3. File.svg

When we open the extracted file in a browser, we can see a 1000×3500 px image with multiple "steps" in 3 colors. *Inspired by [Haikei](https://app.haikei.app/)*  
Each step is supposed to represent a bit.
A narrow step represents a 0, and a wide step represents a 1.

```
grep -o '<path[^/]*/>' file.svg | wc -l   # → 3 paths + 1 rect
```

Each `path` tag draws one layer of steps. The front layer shows us how each step is structured.

```
M{x} 0  L{x} 0  L{x} 10  L{x'} 10  L{x'} 20 ...
```

Each row is 10 px tall. The x-coordinate of the right edge of each step is what varies.

| Value x | Meaning |
|----------|---------|
| ≈ 720 (× [0.9–1.1]) | bit **1** |
| ≈ 360 (× [0.9–1.1]) | bit **0** |

*Each row also has a small random variation applied, which must be accounted for.*

We therefore use a threshold to determine each bit's value.

---

### Step 4. Extraction of bits

Now that we understand the encoding, we can write a script to extract the bits.

```python
import re

with open("flag.svg", "r") as f:
    content = f.read()

# Premier path = couche frontale (HIGH_X=720 LOW_X=360)
d = re.findall(r'<path d="([^"]+)"', content)[0]

# Extraire tous les L x y (filtrer la fermeture à x=0)
lcommands = re.findall(r'L([\d.]+)\s+([\d.]+)', d)
data = [(float(x), float(y)) for x, y in lcommands if float(x) > 1.0]

# Chaque bit génère 2 L consécutifs au même x → prendre un sur deux
THRESHOLD = 540
bits = [1 if data[i][0] > THRESHOLD else 0 for i in range(0, len(data), 2)]

print(f"[+] {len(bits)} bits extraits")
# → 344 bits = 43 octets
```

The extracted bits do not make sense as plain text, so the data is likely encoded.

---

### Step 5. Find the XOR key

In the header comment of the file we can read that there is a `FILE KEY`.  
The value is `x or Y`, which hints that the key is used in a simple XOR.

>   ┌─────────────────────────────────────────────────────────────────┐  
  │  MILSEC INDUSTRIES — CLASSIFIED ASSET                           │  
  │  NEONREACH NETWORK OVERSIGHT COMMAND (NOC) · BUILD 7.4.1-ALPHA  │  
  │  CLEARANCE LEVEL : ULTRABLACK / SECTION 9-DELTA                 │  
  │  UNAUTHORIZED ACCESS IS A CAPITAL OFFENSE UNDER CORP-ACT 2081   │  
  │  FILE KEY : x or Y                                              │  
  └─────────────────────────────────────────────────────────────────┘  

We now need to find the actual key by looking for unusual elements in the file.  
There are multiple `path` tags, but four of them are unusually long.  
If we isolate each of those paths into a separate file, we can see that they spell out the key: `P-L-O-P`

If nothing is visible at first, it is because the paths have no color defined.  
At the end of each tag, the `stroke` and `fill` attributes specify the color.  
Since no color is set, we can add `fill="black"` to reveal the shapes.

```svg
<path d="..." stroke="none" fill="none" fill-rule="evenodd"/>
```

We can now update our script to apply XOR with the key we found.
```python
#!/usr/bin/env python3
import re, base64
from itertools import cycle

SVG_FILE  = "complex.svg"
KEY = b"PLOP"
THRESHOLD = 540

with open(SVG_FILE, "r") as f:
    src = f.read()

script = re.search(r'<!\[CDATA\[(.*?)//\]\]>', src, re.DOTALL).group(1)

raw_chunks = re.findall(r'String\.fromCharCode\(\.\.\.\[([^\]]+)\]\)', script)
chunks = ["".join(chr(int(n)) for n in c.split(",")) for c in raw_chunks]

order_match = re.search(
    r'var _0x\w+ = \[([0-9,\s]+)\];\s*var _0x\w+ = _0x\w+\.map', script
)
order = list(map(int, order_match.group(1).split(",")))
b64 = "".join(chunks[i] for i in order)
flag_svg = base64.b64decode(b64).decode()

d = re.findall(r'<path d="([^"]+)"', flag_svg)[0]
lcommands = re.findall(r'L([\d.]+)\s+([\d.]+)', d)
data = [(float(x), float(y)) for x, y in lcommands if float(x) > 1.0]
bits = [1 if data[i][0] > THRESHOLD else 0 for i in range(0, len(data), 2)]

key_bits = [int(b) for byte in KEY for b in f"{byte:08b}"]
bits_dec = [b ^ k for b, k in zip(bits, cycle(key_bits))]

flag = "".join(
    chr(int("".join(map(str, bits_dec[i:i+8])), 2))
    for i in range(0, len(bits_dec), 8)
    if len(bits_dec[i:i+8]) == 8
)
print(flag)
```
The script outputs `interiut{SVGs_are_really_fun_and_powerfull}` — that's the flag!


---

### Flag

```
interiut{SVGs_are_really_fun_and_powerfull}
```

---

## Creation of the chall files

The creation of the challenge is pretty straightforward. You need to make the primary file *[example](complex.svg)* and then add hidden elements.  
To create the SVG file that contains the flag, you can use the script [encode_flag.py](encode_flag.py).  
Feel free to adapt everything to your own theme.
