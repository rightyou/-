\ Model SP
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0.1 EDG[0] + 0.1 EDG[1] + 0.1 EDG[2] + 0.1 EDG[3] + 0.1 EDG[4]
   + 0.1 EDG[5] + 0.1 EDG[6] + 0.1 EDG[7] + 0.1 EDG[8] + 0.1 EDG[9]
   + 0.1 EDG[10] + 0.1 EDG[11] + 0.1 EDG[12] + 0.1 EDG[13] + 0.1 EDG[14]
   + 0.1 EDG[15] + 0.1 EDG[16] + 0.1 EDG[17] + 0.1 EDG[18] + 0.1 EDG[19]
   + 0.1 EDG[20] + 0.1 EDG[21] + 0.1 EDG[22] + 0.1 EDG[23] + 0.4 EBFG[0]
   + 0.4 EBFG[1] + 0.4 EBFG[2] + 0.4 EBFG[3] + 0.4 EBFG[4] + 0.4 EBFG[5]
   + 1.4 EBFG[6] + 1.4 EBFG[7] + 1.4 EBFG[8] + 2.2 EBFG[9] + 2.2 EBFG[10]
   + 2.2 EBFG[11] + 1.4 EBFG[12] + 1.4 EBFG[13] + 2.2 EBFG[14]
   + 2.2 EBFG[15] + 2.2 EBFG[16] + 2.2 EBFG[17] + 1.4 EBFG[18]
   + 1.4 EBFG[19] + 1.4 EBFG[20] + 0.4 EBFG[21] + 0.4 EBFG[22]
   + 0.4 EBFG[23] - 0.2 ESTG[0] - 0.2 ESTG[1] - 0.2 ESTG[2] - 0.2 ESTG[3]
   - 0.2 ESTG[4] - 0.2 ESTG[5] - 0.6 ESTG[6] - 0.6 ESTG[7] - 0.6 ESTG[8]
   - 1.2 ESTG[9] - 1.2 ESTG[10] - 0.8 ESTG[11] - 0.8 ESTG[12]
   - 0.6 ESTG[13] - 0.6 ESTG[14] - 0.8 ESTG[15] - 0.6 ESTG[16]
   - 0.6 ESTG[17] - 0.6 ESTG[18] - 0.2 ESTG[19] - 0.2 ESTG[20]
   - 0.2 ESTG[21] - 0.2 ESTG[22] - 0.2 ESTG[23] + 7.2 Constant + [
   0.002 EDG[0] ^2 + 0.002 EDG[1] ^2 + 0.002 EDG[2] ^2 + 0.002 EDG[3] ^2
   + 0.002 EDG[4] ^2 + 0.002 EDG[5] ^2 + 0.002 EDG[6] ^2 + 0.002 EDG[7] ^2
   + 0.002 EDG[8] ^2 + 0.002 EDG[9] ^2 + 0.002 EDG[10] ^2
   + 0.002 EDG[11] ^2 + 0.002 EDG[12] ^2 + 0.002 EDG[13] ^2
   + 0.002 EDG[14] ^2 + 0.002 EDG[15] ^2 + 0.002 EDG[16] ^2
   + 0.002 EDG[17] ^2 + 0.002 EDG[18] ^2 + 0.002 EDG[19] ^2
   + 0.002 EDG[20] ^2 + 0.002 EDG[21] ^2 + 0.002 EDG[22] ^2
   + 0.002 EDG[23] ^2 ] / 2 
