# design tokens
needs python 3
needs requests

Pulls in styles of elements within a figma file based on container frame.

based off [figmagic](https://github.com/mikaelvesavuori/figmagic)

[figma file](https://www.figma.com/file/J9q5TGVX4biCs9WL8l5Col/token-example?node-id=0%3A1)

run:
python3 pulltokens.py -k "API-KEY" -id FILE-ID

after run a json file is made called tokens