#===== PERHITUNGAN UNTUK ILUMINASI DAN FASE BULAN =====#
import numpy as np
import sys

#----- KOORDINAT GEOSENTRIS -----#
# KONVERSI KOORDINAT GEOSENTRIS EKLIPTIKA <-> GEOSENTRIS EKUATORIAL
# KAMUS
# _lambda       = longitude (Ekliptika Geo)
# _beta         = latitude (Ekliptika Geo)
# _alpha        = right ascension (Ekuatorial Geo)
# _delta        = deklinasi (Ekuatorial Geo)
# _epsilon      = inklinasi oblika (sudut bidang ekliptika dan ekuator)
# *semua dalam satuan derajat

def EKLtoEKU(_lambda, _beta, _epsilon=23.439607):
    _delta = np.degrees(np.arcsin(np.sin(np.radians(_beta))*np.cos(np.radians(_epsilon))+
                                  np.sin(np.radians(_lambda))*np.cos(np.radians(_beta))*np.sin(np.radians(_epsilon))))
    while _delta < -360:
        _delta += 360
    while _delta > 360:
        _delta -= 360

    _alpha = np.degrees(np.arctan((np.sin(np.radians(_lambda))*np.cos(np.radians(_epsilon))-np.tan(np.radians(_beta))
                                   *np.sin(np.radians(_epsilon)))/np.cos(np.radians(_lambda))))
    while _alpha < 0:
        _alpha += 360
    while _alpha > 360:
        _alpha -= 360
    return _alpha, _delta

def EKUtoEKL(_alpha, _delta, _epsilon=23.439607):
    _lambda = np.degrees(np.arctan((np.sin(np.radians(_alpha))*np.cos(np.radians(_epsilon))+
                                    np.tan(np.radians(_delta))*np.sin(np.radians(_epsilon)))/(np.cos(np.radians(_alpha)))))
    while _lambda < 0:
        _lambda += 360
    while _lambda > 360:
        _lambda -= 360
    _beta = np.degrees(np.arcsin(np.sin(np.radians(_delta))*np.cos(np.radians(_epsilon))
                                - np.sin(np.radians(_alpha))*np.cos(np.radians(_delta))*np.sin(np.radians(_epsilon))))
    while _beta < 0:
        _beta += 360
    while _beta > 360:
        _beta -= 360
    return _lambda, _beta

#----- JULIAN DAY -----#
# KONVERSI TANGGAL GREGORIAN <-> JD
# *menggunakan tanggal Julian untuk tanggal sebelum 15 Oktober 1582

def DtoJD (D, M, Y, hrs=0, mnt=0, dtk=0):
    A = int(Y/100)
    B = 2-A+int(A/4)
    #Cek kalender Julian atau Gregorian
    if Y < 1582:
        B = 0
    elif Y > 1582:
        B = B
    elif Y == 1582:
        if M < 10:
            B = 0
        elif M > 10:
            B = B
        elif M == 10:
            if D < 5:
                B = 0
            elif D > 14:
                B = B
            else:
                sys.exit("date not found")
    #Perhitungan JD
    if 0 < M <=2:
      Y = Y - 1
      M = M + 12
    JD = 1720994.5 + int(365.25*(Y)) + int(30.60001*(M+1)) + D + B
    #Menghitung kontribusi waktu
    JD = JD + hrs/24 + mnt/(24*60) + dtk/(24*60*60)
    return JD

def JDtoD(JD):
    Z = int(JD + 0.5)
    F = JD + 0.5 - Z
    if Z < 2299161:
        A = Z
    elif Z >= 2291161:
        alfa = int((Z-1867216.25)/36524.25)
        A = Z + 1 + alfa - int(alfa/4)
    B = A + 1524
    C = int((B - 122.1)/365.25)
    D = int(365.25*C)
    E = int((B-D)/30.6001)

    d = int(B - D - int(30.6001*E) + F)
    if E < 14:
        m = E - 1
    elif E == 14 or 15:
        m = E - 13
    if m > 2:
        y = C - 4716
    elif m == 1 or 2:
        y = C - 4715

    h = int((JD + 1.5)%7)
    hname = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
    hari = hname[h]
    
    FJD = (JD - int(JD)) - 0.5          #FJD = Berapa hari (desimal) terlewati sejak hari itu
    if FJD < 0:
        FJD = 1 + FJD
    hrs = int(FJD*24)
    mnt = int((FJD*24 - hrs)*60)
    dtk = int(((FJD*24 - hrs)*60 - mnt)*60)
    return d, m, y, hrs, mnt, dtk, hari

