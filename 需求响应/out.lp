\ Model EV_distribution
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 [ 2.118923867992616 EV_P[0] ^2 - 4.11720669191394 EV_P[0] * lambda
   + 2 lambda ^2 ] / 2 
Subject To
 A: 1.029301672978485 EV_P[0] - lambda = 0
 B: EV_P[0] = 3.25608e-12
Bounds
 -4.975 <= EV_P[0] <= 12.65
 lambda free
End
