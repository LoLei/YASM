# YASM
**Y**et **A**nother **S**ite **M**apper

Generate a (visual) site map free and open-source.

## Requirements
* [Graphviz](https://graphviz.readthedocs.io) or
* [Blockdiag](http://blockdiag.com/en/blockdiag/introduction.html)
  * with PDF support: `pip install "blockdiag[pdf]"`
* [Python-colorspace](https://python-colorspace.readthedocs.io)

## Usage
```
$ ./yasm.py -h
usage: yasm.py [-h] [-v] [-i] [-d DEPTH] [-wp WIDTHPADDING] [-hp HEIGHTPADDING] [-e {dot,blockdiag}] [-o {landscape,portrait}] [-t {pdf,svg}] [-s] file

positional arguments:
  file                  Input file - YACA JSON

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Verbosity of the output
  -i, --instant         View the output file immediately
  -d DEPTH, --depth DEPTH
                        Maximum depth of the sitemap (default unlimited)
  -wp WIDTHPADDING, --widthpadding WIDTHPADDING
                        Padding width between adjacent nodes
  -hp HEIGHTPADDING, --heightpadding HEIGHTPADDING
                        Padding height between adjacent nodes
  -e {dot,blockdiag}, --engine {dot,blockdiag}
                        Engine for output
  -o {landscape,portrait}, --orientation {landscape,portrait}
                        Orientation for blockdiag output
  -t {pdf,svg}, --type {pdf,svg}
                        Output file type
  -s, --sdsp            Treat subdomains same as slash path URL parts
```

## Example
The input file is the output of [YACA](https://github.com/LoLei/YASM#related), or JSON of the same format.

`./yasm.py ../yaca/output/brunch-io.json`

![YASM brunch.io output](https://raw.githubusercontent.com/LoLei/YASM/master/images/brunch-io.png "YASM brunch.io output")

`$ ./yasm.py ../yaca/output/nextjs-org.json -e blockdiag --orientation landscape -wp 30 -hp 10`

![YASM nextjs.org output](https://raw.githubusercontent.com/LoLei/YASM/master/images/nextjs-org.png "YASM nextjs.org output")
([full](https://github.com/LoLei/YASM/blob/master/images/nextjs-org.svg))

## Related
[YACA](https://github.com/LoLei/yaca) - **Y**et **A**nother **C**ontent **A**uditor  
Can be used as input for YASM.

## License
[CC BY-SA 4.0](https://github.com/LoLei/YASM/blob/master/yasm/LICENSE)

## Authors
* [@AlmostBearded](https://github.com/AlmostBearded)
* [@d4geiger](https://github.com/d4geiger)
* [@Erago3](https://github.com/Erago3)
* [@LoLei](https://github.com/LoLei)
