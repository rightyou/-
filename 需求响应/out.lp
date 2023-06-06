\ Model EV_distribution
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 [ 5.334132011567823 EV_P[0] ^2 - 6.532461717648453 EV_P[0] * lambda
   + 4.994965458411103 EV_P[1] ^2 - 6.321370394723665 EV_P[1] * lambda
   + 4.458830834712749 EV_P[2] ^2 - 5.972490826924894 EV_P[2] * lambda
   + 6 lambda ^2 ] / 2 
Subject To
 A: 1.633115429412113 EV_P[0] + 1.580342598680916 EV_P[1]
   + 1.493122706731223 EV_P[2] - 3 lambda = 0
 B: EV_P[0] + EV_P[1] + EV_P[2] = 0
Bounds
 -4.925 <= EV_P[0] <= 12.625
 -5 <= EV_P[1] <= 12.925
 -5.175 <= EV_P[2] <= 13.1
 lambda free
End
