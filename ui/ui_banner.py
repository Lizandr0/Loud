from rich.panel import Panel
import os
def baner(console):
    os.system('clear')
    text=('''[bold #9999FF]
 (                    
 )\ )           (     
(()/(       (   )\ )  
 /(_)) (   ))\ (()/(  
(_))   )\ /((_) ((_)) 
| |   ((_|_))(  _| |  
| |__/ _ \ || / _` |  
|____\___/\_,_\__,_|                      

[bold black on #CCCCFF]'Loud' music player by @Lizandr0 -
        ''')
    
    console.print(text, justify='center')