import math
import random

def random_color() : 
    #implémenter un compteur pour avoir le nombre de couleur désiré
    #créer un set 

    cal_color = random.randint(0, 16777215)
    gen_color = f"#{hex(cal_color)[2:].zfill(6)}" 
    return gen_color

#assigné les couleurs dans le set pour enlever les doublons 

# Appel de la fonction et affichage
color = random_color()
print(f"Couleur généree : {color}")