#----- POSISI GEOSENTRIS MATAHARI DAN BULAN -----#
# R         = Jarak matahari (km)
# _Delta    = Jarak bulan (km)
# _alpha    = Right Ascension
# _delta    = Deklinasi
# _lambda   = Longitude (Ekliptika)
# _beta     = Latitude  (Ekliptika)
# *latitude matahari dianggap selalu sama dengan nol

def SolarPos(JDE):
    def deg_norm(x):
        while x < 0:
            x += 360
        while x > 360:
            x -= 360
        return x
    #Abad terlewati sejak  1.5 TD Januari 2000
    T = (JDE - 2451545.0)/36525
    #Mean longitude of the Sun
    L0 = 280.46646 + 36000.76983*T + 0.0003032*(T**2)      
    L0 = deg_norm (L0)
    #Mean anomaly of the Sun
    M0 = 357.52911 + 35999.05029*T - 0.0001537*(T**2)     
    M0 = deg_norm (M0)
    #Eccentricity of the Earth
    e = 0.016708634 - 0.000042037*T - 0.0000001267*(T**2)  
    C = (1.914602-0.004817*T-0.000014*(T**2))*np.sin(np.radians(M0))+(0.019993-0.000101*T)*np.sin(2*np.radians(M0)) + 0.000289*np.sin(3*np.radians(M0)) #degree
    C = deg_norm (C)
    #True longitude of the Sun
    L = L0 + C                                          
    L = deg_norm (L)
    #True anomaly of the Sun
    M = M0 + C                                      
    M = deg_norm (M)
    #Koreksi longitudinal akibat nutasi dan aberasi
    _Omega = 125.04-1934.136*T
    _Omega = deg_norm (_Omega)
    #Apparent longitude of the Sun
    _lambda = L - 0.00569 - 0.00478*np.sin(np.radians(_Omega))
    _lambda = deg_norm (_lambda)

    #Jika ketelitian tinggi tidak diperlukan, latitude matahari dianggap nol
    _beta = 0

    #Jarak matahari ke bumi
    R = (1.000001018*(1-e**2))/(1+e*np.cos(np.radians(M)))     
    R = R*149597870.7                                       

    #Konversi ke koordinat geosentrik
    _epsilon0 = 23+26/60+21.448/3600 - 4680.93/3600*(T/100) - 1.55*(T/100)**2 + 1999.25*(T/100)**3 - 51.38*(T/100)**4 #diambil 5 suku pertama
    _L = 280.4665 + 36000.7698*T            #mean longitude of the Sun
    _L = deg_norm (_L)
    __L = 218.3165 + 481267.8813*T          #mean longitude of the Moon
    __L = deg_norm (__L)
    _depsilon = 9.2/3600*np.cos(np.radians(_Omega)) + 0.57/3600*np.cos(2*np.radians(_L)) + 0.10/3600*np.cos(2*np.radians(__L)) - 0.09/3600*np.cos(2*np.radians(_Omega))
    _depsilon = deg_norm (_depsilon)
    _epsilon = _epsilon0 + _depsilon + 0.00256*np.cos(np.radians(_Omega))
    _epsilon = deg_norm (_epsilon)
    # Right Ascension
    _alpha = np.degrees(np.arctan(np.cos(np.radians(_epsilon))*np.sin(np.radians(_lambda))/(np.cos(np.radians(_lambda)))))
    while _alpha < 0:
        _alpha = _alpha + 180
    while _alpha > 180:
        _alpha = _alpha -180
    # Deklinasi
    _delta = np.degrees(np.arcsin(np.sin(np.radians(_epsilon))*np.sin(np.radians(_lambda))))
    _delta = deg_norm (_delta)

    return R, _alpha, _delta, _lambda, _beta

