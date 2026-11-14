# Simulator audit and temporal methodology

## Simulator audit


===========================================================================
1. DATASET INTEGRITY
===========================================================================
Transactions: 94722
Unique transaction IDs: 94722
Duplicate transaction IDs: 0
Missing transaction truth: 0
Fraud-stage rows: 141

Stage counts:
stage
legitimate        94470
seasoning           111
victim_to_mule       88
mule_layering        29
cashout              24

===========================================================================
2. NUMERIC DISTRIBUTIONS BY STAGE
===========================================================================

amount_inr
                count     median       mean        min        max
stage                                                            
cashout            24   42179.52   42707.02    3449.54  108345.76
legitimate      94470     548.30    1462.55       5.01   64956.73
mule_layering      29  174632.71  174272.94  118960.22  231288.65
seasoning         111    1322.93    1344.99     223.58    2495.52
victim_to_mule     88   13339.40   21798.67     343.80   74402.41

day
                count  median   mean  min  max
stage                                         
cashout            24    58.5  54.50   25   74
legitimate      94470    37.0  36.91    0   74
mule_layering      29    59.0  52.21   21   74
seasoning         111    53.0  44.89   15   65
victim_to_mule     88    51.0  49.45   20   71

sender_id
                count  median     mean   min   max
stage                                             
cashout            24  1620.5  1620.75  1605  1637
legitimate      94470   754.0   755.93     1  1600
mule_layering      29  1619.0  1618.52  1601  1636
seasoning         111   849.0   799.50    13  1481
victim_to_mule     88   565.5   646.16    23  1455

receiver_id
                count  median     mean   min   max
stage                                             
cashout            24  1550.0  1548.17  1509  1590
legitimate      94470  1167.0  1035.92     1  1600
mule_layering      29  1620.0  1619.52  1602  1637
seasoning         111  1619.0  1619.00  1601  1637
victim_to_mule     88  1615.0  1616.67  1601  1633

sender_age_days
                count  median   mean  min  max
stage                                         
cashout            24    14.5  14.50   14   15
legitimate      94470    37.0  36.91    0   74
mule_layering      29    12.0  12.34   11   14
seasoning         111    53.0  44.89   15   65
victim_to_mule     88    51.0  49.45   20   71

receiver_age_days
                count  median   mean  min  max
stage                                         
cashout            24    58.5  54.50   25   74
legitimate      94470    37.0  36.91    0   74
mule_layering      29    12.0  12.34   11   14
seasoning         111     5.0   5.00    5    5
victim_to_mule     88    10.5  10.50   10   11

===========================================================================
3. PAYMENT_TYPE BY STAGE
===========================================================================
Counts:
stage          cashout  legitimate  mule_layering  seasoning  victim_to_mule
payment_type                                                                
APP_TRANSFER         0           0              0          0              88
GROUP_PAYMENT        0        6000              0          0               0
MERCHANT            24       33750              0          0               0
P2P                  0       52500             29        111               0
PAYROLL              0         900              0          0               0
RECURRING            0        1320              0          0               0

Row percentages:
stage          cashout  legitimate  mule_layering  seasoning  victim_to_mule
payment_type                                                                
APP_TRANSFER       0.0         0.0            0.0        0.0           100.0
GROUP_PAYMENT      0.0       100.0            0.0        0.0             0.0
MERCHANT           0.1        99.9            0.0        0.0             0.0
P2P                0.0        99.7            0.1        0.2             0.0
PAYROLL            0.0       100.0            0.0        0.0             0.0
RECURRING          0.0       100.0            0.0        0.0             0.0

===========================================================================
3. CHANNEL BY STAGE
===========================================================================
Counts:
stage       cashout  legitimate  mule_layering  seasoning  victim_to_mule
channel                                                                  
internet         11       31545             13         35              21
mobile_app        5       31443              8         31              34
upi               8       31482              8         45              33

Row percentages:
stage       cashout  legitimate  mule_layering  seasoning  victim_to_mule
channel                                                                  
internet        0.0        99.7            0.0        0.1             0.1
mobile_app      0.0        99.8            0.0        0.1             0.1
upi             0.0        99.7            0.0        0.1             0.1

===========================================================================
3. SENDER_SEGMENT_ACTUAL BY STAGE
===========================================================================
Counts:
stage                  cashout  legitimate  mule_layering  seasoning  victim_to_mule
sender_segment_actual                                                               
merchant                     0         900              0          0               0
salaried                    24       62522             29         70              60
senior                       0        9206              0         16               1
sole_prop                    0        6235              0          5               7
student                      0       15607              0         20              20

