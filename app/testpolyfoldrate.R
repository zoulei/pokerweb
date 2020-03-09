args = commandArgs(trailingOnly=TRUE)

NANSYMBOL = -10000.0
HPVALUESLOT = 0.01
ifilename = "/home/zoul15/pcshareddir/gnudata/fulltestdata.csv"
ofilename = "/home/zoul15/testopt"
threidx = 40
cmpfname = "/home/zoul15/pcshareddir/gnudata/folddata.csv"
drawpic = 1

cmpdata = read.csv(cmpfname,sep="\t",header=FALSE)
cmpdata = subset(cmpdata,V1 <= threidx)

#install.packages("/home/zoul15/pcshareddir/MonoPoly", repos = NULL, type = "source")
suppressMessages(library("MonoPoly"))
data = read.csv(ifilename,sep="\t",header=FALSE)
data = subset(data,V1 <= threidx & V2 != NANSYMBOL)
data[nrow(data),ncol(data)] = 0.0


model = monpol(V2~V1,data,degree=5,weights=data$V3,a=0,b=1 / HPVALUESLOT,monotone="decreasing")
#coef(model,scale="fitted")
para = coef(model)
#para

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
    png("/home/zoul15/pcshareddir/gnuresult/testpolyfoldrate.png")
    plot(V2~V1,data)
    lines(y~x,realvaluepart,col="red")
    lines(V2~V1,cmpdata,col="green")
    suppressoutput = dev.off()
}