def LunarPos(JDE):
    def deg_norm(x):
        while x < 0:
            x += 360
        while x > 360:
            x -= 360
        return x
    #Abad terlewati sejak  1.5 TD Januari 2000
    T = (JDE - 2451545.0)/36525
    #Mean Longitude
    _L = 218.3164477+481267.88123421*T-0.0015786*(T**2)+(T**3)/538841-(T**4)/65194000
    _L = deg_norm(_L)
    #Mean Elongation
    D = 297.8501921+445267.1114034*T-0.0018819*(T**2)+(T**3)/545868-(T**4)/113065000
    D = deg_norm(D)
    #Mean anomaly of the Sun
    M = 357.5291092 + 35999.0502909*T - 0.0001536*(T**2) + (T**3)/24490000 
    M = deg_norm (M)
    #Mean anomaly of the Moon
    _M = 134.9633964 + 477198.8675055*T + 0.0087414*(T**2) + (T**3)/69699 - (T**4)/14712000
    _M = deg_norm(_M)
    #Mean distance from ascending node
    F = 93.2720950 + 483202.0175233*T - 0.0036539*(T**2) - (T**3)/3526000 + (T**4)/863310000
    F = deg_norm(F)

    A1 = 119.75 + 131.849*T
    A1 = deg_norm(A1)
    A2 = 53.09 + 479264.29*T
    A2 = deg_norm(A2)
    A3 = 313.45 + 481266.484*T
    A3 = deg_norm(A3)
    
    #Eccentricity of the Earth orbit factor
    E = 1 - 0.002516*T - 0.0000074*(T**2)
    
    #Suku koreksi longitudinal dan radians
    lr = [
        [ 0,  0,  1,  0,  6288774, -20905335 ], 
        [ 2,  0, -1,  0,  1274027,  -3699111 ], 
        [ 2,  0,  0,  0,   658314,  -2955968 ], 
        [ 0,  0,  2,  0,   213618,   -569925 ], 
        [ 0,  1,  0,  0,  -185116,     48888 ], 
        [ 0,  0,  0,  2,  -114332,     -3149 ], 
        [ 2,  0, -2,  0,    58793,    246158 ], 
        [ 2, -1, -1,  0,    57066,   -152138 ], 
        [ 2,  0,  1,  0,    53322,   -170733 ], 
        [ 2, -1,  0,  0,    45758,   -204586 ], 
        [ 0,  1, -1,  0,   -40923,   -129620 ], 
        [ 1,  0,  0,  0,   -34720,    108743 ], 
        [ 0,  1,  1,  0,   -30383,    104755 ], 
        [ 2,  0,  0, -2,    15327,     10321 ], 
        [ 0,  0,  1,  2,   -12528,         0 ], 
        [ 0,  0,  1, -2,    10980,     79661 ], 
        [ 4,  0, -1,  0,    10675,    -34782 ], 
        [ 0,  0,  3,  0,    10034,    -23210 ], 
        [ 4,  0, -2,  0,     8548,    -21636 ], 
        [ 2,  1, -1,  0,    -7888,     24208 ], 
        [ 2,  1,  0,  0,    -6766,     30824 ], 
        [ 1,  0, -1,  0,    -5163,     -8379 ], 
        [ 1,  1,  0,  0,     4987,    -16675 ], 
        [ 2, -1,  1,  0,     4036,    -12831 ], 
        [ 2,  0,  2,  0,     3994,    -10445 ], 
        [ 4,  0,  0,  0,     3861,    -11650 ], 
        [ 2,  0, -3,  0,     3665,     14403 ], 
        [ 0,  1, -2,  0,    -2689,     -7003 ], 
        [ 2,  0, -1,  2,    -2602,         0 ], 
        [ 2, -1, -2,  0,     2390,     10056 ], 
        [ 1,  0,  1,  0,    -2348,      6322 ], 
        [ 2, -2,  0,  0,     2236,     -9884 ], 
        [ 0,  1,  2,  0,    -2120,      5751 ], 
        [ 0,  2,  0,  0,    -2069,         0 ], 
        [ 2, -2, -1,  0,     2048,     -4950 ], 
        [ 2,  0,  1, -2,    -1773,      4130 ], 
        [ 2,  0,  0,  2,    -1595,         0 ], 
        [ 4, -1, -1,  0,     1215,     -3958 ], 
        [ 0,  0,  2,  2,    -1110,         0 ], 
        [ 3,  0, -1,  0,     -892,      3258 ], 
        [ 2,  1,  1,  0,     -810,      2616 ], 
        [ 4, -1, -2,  0,      759,     -1897 ], 
        [ 0,  2, -1,  0,     -713,     -2117 ], 
        [ 2,  2, -1,  0,     -700,      2354 ], 
        [ 2,  1, -2,  0,      691,         0 ], 
        [ 2, -1,  0, -2,      596,         0 ], 
        [ 4,  0,  1,  0,      549,     -1423 ], 
        [ 0,  0,  4,  0,      537,     -1117 ], 
        [ 4, -1,  0,  0,      520,     -1571 ], 
        [ 1,  0, -2,  0,     -487,     -1739 ], 
        [ 2,  1,  0, -2,     -399,         0 ], 
        [ 0,  0,  2, -2,     -381,     -4421 ], 
        [ 1,  1,  1,  0,      351,         0 ], 
        [ 3,  0, -2,  0,     -340,         0 ], 
        [ 4,  0, -3,  0,      330,         0 ], 
        [ 2, -1,  2,  0,      327,         0 ], 
        [ 0,  2,  1,  0,     -323,      1165 ], 
        [ 1,  1, -1,  0,      299,         0 ], 
        [ 2,  0,  3,  0,      294,         0 ], 
        [ 2,  0, -1, -2,        0,      8752 ] 
        ]
        
    
    #Suku koreksi latitude
    b = [
        [ 0,  0,  0,  1, 5128122 ], 
        [ 0,  0,  1,  1,  280602 ], 
        [ 0,  0,  1, -1,  277693 ], 
        [ 2,  0,  0, -1,  173237 ], 
        [ 2,  0, -1,  1,   55413 ], 
        [ 2,  0, -1, -1,   46271 ], 
        [ 2,  0,  0,  1,   32573 ], 
        [ 0,  0,  2,  1,   17198 ], 
        [ 2,  0,  1, -1,    9266 ], 
        [ 0,  0,  2, -1,    8822 ], 
        [ 2, -1,  0, -1,    8216 ], 
        [ 2,  0, -2, -1,    4324 ], 
        [ 2,  0,  1,  1,    4200 ], 
        [ 2,  1,  0, -1,   -3359 ], 
        [ 2, -1, -1,  1,    2463 ], 
        [ 2, -1,  0,  1,    2211 ], 
        [ 2, -1, -1, -1,    2065 ], 
        [ 0,  1, -1, -1,   -1870 ], 
        [ 4,  0, -1, -1,    1828 ], 
        [ 0,  1,  0,  1,   -1794 ], 
        [ 0,  0,  0,  3,   -1749 ], 
        [ 0,  1, -1,  1,   -1565 ], 
        [ 1,  0,  0,  1,   -1491 ], 
        [ 0,  1,  1,  1,   -1475 ], 
        [ 0,  1,  1, -1,   -1410 ], 
        [ 0,  1,  0, -1,   -1344 ], 
        [ 1,  0,  0, -1,   -1335 ], 
        [ 0,  0,  3,  1,    1107 ], 
        [ 4,  0,  0, -1,    1021 ], 
        [ 4,  0, -1,  1,     833 ], 
        [ 0,  0,  1, -3,     777 ], 
        [ 4,  0, -2,  1,     671 ], 
        [ 2,  0,  0, -3,     607 ], 
        [ 2,  0,  2, -1,     596 ], 
        [ 2, -1,  1, -1,     491 ], 
        [ 2,  0, -2,  1,    -451 ], 
        [ 0,  0,  3, -1,     439 ], 
        [ 2,  0,  2,  1,     422 ], 
        [ 2,  0, -3, -1,     421 ], 
        [ 2,  1, -1,  1,    -366 ], 
        [ 2,  1,  0,  1,    -351 ], 
        [ 4,  0,  0,  1,     331 ], 
        [ 2, -1,  1,  1,     315 ], 
        [ 2, -2,  0, -1,     302 ], 
        [ 0,  0,  1,  3,    -283 ], 
        [ 2,  1,  1, -1,    -229 ], 
        [ 1,  1,  0, -1,     223 ], 
        [ 1,  1,  0,  1,     223 ], 
        [ 0,  1, -2, -1,    -220 ], 
        [ 2,  1, -2, -1,    -220 ], 
        [ 1,  0,  1,  1,    -185 ], 
        [ 2, -1, -2, -1,     181 ], 
        [ 0,  1,  2,  1,    -177 ], 
        [ 4,  0, -2, -1,     176 ], 
        [ 4, -1, -1, -1,     166 ], 
        [ 1,  0,  1, -1,    -164 ], 
        [ 4,  0,  1, -1,     132 ], 
        [ 1,  0, -1, -1,    -119 ], 
        [ 4, -1,  0, -1,     115 ], 
        [ 2, -2,  0,  1,     107 ] 
        ]
    
    #Jumlahan suku koreksi longitude dan radians
    suml = 0
    sumr = 0
    for i in range (0, len(lr)):
        k = lr[i]
        a = D*k[0] + M*k[1] + _M*k[2] + F*k[3]

        c = 1
        if abs(k[1]) == 1:
            c = E
        if abs(k[1]) == 2:
            c = E**2
        suml += c*k[4]*np.sin(np.radians(a))
        sumr += c*k[5]*np.cos(np.radians(a))

    #Jumlahan suku koreksi latitude
    sumb = 0
    for i in range (0, len(b)):
        k = b[i]
        a = D*k[0] + M*k[1] + _M*k[2] + F*k[3]

        c = 1
        if abs(k[1]) == 1:
            c = E
        if abs(k[1]) == 2:
            c = E**2
        sumb += c*k[4]*np.sin(np.radians(a))
    
    #Koreksi tambahan
    suml += 3958*np.sin(np.radians(A1)) + 1962*np.sin(np.radians(_L)-np.radians(F)) + 318*np.sin(np.radians(A2))
    sumb += -2235*np.sin(np.radians(_L)) + 382*np.sin(np.radians(A3)) + 175*np.sin(np.radians(A1-F)) + 175*np.sin(np.radians(A1+F)) + 127*np.sin(np.radians(_L-_M)) - 115*np.sin(np.radians(_L+_M))

    #Koordinat Ekliptika Geosentrik
    _lambda0 = _L + suml/(10**6)
    _beta = sumb/(10**6)
    _Delta = 385000.56 + sumr/1000          #km

    #Equatorial horizontal parallax of the Moon
    _pi = np.degrees(np.arcsin(6378.14/_Delta))

    #Longitude of ascending node
    _Omega = 125.04452-1934.136261*T+0.0020708*(T**2)+(T**3)/450000

    #Mean longitudes of the Sun and the Moon
    _L = 280.4665 + 36000.7698*T            #mean longitude of the Sun
    _L = deg_norm (_L)
    __L = 218.3165 + 481267.8813*T          #mean longitude of the Moon
    __L = deg_norm (__L)

    #Nutasi in 
    _dPsi = -17.20/3600*np.sin(np.radians(_Omega))+1.32/3600*np.sin(2*np.radians(_L))-0.23/3600*np.sin(2*np.radians(__L))+0.21/3600*np.sin(2*np.radians(_Omega))
    _dPsi = deg_norm(_dPsi)
    _depsilon = 9.2/3600*np.cos(np.radians(_Omega)) + 0.57/3600*np.cos(2*np.radians(_L)) + 0.10/3600*np.cos(2*np.radians(__L)) - 0.09/3600*np.cos(2*np.radians(_Omega))
    _depsilon = deg_norm (_depsilon)

    #Koordinat Ekuatorial Geosentrik
    _lambda = _lambda0 + _dPsi
    _epsilon0 = 23+26/60+21.448/3600 - 4680.93/3600*(T/100) - 1.55*(T/100)**2 + 1999.25*(T/100)**3 - 51.38*(T/100)**4   #diambil 5 suku pertama
    _epsilon = _epsilon0 + _depsilon

    _alpha, _delta = EKLtoEKU(_lambda, _beta, _epsilon)
    return _Delta, _alpha, _delta, _lambda, _beta