Row percentages:
stage                  cashout  legitimate  mule_layering  seasoning  victim_to_mule
sender_segment_actual                                                               
merchant                   0.0       100.0            0.0        0.0             0.0
salaried                   0.0        99.7            0.0        0.1             0.1
senior                     0.0        99.8            0.0        0.2             0.0
sole_prop                  0.0        99.8            0.0        0.1             0.1
student                    0.0        99.7            0.0        0.1             0.1

===========================================================================
3. RECEIVER_SEGMENT_ACTUAL BY STAGE
===========================================================================
Counts:
stage                    cashout  legitimate  mule_layering  seasoning  victim_to_mule
receiver_segment_actual                                                               
merchant                      24       33750              0          0               0
salaried                       0       40484             29        111              88
senior                         0        5991              0          0               0
sole_prop                      0        4021              0          0               0
student                        0       10224              0          0               0

Row percentages:
stage                    cashout  legitimate  mule_layering  seasoning  victim_to_mule
receiver_segment_actual                                                               
merchant                     0.1        99.9            0.0        0.0             0.0
salaried                     0.0        99.4            0.1        0.3             0.2
senior                       0.0       100.0            0.0        0.0             0.0
sole_prop                    0.0       100.0            0.0        0.0             0.0
student                      0.0       100.0            0.0        0.0             0.0

===========================================================================
3. SENDER_TRUE_ROLE BY STAGE
===========================================================================
Counts:
stage             cashout  legitimate  mule_layering  seasoning  victim_to_mule
sender_true_role                                                               
customer                0       93570              0        111              88
merchant                0         900              0          0               0
mule                   24           0             29          0               0

Row percentages:
stage             cashout  legitimate  mule_layering  seasoning  victim_to_mule
sender_true_role                                                               
customer              0.0        99.8            0.0        0.1             0.1
merchant              0.0       100.0            0.0        0.0             0.0
mule                 45.3         0.0           54.7        0.0             0.0

===========================================================================
4. ACCOUNT ID AND CAMPAIGN STRUCTURE
===========================================================================

sender_id by stage:
                 min  median   max  nunique
stage                                      
cashout         1605  1620.5  1637        8
legitimate         1   754.0  1600     1600
mule_layering   1601  1619.0  1636       29
seasoning         13   849.0  1481      106
victim_to_mule    23   565.5  1455       39

receiver_id by stage:
                 min  median   max  nunique
stage                                      
cashout         1509  1550.0  1590       20
legitimate         1  1167.0  1600     1600
mule_layering   1602  1620.0  1637       29
seasoning       1601  1619.0  1637       37
victim_to_mule  1601  1615.0  1633        8

Campaigns by stage:
campaign_id  stage         
C001         cashout               3
             mule_layering         4
             seasoning            15
             victim_to_mule       11
C002         cashout               3
             mule_layering         4
             seasoning            15
             victim_to_mule       11
C003         cashout               3
             mule_layering         3
             seasoning            12
             victim_to_mule       17
C004         cashout               3
             mule_layering         3
             seasoning            12
             victim_to_mule       10
C005         cashout               3
             mule_layering         4
             seasoning            15
             victim_to_mule        5
C006         cashout               3
             mule_layering         3
             seasoning            12
             victim_to_mule       11
C007         cashout               3
             mule_layering         4
             seasoning            15
             victim_to_mule       13
C008         cashout               3
             mule_layering         4
             seasoning            15
             victim_to_mule       10
NaN          legitimate        94470

===========================================================================
5. DAILY ACTIVITY
===========================================================================
     transactions  fraud_stages  campaigns  fraud_stage_rate_pct
