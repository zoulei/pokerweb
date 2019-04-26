args = commandArgs(trailingOnly=TRUE)

NANSYMBOL = -10000.0
HPVALUESLOT = 0.01
ifilename = args[1]
ofilename = args[2]
threidx = as.numeric(args[3])
drawpic = 0
if (length(args)>3){
    drawpic = as.numeric(args[4])
}

suppressMessages(library("MonoPoly"))
data = read.csv(ifilename,sep="\t",header=FALSE)
data = subset(data,V1 <= threidx & V2 != NANSYMBOL)
if (nrow(data) <= 1){
    q()
}
data[nrow(data),ncol(data)] = 0.0
#result = tryCatch({
#    model = monpol(V2~V1,data,degree=10,weights=data$V3,a=0,b=1 / HPVALUESLOT,monotone="decreasing",trace=TRUE)
#},
#error=function(cond) {
#            message("Here's the original error message:")
#            message(cond)
#            print(args)
#        })
print("stuck")
model = monpol(V2~V1,data,degree=10,weights=data$V3,a=0,b=1 / HPVALUESLOT,monotone="decreasing")
print("over")
para = coef(model)
print("where")

fullx = seq(0,1 / HPVALUESLOT,by=1)
fitteddata = evalPol(fullx,para)
fittedcurve = data.frame(x=fullx,y=fitteddata)
realvaluepart = subset(fittedcurve,x <= threidx)
realy = realvaluepart$y
filly = rep(0, length(fullx) - length(realy))
fully = c(realy,filly)

nr = 1
nc = length(fully) / nr

wdata <- matrix(c(nc,fully), nr, nc+1)
write.table(wdata, ofilename, row.names = FALSE, col.names=FALSE, sep = "\t", append = TRUE)

if (drawpic == 1){
    png(filename=args[5])
    plot(V2~V1,data)
    lines(y~x,fittedcurve,col="red")
    suppressoutput = dev.off()
}

# Rscript /home/zoul15/pokerweb/polyfoldrate.R /home/zoul15/pcshareddir/gnudata/fulltestdata.csv "/home/zoul15/testopt" 40 1 "/home/zoul15/pcshareddir/gnuresult/polyfoldrate.png"
# Rscript /home/zoul15/pokerweb/polyfoldrate.R /home/zoul15/pcshareddir/gnudata/fulltestdata.csv "/home/zoul15/testopt" 40