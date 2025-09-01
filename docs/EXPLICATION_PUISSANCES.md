# Explication des Puissances dans RF Simulator

## Pourquoi la barre de droite affiche des valeurs négatives ?

### **C'est normal et correct !** 

Les valeurs négatives en dBm sont tout à fait normales dans une simulation RF. Voici pourquoi :

## Différence entre Puissance Émise et Puissance Reçue

### Puissance Émise (à l'antenne)
- **+30 dBm** = Puissance que l'antenne émet
- Cette valeur est positive et reste constante
- C'est la puissance à la source

### Puissance Reçue (dans l'environnement)
- **-27 dBm à -199 dBm** = Puissance qui arrive aux différents points
- Ces valeurs sont négatives car il y a des pertes
- C'est ce qui est affiché dans la barre de droite

## Formule de Calcul

```
Puissance Reçue = Puissance Émise - Pertes de Propagation

Exemples :
+30 dBm - 60 dB = -30 dBm    (signal fort)
+30 dBm - 120 dB = -90 dBm   (signal faible)
+30 dBm - 200 dB = -170 dBm  (signal très faible)
```

## Types de Pertes

1. **Perte en espace libre** : Augmente avec la distance
2. **Absorption par les matériaux** : Murs, bâtiments
3. **Réflexions multiples** : Trajets indirects
4. **Diffraction** : Contournement d'obstacles

## Interprétation des Valeurs

| Puissance Reçue | Qualité du Signal |
|-----------------|-------------------|
| > -30 dBm       | Excellent         |
| -30 à -70 dBm   | Bon              |
| -70 à -90 dBm   | Acceptable       |
| -90 à -120 dBm  | Faible           |
| < -120 dBm      | Très faible      |

## Conclusion

Les valeurs négatives sont **normales et attendues** dans une simulation RF. Plus la valeur est proche de 0, meilleur est le signal !
