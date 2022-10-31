\ Model EV_distribution
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 [ 0.15125 EV_P[0] ^2 - 1.1 EV_P[0] * lambda + 0.98 EV_P[1] ^2
   - 2.8 EV_P[1] * lambda + 4 lambda ^2 ] / 2 
Subject To
 A: 0.275 EV_P[0] + 0.7 EV_P[1] - 2 lambda = 0
 B: EV_P[0] + EV_P[1] = 28.43000000590132
Bounds
 EV_P[0] >= 45
 EV_P[1] >= -0.2899999940971731
End
