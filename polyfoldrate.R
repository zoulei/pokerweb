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

#install.packages("/home/zoul15/pcshareddir/MonoPoly", repos = NULL, type = "source")
suppressMessages(library("MonoPoly"))
data = read.csv(ifilename,sep="\t",header=FALSE)
# below three line make sure the algorithm work success
data[1,2] = 1
data[threidx+1,2] = 0
data[threidx+1,3] = 0
data = subset(data,V1 <= threidx & V2 != NANSYMBOL)

if (nrow(data) <= 2){
    # print ("error, no valid data.\n")
    # print(args)
    # print("-------")
    fullx = seq(0,1 / HPVALUESLOT,by=1)
    fully = rep(0, length(fullx))
    fully[1] = 1
    nr = 1
    nc = length(fully) / nr
    wdata <- matrix(c(nc,fully), nr, nc+1)
    write.table(wdata, ofilename, row.names = FALSE, col.names=FALSE, sep = "\t", append = FALSE)
    q()
}
# data[nrow(data),ncol(data)] = 0.0
# data[nrow(data),2] = 0.0
# data
result = tryCatch({
   model = monpol(V2~V1,data,degree=10,weights=data$V3,a=0,b=1 / HPVALUESLOT,monotone="decreasing")
},
error=function(cond) {
           message("Here's the original error message:")
           message(cond)
           print(args)
        print(data)
    print("=========")
})
model = monpol(V2~V1,data,degree=10,weights=data$V3,a=0,b=1 / HPVALUESLOT,monotone="decreasing")
para = coef(model)

fullx = seq(0,1 / HPVALUESLOT,by=1)
fitteddata = evalPol(fullx,para)
fitteddata[fitteddata < 0] <- 0
fittedcurve = data.frame(x=fullx,y=fitteddata)
realvaluepart = subset(fittedcurve,x < threidx)
realy = realvaluepart$y
filly = rep(0, length(fullx) - length(realy))
fully = c(realy,filly)

nr = 1
nc = length(fully) / nr

wdata <- matrix(c(nc,fully), nr, nc+1)
write.table(wdata, ofilename, row.names = FALSE, col.names=FALSE, sep = "\t", append = FALSE)

if (drawpic == 1){
    png(filename=args[5])
    plot(V2~V1,data)
    lines(y~x,fittedcurve,col="red")
    suppressoutput = dev.off()
}

# Rscript /home/zoul15/pokerweb/polyfoldrate.R /home/zoul15/pcshareddir/gnudata/fulltestdata.csv "/home/zoul15/testopt" 40 1 "/home/zoul15/pcshareddir/gnuresult/polyfoldrate.png"
# Rscript /home/zoul15/pokerweb/polyfoldrate.R /home/zoul15/pcshareddir/gnudata/fulltestdata.csv "/home/zoul15/testopt" 40