f(x) = a*x + b

a = 1
b = 1

c = 1
d = 1
e = 1
f = 1

g(x) = f * x * x * x + c * x * x + d * x + e

set logscale x
set logscale y

fit f(x) 'lengthscore.data' using 1:2 via a,b
#fit g(x) 'lengthscore.data' using 1:2 via c,d,e,f

set xlabel 'length'
set ylabel 'score'


plot  "lengthscore.data" using 1:2 title "data from news.yc" #, f(x) title "linear regression" # g(x)