#----- FRAKSI ILUMINASI BULAN -----#
def LunarIllum(JDE):
    def deg_norm(x):
        while x < 0:
            x += 360
        while x > 360:
            x -= 360
        return x
    _lambda0 = SolarPos(JDE)[3]
    _lambda = LunarPos(JDE)[3]

    D = _lambda - _lambda0
    D = deg_norm(D)
    F = 0.5*(1-np.cos(np.radians(D)))
    return F

#----- FASE BULAN -----#
# MENCARI JD DARI SUATU FASE BULAN
# k = X.0   -> New Moon
# k = x.25  -> First Quarter
# k = X.5   -> Full Moon
# k = X.75  -> Third Quarter
# yfrac = (y) + (m - 1+ (d-1)/30.5)/12
# k = (yfrac - 2000)*12.3685

def JDLunarPhase(k):
    #fraksi tahun terlewati
    def deg_norm(x):
        while x < 0:
            x += 360
        while x > 360:
            x -= 360
        return x
    T = k/1236.85

    #Mean anomaly of the Sun
    M = 2.5534 + 29.1053567*k - 0.0000014*T**2 - 0.00000011*T**3
    M = deg_norm(M)
    #Mean anomaly of the Moon
    _M = 201.5643 + 385.81693528*k + 0.0107528*T**2 + 0.00001238*T**3 - 0.000000058*T**4
    _M = deg_norm(_M)
    #Moon argument of latitude
    F = 160.7108 + 390.67050284*k - 0.0016118*T**2 - 0.00000227*T**3 + 0.000000011*T**4
    F = deg_norm(F)
    #Longitude of the ascending node
    _Omega = 124.7746 - 1.56375588*k + 0.0020672*T**2 + 0.00000215*T**3
    _Omega = deg_norm(_Omega)
    #Planetary argument
    A1 = (299.77 + 0.107408*k - 0.009173*T*T)
    A2 = (251.88 + 0.016321*k)
    A3 = (251.83 + 26.651886*k)
    A4 = (349.42 + 36.412478*k)
    A5 = (84.66 + 18.206239*k)
    A6 = (141.74 + 53.303771*k)
    A7 = (207.14 + 2.453732*k)
    A8 = (154.84 + 7.306860*k)
    A9 = (34.52 + 27.261239*k)
    A10 = (207.19 + 0.121824*k)
    A11 = (291.34 + 1.844379*k)
    A12 = (161.72 + 24.198154*k)
    A13 = (239.56 + 25.513099*k)
    A14 = (331.55 + 3.592518*k)

    #Eccentricity of the Earth orbit factor
    E = 1 - 0.002516*T - 0.0000074*(T**2)

    #Correction (in days)
    corr = [
        #New Moon       #Full Moon      #Quarter        #sin of
        [-0.4072,       -0.40614,       -0.62801,       _M      ],
        [0.17241*E,     0.17302*E,      0.17172*E,      M       ],
        [0.01608,       0.01614,        0.00862,        2*_M    ],
        [0.01039,       0.01043,        0.00804,        2*F     ],
        [0.00739*E,     0.00734*E,      0.00454*E,      _M-M    ],
        [-0.00514*E,    -0.00515*E,     -0.01183*E,     _M+M    ],
        [0.00208*E**2,  0.00209*E**2,   0.00204*E**2,    2*M     ],
        [-0.00111,      -0.00111,       -0.0018,        _M-2*F  ],
        [-0.00057,      -0.00057,       -0.0007,        _M+2*F  ],
        [0.00056*E,     0.00056*E,      0.00027*E,      2*_M+M  ],
        [-0.00042,      -0.00042,       -0.0004,        3*_M    ],
        [0.00042*E,     0.00042*E,      0.00032*E,      M+2*F   ],
        [0.00038*E,     0.00038*E,      0.00032*E,      M-2*F   ],
        [-0.00024*E,    -0.00024*E,     -0.00034*E,     2*_M-M  ],
        [-0.00017,      -0.00017,       -0.00017,       _Omega  ],
        [-0.00007,      -0.00007,       -0.00028*E**2,  _M+2*M  ],
        [0.00004,       0.00004,        0.00002,        2*_M-2*F],
        [0.00004,       0.00004,        0.00003,        3*M     ],
        [0.00003,       0.00003,        0.00003,        _M+M-2*F],
        [0.00003,       0.00003,        0.00004,        2*_M+2*F],
        [-0.00003,      -0.00003,       -0.00004,       _M+M+2*F],
        [0.00003,       0.00003,        0.00002,        _M-M+2*F],
        [-0.00002,      -0.00002,       -0.00005,       _M-M-2*F],
        [-0.00002,      -0.00002,       -0.00002,       3*_M+M  ],
        [0.00002,       0.00002,        0,              4*_M    ],
        [0,             0,              0.00004,        _M-2*M]
        ]

    corrNew = 0
    corrFull = 0
    corrQuarter = 0
    for i in range(0, len(corr)):
        j = corr[i]
        corrNew += j[0] * np.sin(np.radians(j[3]))
        corrFull += j[1] * np.sin(np.radians(j[3]))
        corrQuarter += j[2] * np.sin(np.radians(j[3]))

    #Correction for quarter phase
    W = (0.00306 - 0.00038*E*np.cos(np.radians(M)) + 0.00026*np.cos(np.radians(_M)) - 0.00002*np.cos(np.radians(_M-M))
         + 0.00002*np.cos(np.radians(_M+M)) + 0.00002*np.cos(2*np.radians(F)))

    #Additional correction
    addcorr = (0.000325*np.sin(np.radians(A1)) + 0.000165*np.sin(np.radians(A2)) + 0.000164*np.sin(np.radians(A3)) + 0.000126*np.sin(np.radians(A4))
               + 0.000110*np.sin(np.radians(A5)) + 0.000062*np.sin(np.radians(A6)) + 0.000060*np.sin(np.radians(A7)) + 0.000056*np.sin(np.radians(A8))
               + 0.000047*np.sin(np.radians(A9)) + 0.000042*np.sin(np.radians(A10)) + 0.000040*np.sin(np.radians(A11)) + 0.000037*np.sin(np.radians(A12))
               + 0.000035*np.sin(np.radians(A13)) + 0.000023*np.sin(np.radians(A14)))
    
    #JD pada saat desimal k = 0; 0.25, 0.5, 0.75
    JDE = 2451550.09766 + 29.530588861*k + 0.00015437*T**2 - 0.00000015*T**3 + 0.00000000073*T**4
    if abs(k-int(k)) == 0:
        #NEW MOON
        corrNew = 0
        for i in range(0, len(corr)):
            k = corr[i]
            corrNew += k[0] * np.sin(np.radians(k[3]))
        JDE += corrNew + addcorr
    elif abs(k-int(k)) == 0.5:
        #FULL MOON
        corrFull = 0
        for i in range(0, len(corr)):
            k = corr[i]
            corrFull += k[1] * np.sin(np.radians(k[3]))
        JDE += corrFull + addcorr
    elif abs(k-int(k)) == 0.25:
        #FIRST QUARTER
        corrQuarter = 0
        for i in range(0, len(corr)):
            k = corr[i]
            corrQuarter += k[2] * np.sin(np.radians(k[3]))
        JDE += corrQuarter + addcorr + W
    elif abs(k-int(k)) == 0.75:
        #LAST QUARTER
        corrQuarter = 0
        for i in range(0, len(corr)):
            k = corr[i]
            corrQuarter += k[2] * np.sin(np.radians(k[3]))
        JDE += corrQuarter + addcorr - W
    else:
        JDE = 0
    return JDE