# Raiplaysoundrss

Script per lo scaricamento delle trasmissioni di Rai Play Sound sotto forma di feed RSS o di file audio.

Attualmente permette solo lo scaricamento degli audiolibri.

## Dipendenze

Fedora:

```
$ dnf install python3-requests python3-feedgen
```

Pip

```
$ pip install requests feedgen
```


## Utilizzo

L'elenco degli audiolibri è disponibile qui: https://www.raiplaysound.it/programmi/adaltavoce/audiolibri.

Per scaricare i file audio:

```
python3 raiplaysoundrss.py download-audio NAME OUTDIR
```

Dove `NAME` è il nome dell'audiolibro definito nell'URL (e.g.
`unannosullaltipiano` per
https://www.raiplaysound.it/audiolibri/unannosullaltipiano) e `OUTDIR` è la
directory in cui salvare i file audio.

Per generare il feed RSS:

```
python3 raiplaysoundrss.py download-rss NAME RSSFILE
```

Dove `NAME` è il nome dell'audiolibro definito nell'URL (e.g.
`unannosullaltipiano` per
https://www.raiplaysound.it/audiolibri/unannosullaltipiano) e `RSSFILE` è il
path in cui salvare il file RSS.

## Licenza

Copyright (C) 2023 Emanuele Di Giacomo emanuele@digiacomo.cc

Raiplaysoundrss è distribuito sotto licenza GPLv3.