Subject To
 power_balance[0]: EDG[0] + EBFG[0] - ESTG[0] + RES[0,0] - EVA[0,0] = 100
 power_balance[1]: EDG[1] + EBFG[1] - ESTG[1] + RES[0,1] - EVA[0,1] = 110
 power_balance[2]: EDG[2] + EBFG[2] - ESTG[2] + RES[0,2] - EVA[0,2] = 90
 power_balance[3]: EDG[3] + EBFG[3] - ESTG[3] + RES[0,3] - EVA[0,3] = 122
 power_balance[4]: EDG[4] + EBFG[4] - ESTG[4] + RES[0,4] - EVA[0,4] = 140
 power_balance[5]: EDG[5] + EBFG[5] - ESTG[5] + RES[0,5] - EVA[0,5] = 150
 power_balance[6]: EDG[6] + EBFG[6] - ESTG[6] + RES[0,6] - EVA[0,6] = 260
 power_balance[7]: EDG[7] + EBFG[7] - ESTG[7] + RES[0,7] - EVA[0,7] = 300
 power_balance[8]: EDG[8] + EBFG[8] - ESTG[8] + RES[0,8] - EVA[0,8] = 400
 power_balance[9]: EDG[9] + EBFG[9] - ESTG[9] + RES[0,9] - EVA[0,9] = 410
 power_balance[10]: EDG[10] + EBFG[10] - ESTG[10] + RES[0,10] - EVA[0,10]
   = 420
 power_balance[11]: EDG[11] + EBFG[11] - ESTG[11] + RES[0,11] - EVA[0,11]
   = 440
 power_balance[12]: EDG[12] + EBFG[12] - ESTG[12] + RES[0,12] - EVA[0,12]
   = 442
 power_balance[13]: EDG[13] + EBFG[13] - ESTG[13] + RES[0,13] - EVA[0,13]
   = 452
 power_balance[14]: EDG[14] + EBFG[14] - ESTG[14] + RES[0,14] - EVA[0,14]
   = 430
 power_balance[15]: EDG[15] + EBFG[15] - ESTG[15] + RES[0,15] - EVA[0,15]
   = 422
 power_balance[16]: EDG[16] + EBFG[16] - ESTG[16] + RES[0,16] - EVA[0,16]
   = 320
 power_balance[17]: EDG[17] + EBFG[17] - ESTG[17] + RES[0,17] - EVA[0,17]
   = 233
 power_balance[18]: EDG[18] + EBFG[18] - ESTG[18] + RES[0,18] - EVA[0,18]
   = 150
 power_balance[19]: EDG[19] + EBFG[19] - ESTG[19] + RES[0,19] - EVA[0,19]
   = 200
 power_balance[20]: EDG[20] + EBFG[20] - ESTG[20] + RES[0,20] - EVA[0,20]
   = 210
 power_balance[21]: EDG[21] + EBFG[21] - ESTG[21] + RES[0,21] - EVA[0,21]
   = 160
 power_balance[22]: EDG[22] + EBFG[22] - ESTG[22] + RES[0,22] - EVA[0,22]
   = 100
 power_balance[23]: EDG[23] + EBFG[23] - ESTG[23] + RES[0,23] - EVA[0,23]
   = 101
Bounds
 EDG[0] = 10
 EDG[1] = 20
 EDG[2] = 20
 EDG[3] = 14
 EDG[4] = 30
 EDG[5] = 20
 EDG[6] = 90
 EDG[7] = 140
 EDG[8] = 260
 EDG[9] = 270
 EDG[10] = 150
 EDG[11] = 130
 EDG[12] = 134
 EDG[13] = 140
 EDG[14] = 150
 EDG[15] = 300
 EDG[16] = 310
 EDG[17] = 250
 EDG[18] = 120
 EDG[19] = 60
 EDG[20] = 80
 EDG[21] = 70
 EDG[22] = 50
 EDG[23] = 30
 RES[0,0] <= 423
 RES[0,1] <= 421
 RES[0,2] <= 410
 RES[0,3] <= 400
 RES[0,4] <= 360
 RES[0,5] <= 300
 RES[0,6] <= 152
 RES[0,7] <= 80
 RES[0,8] <= 76
 RES[0,9] <= 78
 RES[0,10] <= 80
 RES[0,11] <= 84
 RES[0,12] <= 86
 RES[0,13] <= 79
 RES[0,14] <= 90
 RES[0,15] <= 83
 RES[0,16] <= 79
 RES[0,17] <= 85
 RES[0,18] <= 190
 RES[0,19] <= 260
 RES[0,20] <= 310
 RES[0,21] <= 360
 RES[0,22] <= 371
 RES[0,23] <= 380
 EVA[0,0] = 0
 EVA[0,1] = 0
 EVA[0,2] = 0
 EVA[0,3] = 0
 EVA[0,4] = 0
 EVA[0,5] <= 60
 EVA[0,6] <= 60
 EVA[0,7] <= 60
 EVA[0,8] <= 60
 EVA[0,9] <= 60
 EVA[0,10] <= 60
 60 <= EVA[0,11] <= 120
 EVA[0,12] <= 90
 EVA[0,13] <= 120
 EVA[0,14] <= 120
 EVA[0,15] <= 120
 210 <= EVA[0,16] <= 270
 90 <= EVA[0,17] <= 120
 EVA[0,18] = 120
 EVA[0,19] = 0
 EVA[0,20] = 0
 EVA[0,21] = 0
 EVA[0,22] = 0
 EVA[0,23] = 0
 Constant = 1
End
