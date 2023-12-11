# HP-calc programs



## converting HP-15c program code to HP-42s code

use the tool 'conv15to42s.py' to convert HP-15c code to HP-42s code.

Tool creates a 1:1 transformation.
You need to review and rework the new program.

a)
e.g.:
```
conv15to42s.py hp15c/hp15c-afh-en/HP-15C_adv_p066.15c > hp15c/hp15c-afh-en/HP-15C_adv_p066.42s
```

b)
Now edit the program. Rename the lables,...


c) 
convert to raw file.
* [Use the ext2raw tool](https://thomasokken.com/free42/download/unsupported/txt2raw)

```
txt2raw.pl.py hp15c/hp15c-afh-en/HP-15C_adv_p066.42s
```


d)
Load program into HP-42s (free42, plus42, DM42)
'hp15c/hp15c-afh-en/HP-15C_adv_p066.42s.raw'


