from smc import *
from plotResults import *
from sciPlots import *
import pickle

# normalized variance parameter
sigma = 0.00174; ess = 1.0
obsWeights = [1,1,0.02]
yadeFile = 'mcTriax_e.py'
yadeDataDir = 'iterPFNew3'
obsDataFile = 'obsdata.dat'
obsCtrl = 'e_a'

# ranges of parameters (E, \mu, kr, \mu_r)
paramNames = ['E', 'mu', 'k_r','mu_r']
paramRanges = {'E':[100e9,200e9],'mu':[0.3,0.5],'k_r':[0,1e4],'mu_r':[0.1,0.5]}
numSamples = 100; maxNumComponents = int(numSamples/10); priorWeight = 1e-2
iterNO = int(yadeDataDir[-1])
sampleDataFile = 'smcTableNew%i.txt'%iterNO
proposalFile = 'gmm_'+yadeDataDir[:-1]+'%i.pkl'%(iterNO-1) if iterNO != 0 else ''
reverse = True if iterNO%2==1 else False

sigAndESS = []; numSig = 500
for i in range(numSig):
	# initialize the problem
	smcTest = smc(sigma,obsWeights,yadeFile,yadeDataDir,obsDataFile,obsCtrl)
	smcTest.initialize(paramNames,paramRanges,numSamples,maxNumComponents,priorWeight,sampleDataFile=sampleDataFile,loadSamples=True,proposalFile=proposalFile)
	# run sequential Monte Carlo; return means and coefficients of variance of PDF over the parameters
	ips, covs = smcTest.run(skipDEM=True,reverse=reverse)
	# get the parameter samples (ensemble) and posterior probability
	posterior = smcTest.getPosterior()
	smcSamples = smcTest.getSmcSamples()
	# calculate effective sample size
	ess = smcTest.getEffectiveSampleSize()[-1]
	print 'Effective sample size: %f'%ess
	sigAndESS.append([sigma,ess])
	sigma *= 0.99

# define appropriate sigma
plotSigAndESS(sigAndESS)
if iterNO == 0: sigma, ESS = sigAndESS[np.argmax(np.array(sigAndESS)[:,1])]
else: sigma, ESS = sigAndESS[np.argmin(abs(np.array(sigAndESS)[:,1]-0.2)**2)]

# initialize the problem
smcTest = smc(sigma,obsWeights,yadeFile,yadeDataDir,obsDataFile,obsCtrl)
smcTest.initialize(paramNames,paramRanges,numSamples,maxNumComponents,priorWeight,sampleDataFile=sampleDataFile,loadSamples=True,proposalFile=proposalFile)
# run sequential Monte Carlo; return means and coefficients of variance of PDF over the parameters
ips, covs = smcTest.run(skipDEM=True,reverse=reverse)
# get the parameter samples (ensemble) and posterior probability
posterior = smcTest.getPosterior()
smcSamples = smcTest.getSmcSamples()
# calculate effective sample size
ess = smcTest.getEffectiveSampleSize()[-1]
print 'Effective sample size: %f'%ess

# plot time evolution of effective sample size
plt.figure();plt.plot(smcTest.getEffectiveSampleSize());
plt.figure();plt.plot(smcTest.getSmcSamples()[0][:,0],smcTest._proposal,'o',label='proposal'); plt.show()

# plot means of PDF over the parameters
microParamUQ = plotIPs(paramNames,ips[:,::(-1)**reverse].T,covs[:,::(-1)**reverse].T,smcTest.getNumSteps(),posterior,smcSamples[0])

# resample parameters
caliStep = -1
gmm, maxNumComponents = smcTest.resampleParams(caliStep=caliStep)

# plot initial and resampled parameters
plotAllSamples(smcTest.getSmcSamples(),smcTest.getNames())

# save trained Gaussian mixture model
pickle.dump(gmm, open('gmm_'+yadeDataDir+'.pkl', 'wb'))

m = smcTest.getNumSteps(); n = smcTest._numSamples
weights = smcTest.getPosterior()*np.repeat(smcTest._proposal,m).reshape(n,m)
weights /= sum(weights)

plt.figure()
for i in (-weights[:,caliStep]).argsort()[:10]:
	plt.plot(smcTest._obsCtrlData,smcTest._yadeData[:,i,0].T/smcTest._yadeData[:,i,1].T,'-',label=', '.join([paramNames[j]+': '+'%g'%smcSamples[0][i,j] for j in range(len(paramNames))]))
plt.plot(smcTest._obsCtrlData,smcTest._obsData[:,0].T/smcTest._obsData[:,1].T,'ko-',label='Test')
means = np.sum(smcTest._yadeData.T*weights,1)
plt.plot(smcTest._obsCtrlData,means[0,:]/means[1,:],'b^-',label='Mean')
plt.legend();plt.tight_layout();

plt.figure()
for i in (-weights[:,caliStep]).argsort()[:10]:
	plt.plot(smcTest._obsCtrlData,smcTest._yadeData[:,i,2].T,'-',label=', '.join([paramNames[j]+': '+'%g'%smcSamples[0][i,j] for j in range(len(paramNames))]))
plt.plot(smcTest._obsCtrlData,smcTest._obsData[:,2].T,'ko-',label='Test')
plt.plot(smcTest._obsCtrlData,means[2,:],'b^-',label='Mean')
plt.legend();plt.tight_layout(); plt.show()

mcFiles = glob.glob(yadeDataDir+'/*txt'); mcFiles.sort()
goodFiles = []; EValues = []; muValues = []; krValues = []; mu_rValues = []
for i in (-weights[:,caliStep]).argsort()[:3]:
	goodFiles.append(mcFiles[i]); 
	EValues.append(smcSamples[0][i,0]); muValues.append(smcSamples[0][i,1])
	krValues.append(smcSamples[0][i,2]); mu_rValues.append(smcSamples[0][i,3])
keysAndData, obsCtrlData, _, _ = smcTest.getObsDataFromFile(obsDataFile,obsCtrl)
macroParamUQ = plotExpAndNum('VAE3',paramNames,'%i'%iterNO,smcTest.getPosterior()[:,::(-1)**reverse],mcFiles,goodFiles,\
	EValues,muValues,krValues,mu_rValues,\
	keysAndData['p'],keysAndData['q'],keysAndData['n'],obsCtrlData*100,np.zeros(smcTest.getNumSteps()))