day                                                             
0            1650             0          0              0.000000
1            1230             0          0              0.000000
2            1230             0          0              0.000000
3            1230             0          0              0.000000
4            1230             0          0              0.000000
5            1230             0          0              0.000000
6            1230             0          0              0.000000
7            1350             0          0              0.000000
8            1230             0          0              0.000000
9            1230             0          0              0.000000
10           1230             0          0              0.000000
11           1230             0          0              0.000000
12           1230             0          0              0.000000
13           1230             0          0              0.000000
14           1350             0          0              0.000000
15           1245             0          1              0.000000
16           1230             0          0              0.000000
17           1230             0          0              0.000000
18           1230             0          0              0.000000
19           1230             0          0              0.000000
20           1239             9          1              0.726392
21           1353             3          1              0.221729
22           1231             1          1              0.081235
23           1231             1          1              0.081235
24           1231             1          1              0.081235
25           1248             3          2              0.240385
26           1230             0          0              0.000000
27           1230             0          0              0.000000
28           1350             0          0              0.000000
29           1230             0          0              0.000000
30           1536             6          1              0.390625
31           1236             6          1              0.485437
32           1231             1          1              0.081235
33           1231             1          1              0.081235
34           1231             1          1              0.081235
35           1365             3          2              0.219780
36           1230             0          0              0.000000
37           1230             0          0              0.000000
38           1230             0          0              0.000000
39           1230             0          0              0.000000
40           1239             9          1              0.726392
41           1239             9          1              0.726392
42           1351             1          1              0.074019
43           1231             1          1              0.081235
44           1233             3          1              0.243309
45           1242             0          1              0.000000
46           1230             0          0              0.000000
47           1230             0          0              0.000000
48           1230             0          0              0.000000
49           1350             0          0              0.000000
50           1232             2          1              0.162338
51           1239             9          1              0.726392
52           1231             1          1              0.081235
53           1246             1          2              0.080257
54           1233             3          1              0.243309
55           1230             0          0              0.000000
56           1350             0          0              0.000000
57           1230             0          0              0.000000
58           1233             3          1              0.243309
59           1245             3          2              0.240964
60           1531             1          1              0.065317
61           1231             1          1              0.081235
62           1231             1          1              0.081235
63           1368             3          2              0.219298
64           1234             4          1              0.324149
65           1253             8          2              0.638468
66           1231             1          1              0.081235
67           1231             1          1              0.081235
68           1240            10          2              0.806452
69           1237             7          1              0.565885
70           1355             5          2              0.369004
71           1238             8          2              0.646204
72           1232             2          2              0.162338
73           1234             4          2              0.324149
74           1234             4          1              0.324149

===========================================================================
6. SENDER ROLE VS TRANSACTION STAGE
===========================================================================
stage             cashout  legitimate  mule_layering  seasoning  victim_to_mule
sender_true_role                                                               
customer                0       93570              0        111              88
merchant                0         900              0          0               0
mule                   24           0             29          0               0

===========================================================================
7. FRAUD-STAGE RATE BY CATEGORICAL FIELD
===========================================================================

payment_type
               transactions  fraud_stages  fraud_rate_pct
payment_type                                             
APP_TRANSFER             88            88         100.000
GROUP_PAYMENT          6000             0           0.000
MERCHANT              33774            24           0.071
P2P                   52640            29           0.055
PAYROLL                 900             0           0.000
RECURRING              1320             0           0.000

channel
            transactions  fraud_stages  fraud_rate_pct
channel                                               
internet           31625            45           0.142
mobile_app         31521            47           0.149
upi                31576            49           0.155

sender_segment_actual
                       transactions  fraud_stages  fraud_rate_pct
sender_segment_actual                                            
merchant                        900             0           0.000
salaried                      62705           113           0.180
senior                         9223             1           0.011
sole_prop                      6247             7           0.112
student                       15647            20           0.128

receiver_segment_actual
                         transactions  fraud_stages  fraud_rate_pct
receiver_segment_actual                                            
merchant                        33774            24           0.071
salaried                        40712           117           0.287
senior                           5991             0           0.000
sole_prop                        4021             0           0.000
student                         10224             0           0.000

===========================================================================
8. CAMPAIGN ACCOUNT ID RANGES
===========================================================================
             first_day  last_day  sender_min  sender_max  receiver_min  receiver_max  accounts
campaign_id                                                                                   
C001                15        25         119        1605          1525          1605        25
C002                25        35          23        1610          1525          1610        25
C003                35        44         147        1614          1525          1614        21
C004                45        54          42        1618          1552          1618        21
C005                53        63          13        1623          1520          1623        25
C006                59        68          73        1627          1515          1627        21
C007                63        73          44        1632          1547          1632        25
C008                65        74         113        1637          1509          1637        25

Audit complete. Ground-truth fields above are for diagnosis only.


## Temporal splits

- Warm-up ends at day 14.
- Train event-time interval: [14, 37).
- Validation event-time interval: [43, 52).
- Test event-time interval: [55, 75).
- Labels use a simulated three-day maturity delay.
- Thresholds are derived from training controls; validation is for selection; test is held out.

## Point-in-time and leakage controls

- Rolling features use strictly prior transactions; same-timestamp events are excluded.
- Campaign IDs, ground-truth labels, account true roles and account IDs are not detector inputs.
- Simulator audit identified APP_TRANSFER as a perfect fraud shortcut; payment_type must not be used as a detector feature.
- Receiver segment and role fields are simulator shortcuts and must not be used as detector features.

## Limitations

- All data is synthetic and the positive sample is small.
- Simulator campaigns and account-generation rules may create artificial patterns.
- Results do not establish real-world or production performance.

## Reproducibility

Record Python/dependency versions and Git commit. Run generation, feature engineering, temporal split, detector and evaluation scripts in the documented order.