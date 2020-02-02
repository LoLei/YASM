# YASM
**Y**et **A**nother **S**ite **M**apper

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

## Related
[YACA](https://github.com/LoLei/yaca) - Yet Another Content Auditor

## Authors
* [@AlmostBearded](https://github.com/AlmostBearded)
* [@d4geiger](https://github.com/d4geiger)
* [@Erago3](https://github.com/Erago3)
* [@LoLei](https://github.com/LoLei)
